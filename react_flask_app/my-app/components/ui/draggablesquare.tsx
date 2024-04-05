"use client";

import { useId } from 'react';
import {FC} from "react";
import {useDraggable} from "@dnd-kit/core"
import React, { CSSProperties } from "react";
import { CSS } from "@dnd-kit/utilities";




export interface DraggableSquareProps {
  name: string;
  xpos: number; 
  ypos: number; 
  classType: string;
  tailwindClassName: string; // Make otherstyles optional
  id: string 
};

const DraggableSquare: React.FC<DraggableSquareProps> = ({ name, xpos, ypos, classType, tailwindClassName }) => {
  const id = useId(); 
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: id,
    data: { id: id, name: name, classType: classType, tailwindClassName: tailwindClassName },

  });


 

  const style: CSSProperties | undefined = isDragging
    ? {
        position: "absolute",
        transform: `translate3d(${transform?.x}px, ${transform?.y}px, 0)`,
        cursor: "move", 

      }
    : {
        position: "relative",
        cursor: "pointer",
        left: `${xpos}px`,
        top: `${ypos}px`,

      };
  
  const mystyle = 
  {
    position: "relative",
    left: `${xpos}px`,
    top: `${ypos}px`
  }; 
      
 
  return (
    <>
      <div
        id={id}
        ref={setNodeRef}
        {...attributes}
        {...listeners}
        className={tailwindClassName}
        style={{ ...style, ...mystyle}}
      
      >
        {name}
      </div>
      {isDragging && <div className={tailwindClassName} style={{ display: "none !important" }}>{name}</div>}
    </>
  );
};

export default DraggableSquare;


