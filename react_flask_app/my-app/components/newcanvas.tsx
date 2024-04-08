// Canvas.tsx
"use client"; // top to the file
import React,  { useMemo, useCallback, useEffect, useState, useId } from 'react';
import {FC} from "react";
import {useDroppable} from "@dnd-kit/core"

import ReactFlow, { Controls, Background ,useNodesState, useEdgesState, addEdge } from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from "@/components/ui/button";
import {DndContext, DragEndEvent} from "@dnd-kit/core"
import DraggableSquare from '@/components/ui/draggablesquare';
import { ReactFlowProvider } from 'reactflow';

interface CanvasProps {
  canvasMap: Map<string, BlockInfo>; 
};

type ProblemData = {
  canvasMap: Map<string, BlockInfo>; 
  
};

const generateUniqueId = () => {
  // Function to generate a unique ID for the new dataset
  return `dataset_${Math.random().toString(36).substr(2, 9)}`;
};


const Canvas: React.FC<CanvasProps> = ({ canvasMap }) => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [showData, setShowData] = React.useState(false);
    const [sendingCanvasMapData, setSendingCanvasMapData] = useState(false);
    const [problemConstructed, setProblemConstructed] = useState(false); 
    const [draggedItem, setDraggedItem] = useState(null);
    const [reactFlowInstance, setReactFlowInstance] = useState(null);

    const sendDataToBackend = async (data) => {
      try {
 
        const response = await fetch("http://localhost:5000/receive_problem_data", {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          
          
          body: JSON.stringify({ data}),
        });
    
        if (!response.ok) {
          throw new Error('Failed to send data to the backend');
        }
    
        // If your backend returns JSON response, you can parse it like this:
        // const responseData = await response.json();
        // return responseData;
    
        // If your backend does not return anything, you can simply return 'true' to indicate success
        return true;
      } catch (error) {
        throw new Error(error.message);
      }
    };
  
    const handleConstructProblem = () => {
      const problem_id = generateUniqueId();
      setSendingCanvasMapData(true);

      const canvas_map_entries = Array.from(canvasMap.entries()).map(([id, blockInfo]) => ({
        id,
        blockInfo
      }));
      
      const dataToSend = {
        canvas_map_entries: canvas_map_entries,
        nodes: nodes, 
        edges: edges,
        problem_id: problem_id,

      };
      console.log("dataToSend DATA ");
      console.log(dataToSend);
      sendDataToBackend(dataToSend)
      // Assuming you have a function to send data to the backend called sendDataToBackend

        .then(response => {
          // Handle response from the backend if needed
          console.log("Data sent successfully:", response);
          setSendingCanvasMapData(false);
          setProblemConstructed(true); // Update state when problem construction is successful
        })
        .catch(error => {
          // Handle error if the data sending fails
          console.error("Error sending data:", error);
          setSendingCanvasMapData(false);
        });
    };

    const handleTrainProblem = () => {
      const dataToSend = {
        'foo': 'TRAIN'
      }
      // Send a signal to the Flask backend to trigger the training process
      fetch("http://localhost:5000/train_neuromancer_problem", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ dataToSend}),
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to trigger training');
        }
        // Handle response from the backend if needed
        console.log("Training process triggered successfully");
      })
      .catch(error => {
        // Handle error if the training process fails to trigger
        console.error("Error triggering training:", error);
      });
    };
  
    const onConnect = useCallback(
      (params) => setEdges((eds) => addEdge(params, eds)),
      [setEdges],
    );
  

   
    const { setNodeRef, isOver, over, node } = useDroppable({
      id: "canvas-droppable"
      
    }); 

    

  
    const mappedNodes = useMemo(() => {
      return Array.from(canvasMap.entries()).map(([id, blockInfo], index) => {
        let style = {};
        if (blockInfo.type === 'default') {
          style = { background: '#FFF' };
        } else if (blockInfo.type === 'custom') {
          style = { background: '#FF0000' }; 
        }      
        return {
          id,
          type: 'default',
          style,
          data: { label: blockInfo.name, classType: blockInfo.classType, },
          position: { x: blockInfo.x, y: index * 100 }, // Adjust y position based on index
        };
      });
    }, [canvasMap]);
  
    useEffect(() => {
      // Update the nodes state when mappedNodes changes
      setNodes(mappedNodes);
    }, [mappedNodes, setNodes]);
  
    const nodeTypes = useMemo(() => ({
      default: DraggableSquare,
    }), []);
  
    const handleShowData = () => {
        setShowData(true);
        console.log("Nodes:");
        nodes.forEach(node => {
          const blockInfo = canvasMap.get(node.id);
          if (blockInfo) {
            console.log(`Node ID: ${node.id}, Name: ${blockInfo.name}, X: ${blockInfo.x}, Y: ${blockInfo.y}`);
          }
        });
        console.log("Edges:", edges);
      };
  
      return (
        <div
          className="flex items-center justify-center w-3/4 h-full bg-gray-50 dark:bg-gray-800 rounded-r-lg"
          ref={setNodeRef}
        >
          <div style={{ width: '100vw', height: '80vh' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
            />
            <Button className="h-9" onClick={handleConstructProblem} disabled={sendingCanvasMapData}>
              Create Neuromancer Problem
            </Button>
            <Button className="h-9 ml-2" onClick={handleTrainProblem} disabled={!problemConstructed}>
              Train Neuromancer Problem
            </Button>
          </div>
        </div>
      );
  };
  
  export default Canvas;