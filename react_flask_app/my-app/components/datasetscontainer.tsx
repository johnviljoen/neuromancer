import React from 'react';
import DraggableSquare from '@/components/ui/draggablesquare';

interface DatasetsContainerProps {
  dataMap: Map<string, any>;
}

const DatasetsContainer: React.FC<DatasetsContainerProps> = ({ dataMap }) => {
  const tailwindClassName = "w-12 h-12 bg-blue-500 m-2 flex items-center justify-center rounded";
  return (
    <div id="datasets-container" className="flex flex-col justify-center items-center h-full">
      <h2 className="text-lg font-semibold text-black">Datasets Container</h2>
      {/* Display draggable squares for each dataset */}
      {[...dataMap.keys()].map(id => (
        <DraggableSquare name={id} xpos={0} ypos={0} tailwindClassName={tailwindClassName} />
      ))}
    </div>
  );
}

export default DatasetsContainer;