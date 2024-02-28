// Components.tsx
"use client"; // top to the file
import React from 'react';
import {DndContext} from "@dnd-kit/core"
import DraggableSquare from '@/components/ui/draggablesquare';
import { useId } from 'react';

const BlocksContainer: React.FC = () => {

  return (
    <DndContext>
      <div className="flex items-center justify-center w-1/4 h-full bg-gray-200 dark:bg-gray-700 rounded-l-lg">
        <h2 className="text-lg font-semibold text-black">BlocksContainer</h2>
        <div className="Neuromancer_Components_Container">
          <DraggableSquare name="MLP" />
          <DraggableSquare name="ResNet" />
          <DraggableSquare name="Linear" />
        </div>
      </div>
    </DndContext>
  );
  
}

export default BlocksContainer;
