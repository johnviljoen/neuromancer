"use client";

import { useId } from 'react';
import Draggable from 'react-draggable';
import React from 'react';

const DraggableSquare = ({ name, onDrop }) => {
  const id = useId();

  const handleStop = (event, { node }) => {
    // Get the ID and name of the dropped square
    const squareId = node.getAttribute('id');
    const squareName = name;

    // Call the onDrop callback with ID and name
    onDrop(squareId, squareName);
  };

  return (
    <Draggable onStop={handleStop}>
      <div id={id} className="w-12 h-12 bg-blue-500 m-2 flex items-center justify-center rounded">
        {name}
      </div>
    </Draggable>
  );
};

export default DraggableSquare;