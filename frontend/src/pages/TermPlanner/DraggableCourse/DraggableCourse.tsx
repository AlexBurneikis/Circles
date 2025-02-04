import React from 'react';
import { Draggable } from 'react-beautiful-dnd';
import { useContextMenu } from 'react-contexify';
import { useSelector } from 'react-redux';
import ReactTooltip from 'react-tooltip';
import { InfoCircleOutlined, WarningOutlined } from '@ant-design/icons';
import { Typography } from 'antd';
import { useTheme } from 'styled-components';
import Marks from 'components/Marks';
import type { RootState } from 'config/store';
import useMediaQuery from 'hooks/useMediaQuery';
import ContextMenu from '../ContextMenu';
import S from './styles';

type Props = {
  code: string
  index: number
  term: string
};

const DraggableCourse = ({ code, index, term }: Props) => {
  const {
    courses,
    isSummerEnabled,
    completedTerms,
  } = useSelector((state: RootState) => state.planner);
  const { showMarks } = useSelector((state: RootState) => state.settings);
  const theme = useTheme();
  const Text = Typography;

  // prereqs are populated in CourseDescription.jsx via course.raw_requirements
  const {
    prereqs, title, isUnlocked, plannedFor,
    isLegacy, isAccurate, termsOffered, handbookNote, supressed, mark,
  } = courses[code];
  const warningMessage = courses[code].warnings;
  const isOffered = plannedFor && /T[0-3]/.test(plannedFor) ? (termsOffered as string[]).includes(plannedFor.match(/T[0-3]/)?.[0] as string) : true;
  const BEwarnings = handbookNote !== '' || !!warningMessage.length;

  const contextMenu = useContextMenu({
    id: `${code}-context`,
  });

  const isDragDisabled = !!plannedFor && !!completedTerms[plannedFor];

  const isSmall = useMediaQuery('(max-width: 1400px)');
  const shouldHaveWarning = !supressed && (
    isLegacy || !isUnlocked || BEwarnings || !isAccurate || !isOffered
  );
  const errorIsInformational = shouldHaveWarning && isUnlocked
    && warningMessage.length === 0 && !isLegacy && isAccurate && isOffered;

  const handleContextMenu = (e: React.MouseEvent) => {
    if (!isDragDisabled) contextMenu.show(e);
  };

  return (
    <>
      <Draggable
        isDragDisabled={isDragDisabled}
        draggableId={`${code}${term}`}
        index={index}
      >
        {(provided) => (
          <S.CourseWrapper
            summerEnabled={isSummerEnabled}
            isSmall={isSmall}
            dragDisabled={isDragDisabled}
            warningsDisabled={isDragDisabled && !isUnlocked}
            isWarning={!supressed && (!isUnlocked || !isOffered)}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            ref={provided.innerRef}
            style={provided.draggableProps.style}
            data-tip
            data-for={code}
            id={code}
            onContextMenu={handleContextMenu}
          >
            {!isDragDisabled && shouldHaveWarning
              && (errorIsInformational ? (
                <InfoCircleOutlined
                  style={{ color: theme.infoOutlined.color }}
                />
              ) : (
                <WarningOutlined
                  style={{ fontSize: '16px', color: theme.warningOutlined.color }}
                />
              ))}
            <S.CourseLabel>
              {isSmall ? (
                <Text className="text">{code}</Text>
              ) : (
                <div>
                  <Text className="text">
                    <strong>{code}: </strong>
                    {title}
                  </Text>
                </div>
              )}
              {showMarks && <Marks mark={mark} />}
            </S.CourseLabel>
          </S.CourseWrapper>
        )}
      </Draggable>
      <ContextMenu code={code} plannedFor={plannedFor} />
      {/* display prereq tooltip for all courses. However, if a term is marked as complete
        and the course has no warning, then disable the tooltip */}
      {isSmall && (
        <ReactTooltip id={code} place="top" effect="solid">
          {title}
        </ReactTooltip>
      )}
      {!isDragDisabled && shouldHaveWarning && (
        <ReactTooltip id={code} place="bottom">
          {isLegacy ? 'This course is discontinued. If an equivalent course is currently being offered, please pick that instead.'
            : !isUnlocked ? prereqs.trim()
              : !isOffered ? 'The course is not offered in this term.'
                : warningMessage.length !== 0 ? warningMessage.join('\n')
                  // eslint-disable-next-line react/no-danger
                  : <div dangerouslySetInnerHTML={{ __html: handbookNote }} />}
          {!isAccurate ? ' The course info may be inaccurate.' : ''}
        </ReactTooltip>
      )}
    </>
  );
};

export default DraggableCourse;
