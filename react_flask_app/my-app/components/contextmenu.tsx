import React, { useState } from 'react';

const ContextMenu = ({ isOpen, onClose, onSubmit, nodeId, position }) => {
  const [selectedLinearMap, setSelectedLinearMap] = useState(''); // State to track the selected linear map
  const [hiddenSize, setHiddenSize] = useState(''); // State to track the hidden size

  const handleLinearMapChange = (e) => {
    setSelectedLinearMap(e.target.value);
  };

  const handleHiddenSizeChange = (e) => {
    setHiddenSize(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(selectedLinearMap, nodeId, hiddenSize); // Pass the selected linear map, node ID, and hidden size
    setSelectedLinearMap('');
    setHiddenSize('');
    onClose();
  };

  const linearMapNames = [
    'l0',
    'linear',
    'nneg',
    'lasso',
    'lstochastic',
    'rstochastic',
    'pf',
    'symmetric',
    'skew_symetric',
    'damp_skew_symmetric',
    'split',
    'stable_split',
    'spectral',
    'softSVD',
    'learnSVD',
    'orthogonal',
    'psd',
    'symplectic',
    'butterfly',
    'schur',
    'identity',
    'gershgorin',
    'bounded_Lp_norm',
    'trivial_nullspace',
    'Power_bound'
  ];

  const linearMapOptions = linearMapNames.map((mapName) => (
    <option key={mapName} value={mapName}>{mapName}</option>
  ));

  return (
    isOpen && (
      <div
        className="absolute bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 p-2 rounded"
        style={{ top: 400, left: 900, width: '80px', height: '200px' }}
      >
        <form onSubmit={handleSubmit}>
          <div className="mb-2">
            <label htmlFor="linearMap" className="block text-sm font-medium text-gray-900 dark:text-gray-100">Linear Map:</label>
            <select id="linearMap" value={selectedLinearMap} onChange={handleLinearMapChange} className="mt-1 block w-full rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
              <option value="">Select a linear map</option>
              {linearMapOptions}
            </select>
          </div>
          <div className="mb-2">
            <label htmlFor="hiddenSize" className="block text-sm font-medium text-gray-900 dark:text-gray-100">Hidden Size:</label>
            <input id="hiddenSize" type="text" value={hiddenSize} onChange={handleHiddenSizeChange} className="mt-1 block w-full rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" />
          </div>
          <button type="submit" className="w-full bg-indigo-600 border border-transparent rounded-md py-2 px-4 inline-flex justify-center text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Submit</button>
        </form>
      </div>
    )
  );
};

export default ContextMenu;