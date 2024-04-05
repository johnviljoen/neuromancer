"use client";

/**
 * This code was generated by v0 by Vercel.
 * @see https://v0.dev/t/ljMRW8ysNr6
 */

import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { DropdownMenuTrigger, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuRadioItem, DropdownMenuRadioGroup, DropdownMenuContent, DropdownMenu } from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import DatasetsContainer  from "@/components/datasetscontainer"
import { Link } from 'react-router-dom';
import { useId } from 'react';

import {
  XYPlot,
  XAxis,
  YAxis,
  HorizontalGridLines,
  VerticalGridLines,
  LineSeries,
} from "react-vis";

type BlockInfo = {
  id: string;
  name: string;
  x: number;
  y: number;
  tailwindClassName: string;
};

type DatasetCreatorProps = {
  canvasMap: Map<string, BlockInfo>;
  addDatasetToCanvasMap: (newCanvasMap: Map<string, BlockInfo>) => void;
};


export const DatasetCreator: React.FC<DatasetCreatorProps> = ({ canvasMap, addDatasetToCanvasMap }) => {

  const [system, setSystem] = useState("VanDerPol");
  const [numSimulations, setNumSimulations] = useState("500");
  const [plotData, setPlotData] = useState([]);
  const [currentChartData, setCurrentChartData] = useState([]);
  const [dataMap, setDataMap] = useState(new Map()); // State to hold the map of data sets

  

  const generateUniqueId = () => {
    // Function to generate a unique ID for the new dataset
    return `dataset_${Math.random().toString(36).substr(2, 9)}`;
  };

  const fetchData = () => {
    const id = generateUniqueId();
    const sendDataParams = {
      id: id, 
      system: system,
      numSimulations: numSimulations,
    };
    console.log(sendDataParams);
    fetch("http://localhost:5000/plot-system", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(sendDataParams)
    })
    .then((res) => {
      if (!res.ok) {
        throw new Error('Failed to fetch data');
      }
      return res.json();
    })
    .then((data) => {
      
      console.log("DATA");
      console.log(data);
      setDataMap(new Map(dataMap.set(id, data)));
      //console.log("chart data is", data['Y_data'].Y);
      const dataArray = data['Y_data'].Y;
      setCurrentChartData(dataArray.map(([x, y]) => ({ x, y })));
      

      
      const newBlockInfo: BlockInfo = {
        id: id, 
        name: system,
        classType: "neuromancer_dataset",
        x: 0,
        y: 0,
        tailwindClassName: "w-12 h-12 bg-blue-500 m-2 flex items-center justify-center rounded",
      };

      // Create a copy of the existing canvasMap
      const newCanvasMap = new Map(canvasMap);
      // Add the new dataset to canvasMap
      newCanvasMap.set(id, newBlockInfo);

      // Call the callback function to update canvasMap in the Root component
      addDatasetToCanvasMap(newCanvasMap);








    })
    .catch(error => {
      console.error('Error fetching data:', error);
    });
  };

  console.log("CANVAS MAP ");
  console.log(canvasMap);
  const plotSystemData = (Y) => {
    
    console.log("FOO")


    return (
      <XYPlot width={400} height={400}>
        <HorizontalGridLines />
        <VerticalGridLines />
        <XAxis title="X Axis" />
        <YAxis title="Y Axis" />
        <LineSeries data={Y} strokeWidth={0.1}/>
      </XYPlot>
    );
  
  };


  const handleSystemChange = (event) => {
    console.log("Drop down change");
    console.log(event)
    console.log(event.target.value)
    setSystem(event.target.value);
  };

  const handleNumSimulationsChange = (event) => {
    const value = parseInt(event.target.value); // Convert input value to integer
    if (!isNaN(value)) {
      setNumSimulations(value); // Set numSimulations state only if input is a valid integer
    }
  };

  console.log(numSimulations);

  return (
    <div className="grid gap-4">
      <div className="flex items-center gap-4">
        {/* Dropdown menu for selecting system */}
        <select value={system} onChange={handleSystemChange}>
          <option value="VanDerPol">VanDerPol</option>
          <option value="LorenzSystem">LorenzSystem</option>
          <option value="Pendulum">Pendulum</option>
          <option value="DoublePendulum">DoublePendulum</option>
          <option value="LotkaVolterra">LotkaVolterra</option>
        </select>
        {/* Input field for number of simulations */}
        <Input className="w-[200px]" placeholder="Enter number of simulations" value={numSimulations} onChange={handleNumSimulationsChange} />
        <Button className="h-9" onClick={fetchData}>Generate System Data</Button>
      </div>
      <div style={{ width: '800px', height: '800px' }}>
        {currentChartData.length > 0 && plotSystemData(currentChartData)}
      </div>
      {/* Render DatasetsContainer component with dataMap */}
      <DatasetsContainer dataMap={dataMap} />
      <Link to="/">Go back to Main Screen</Link>
    </div>
  );
}