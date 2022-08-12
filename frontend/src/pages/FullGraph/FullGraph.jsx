import { useEffect, useRef, useState } from "react";
import G6, { Algorithm } from "@antv/g6";
import axios from "axios";
import GRAPH_STYLE from "../GraphicalSelector/config";

const FullGraph = () => {
  const ref = useRef(null);

  const [graph, setGraph] = useState(null);

  const initialiseGraph = (courses, courseEdges) => {
    const container = ref.current;
    const graphInstance = new G6.Graph({
      container,
      width: container.scrollWidth,
      height: container.scrollHeight,
      linkCenter: true,
      modes: {
        default: [
          "drag-canvas",
          "zoom-canvas",
          // "drag-node",
        ],
      },
      layout: {
        type: "comboCombined",
        preventOverlap: true,
        nodeSpacing: 10,
        linkDistance: 500,
      }H_STYLE.defaultEdge,
      nodeStateStyles: GRAPH_STYLE.nodeStateStyles,
    });

    setGraph(graphInstance);

    const data = {
      nodes: courses.map((c) => handleNodeData(c, plannedCourses)),
      edges: courseEdges,
    };

    graphInstance.data(data);
    graphInstance.render();

    graphInstance.on("node:click", async (ev) => {
      // load up course information
      const node = ev.item;
      const { _cfg: { id } } = node;
      const [courseData, err] = await axiosRequest("get", `/courses/getCourse/${id}`);
      if (!err) setCourse(courseData);

      // hides/ unhides dependent nodes
      const { breadthFirstSearch } = Algorithm;
      if (node.hasState("click")) {
        graphInstance.clearItemStates(node, "click");
        breadthFirstSearch(data, id, {
          enter: ({ current }) => {
            if (id !== current) {
              const currentNode = graphInstance.findById(current);
              // Unhiding node won't unhide other hidden nodes
              currentNode.getEdges().forEach((e) => e.show());
              currentNode.show();
            }
          },
        });
      } else if (node.getOutEdges().length) {
        graphInstance.setItemState(node, "click", true);
        breadthFirstSearch(data, id, {
          enter: ({ current }) => {
            if (id !== current) {
              const currentNode = graphInstance.findById(current);
              currentNode.getEdges().forEach((e) => e.hide());
              currentNode.hide();
            }
          },
        });
      }
    });

    graphInstance.on("node:mouseenter", async (ev) => {
      const node = ev.item;
      graphInstance.setItemState(node, "hover", true);
    });

    graphInstance.on("node:mouseleave", async (ev) => {
      const node = ev.item;
      graphInstance.clearItemStates(node, "hover");
    });
  };

  const setupGraph = async () => {
    const { data } = await axios.get("/programs/full_graph");
    const { edges, courses } = data;

    if (courses.length !== 0 && edges.length !== 0) initialiseGraph(courses, edges);
  };

  useEffect(() => setupGraph(), []);
};

export default FullGraph;
