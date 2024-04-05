// TrashCan.js
import React from 'react';

const TrashCan = ({ onDrop }) => {
    const trashCanViewBox = { x: 0, y: 0, width: 32, height: 32 }; // Increase width and height of viewBox
  
    const handleDropOnTrashCan = (event) => {
      event.preventDefault();
  
      const squareId = event.dataTransfer.getData('squareId');
      const squareName = event.dataTransfer.getData('squareName');
  
      // Trigger onDrop function with square's ID and name
      onDrop(squareId, squareName);
    };
  
    const isInTrashCanArea = (x, y) => {
      return (
        x >= trashCanViewBox.x &&
        x <= trashCanViewBox.x + trashCanViewBox.width &&
        y >= trashCanViewBox.y &&
        y <= trashCanViewBox.y + trashCanViewBox.height
      );
    };
  
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="32"
        height="32"
        viewBox={`${trashCanViewBox.x} ${trashCanViewBox.y} ${trashCanViewBox.width} ${trashCanViewBox.height}`}
        fill="currentColor"
        className="bi bi-trash"
        onDrop={handleDropOnTrashCan}
        onDragOver={(event) => event.preventDefault()}
      >
        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z" />
        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z" />
      </svg>
    );
  };
  
  export default TrashCan;