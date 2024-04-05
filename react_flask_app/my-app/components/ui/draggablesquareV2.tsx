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

    const onDragStart = (event) => {
        event.dataTransfer.setData('application/reactflow', id);
        console.log("IN ON DRAG START");
        event.dataTransfer.effectAllowed = 'move';
    };
    const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
        id: id,
        data: { id: id, name: name, classType: classType, tailwindClassName: tailwindClassName },

    });



    return (
        <>
            <div
                className={tailwindClassName}
                {...attributes}
                {...listeners}
                ref={setNodeRef}
                onDragStart={onDragStart} // Use handleDragStart instead of onDragStart directly
                draggable
            >
                {name}
            </div>
            {isDragging && <div className={tailwindClassName} style={{ display: "none !important" }}>{name}</div>}
        </>
    );
};

export default DraggableSquare;


