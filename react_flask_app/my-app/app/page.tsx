/**
 * v0 by Vercel.
 * @see https://v0.dev/t/KXbYVG69jUt
 * Documentation: https://v0.dev/docs#integrating-generated-code-into-your-nextjs-app
 */

"use client"; // top to the file

import React, { useState } from 'react';
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ReactFlowProvider } from 'reactflow';
import { DropdownMenuTrigger, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuItem, DropdownMenuContent, DropdownMenu } from "@/components/ui/dropdown-menu"
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Main } from "@/components/main";
import { DatasetCreator } from "@/components/datasetcreator"
import {DndContext, DragEndEvent} from "@dnd-kit/core"
import ReactFlow, {
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
} from 'reactflow';




 type BlockInfo = {
  id: string;
  name: string;
  x: number;
  y: number;
  classType: string;
  tailwindClassName: string;
};



export default function App() {
  const [datasets, setDatasets] = useState([]);
  const [canvasMap, setCanvasMap] = useState<Map<string, BlockInfo>>(new Map());
  const [draggedItem, setDraggedItem] = useState<BlockInfo | null>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);


  const updateCanvasMap = (newCanvasMap: Map<string, BlockInfo>) => {
    setCanvasMap(newCanvasMap);
  };


  const fooGetBlockInformation = (e: DragEndEvent) => {
    const id = e.active.id;
    const classType = e.active.data.current.classType.toLowerCase();
    const tailwindClassName = e.active.data.current.tailwindClassName;
    
    const delta_x = e.delta.x;
    const delta_y = e.delta.y;
    
  
    // Update the canvas map
    setCanvasMap((prevCanvasMap) => {
      const updatedCanvasMap = new Map(prevCanvasMap);
      const existingBlockInfo = updatedCanvasMap.get(id);
  
      if (existingBlockInfo) {
        // If the block info exists, update its x and y
        existingBlockInfo.x += delta_x;
        existingBlockInfo.y += delta_y;
        setDraggedItem(existingBlockInfo);
      } else {
        // If the block info doesn't exist, create a new one
        const name = e.active.data.current.name.toLowerCase();
        const newBlockInfo: BlockInfo = {
          id,
          name,
          classType,
          delta_x,
          delta_y,
          tailwindClassName: tailwindClassName
        };
        updatedCanvasMap.set(id, newBlockInfo);
        setDraggedItem(newBlockInfo);
      }
      return updatedCanvasMap;
    });
  };
  

  return (
    
    <Router>
          <Routes>
            <Route path="/" element={<Main canvasMap={canvasMap} getBlockInformation={fooGetBlockInformation} draggedItem={draggedItem}/>} />
            <Route
              path="/dataset-creator"
              element={<DatasetCreator canvasMap={canvasMap} addDatasetToCanvasMap={updateCanvasMap} />}
            />
        
          </Routes>
    </Router>
    
  );
}


function BellIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
    </svg>
  )
}


function Package2Icon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z" />
      <path d="m3 9 2.45-4.9A2 2 0 0 1 7.24 3h9.52a2 2 0 0 1 1.8 1.1L21 9" />
      <path d="M12 3v6" />
    </svg>
  )
}
