// Canvas.tsx
"use client"; // top to the file
import React from 'react';
import {FC} from "react";
import {useDroppable} from "@dnd-kit/core"
import ReactFlow, { addEdge } from 'react-flow-renderer';
import {DndContext, DragEndEvent} from "@dnd-kit/core"
import DraggableSquare from '@/components/ui/draggablesquare';


interface CanvasProps {
  canvasMap: Map<string, BlockInfo>; 
};

const Canvas: React.FC<CanvasProps> = ({ canvasMap }) => {


  const { setNodeRef, isOver } = useDroppable({
    id: "canvas-droppable"
  }); 

  const renderElement = () => {

    if (!canvasMap) {return}
    
    const elementsArray = Array.from(canvasMap.entries()); // Convert Map to array of [key, value] pairs
    
    console.log(elementsArray);
    return elementsArray.map(([id, blockInfo]) => (
      <DraggableSquare name={blockInfo.name} xpos={blockInfo.x} ypos={blockInfo.y} tailwindClassName={blockInfo.tailwindClassName}/>
    ));
  };

  

 

  return (
    <div
      className="flex items-center justify-center w-3/4 h-full bg-gray-50 dark:bg-gray-800 rounded-r-lg"
      ref={setNodeRef}
    >
      <h2 className="text-lg font-semibold text-black">Canvas</h2>
      {renderElement()}
    </div>
  ); 
}; 

export default Canvas;