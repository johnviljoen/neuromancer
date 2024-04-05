"use client";

import { useId } from 'react';
import Draggable from 'react-draggable';
import React from 'react';

const DraggableSquare = ({ name }) => {
  const id = useId();

  const handleDragStart = (event) => {
    event.dataTransfer.setData('squareId', id);
    event.dataTransfer.setData('squareName', name);
  };

  return (
    <Draggable onStart={handleDragStart}}>
      <div id={id} className="w-12 h-12 bg-blue-500 m-2 flex items-center justify-center rounded">
        {name}
      </div>
    </Draggable>
  );
};

export default DraggableSquare;