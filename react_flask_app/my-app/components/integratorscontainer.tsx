import React from 'react';
import DraggableSquare from '@/components/ui/draggablesquare';
import IntegratorSquare from '@/components/ui/integratorsquare';

const IntegratorsContainer: React.FC = () => {
  return (
    <div className="flex items-center justify-center w-1/4 h-full bg-gray-200 dark:bg-gray-700 rounded-l-lg">
      <h2 className="text-lg font-semibold text-black">Integrators</h2>
      <div className="Neuromancer_Integrators_Container">
        <IntegratorSquare name="Euler" xpos={0} ypos={0}/>
      </div>
    </div>
  );
};

export default IntegratorsContainer;