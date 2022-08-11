/* eslint-disable */
import React, { useEffect, useRef, useState } from "react";
import autoAnimate from "@formkit/auto-animate";
import { Typography } from "antd";
import S from "./styles";

const { Title } = Typography;

const Collapsible = ({
  initiallyCollapsed,
  title,
  children,
  headerStyle = {},
}) => {
  const [isCollapsed, setIsCollapsed] = useState(initiallyCollapsed);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const parent = useRef(null);

  useEffect(() => parent.current && autoAnimate(parent.current), [parent]);

  return (
    <div ref={parent}>
      <S.CollapsibleHeader onClick={toggleCollapse} style={headerStyle}>
        <S.CollapseButton collapsed={isCollapsed} />
        {(typeof title === "string")
          ? (
            <Title level={3} className="text">
              {title}
            </Title>
          ) : (
            title
          )}
      </S.CollapsibleHeader>
      {
        (isCollapsed) ? (
          <S.CollapsibleContent collapsed={isCollapsed}>
            {children}
          </S.CollapsibleContent>
        ) : null
      }
    </div>
  );
};

export default Collapsible;
