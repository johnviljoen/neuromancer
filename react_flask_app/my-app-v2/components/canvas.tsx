// Canvas.tsx
import React from 'react';
import {FC} from "react";
import {useDroppable} from "@dnd-kit/core"



interface CanvasProps {
  setCanvasMap: React.Dispatch<React.SetStateAction<Map<string, string>>>;
}

const Canvas: React.FC<CanvasProps> = ({ setCanvasMap }) => {
  const { setNodeRef } = useDroppable({
    id: "canvas-droppable"
  }); 

  return (
    <div
      className="flex items-center justify-center w-3/4 h-full bg-gray-50 dark:bg-gray-800 rounded-r-lg"
      ref={setNodeRef}
    >
      <h2 className="text-lg font-semibold text-black">Canvas</h2>
    </div>
  ); 
}; 

export default Canvas;