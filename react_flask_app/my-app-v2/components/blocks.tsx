// Components.tsx
import React from 'react';
import DraggableSquare from '@/components/ui/draggablesquare';

class BlocksContainer extends React.Component {
  render() {
    return (
      <div className="flex items-center justify-center w-1/4 h-full bg-gray-200 dark:bg-gray-700 rounded-l-lg">
        <h2 className="text-lg font-semibold text-black">BlocksContainer</h2>
        <div className="Neuromancer_Components_Container">
          <DraggableSquare name="MLP" />
          <DraggableSquare name="ResNet" />
          <DraggableSquare name="Linear" />
        </div>
      </div>
    );
  }
}

export default BlocksContainer;
