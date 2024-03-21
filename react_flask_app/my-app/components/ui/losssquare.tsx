"use client";

import { useId } from 'react';
import {FC} from "react";
import {useDraggable, useDroppable } from "@dnd-kit/core"
import React, { CSSProperties } from "react";
import { CSS } from "@dnd-kit/utilities";

import DraggableSquare, { DraggableSquareProps } from './draggablesquare'; // Assuming DraggableSquare is exported as a named export

interface LossSquareProps extends DraggableSquareProps {
  
}

const LossSquare: React.FC<LossSquareProps> = ({ name, xpos, ypos, classType, ...props }) => {
  const { attributes, listeners, setNodeRef } = useDroppable({
    id: 'loss-square', // Unique ID for the droppable
    data: { props }, // Pass props as data
    onDrop: (event) => {
      const droppedId = event.active.id; // Get the ID of the dropped item
      console.log("Dropped ID:", droppedId);
    },
  });

  return (
    <div  
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      
    >
      <DraggableSquare
        name={name}
        xpos={xpos}
        ypos={ypos}
        classType={classType}
        tailwindClassName="w-32 h-32 bg-green-500 m-2 flex items-center justify-center rounded" // Apply a class to distinguish IntegratorSquare
        {...props}
      />
    </div>
  );
};

export default LossSquare;