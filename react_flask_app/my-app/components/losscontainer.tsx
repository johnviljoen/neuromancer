import React from 'react';
import DraggableSquare from '@/components/ui/draggablesquare';
import LossSquare from '@/components/ui/losssquare';

const LossContainer: React.FC = () => {
  return (
    <div className="flex items-center justify-center w-1/4 h-full bg-gray-200 dark:bg-gray-700 rounded-l-lg">
      <h2 className="text-lg font-semibold text-black">Losses</h2>
      <div className="Neuromancer_Loss_Container">
        <LossSquare name="Reference Tracking" xpos={0} ypos={0} classType="neuromancer_loss"/>
      </div>
    </div>
  );
};

export default LossContainer;