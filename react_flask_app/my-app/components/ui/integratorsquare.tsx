"use client";

import { useId } from 'react';
import {FC} from "react";
import {useDraggable} from "@dnd-kit/core"
import React, { CSSProperties } from "react";
import { CSS } from "@dnd-kit/utilities";

import DraggableSquare, { DraggableSquareProps } from './draggablesquare'; // Assuming DraggableSquare is exported as a named export

interface IntegratorSquareProps extends DraggableSquareProps {
  // Add any additional props specific to IntegratorSquare
}

const IntegratorSquare: React.FC<IntegratorSquareProps> = ({ name, xpos, ypos, ...props }) => {
  return (
    <DraggableSquare
      name={name}
      xpos={xpos}
      ypos={ypos}
      tailwindClassName="w-32 h-32 bg-orange-500 m-2 flex items-center justify-center rounded" // Apply a class to distinguish IntegratorSquare

    />
  );
};

export default IntegratorSquare;