// DebugWindow.tsx
import React from 'react';

interface DebugWindowProps {
  canvasMap: Map<string, string>;
}

class DebugWindow extends React.Component<DebugWindowProps> {
  render() {
    return (
      <div>
        {Array.from(this.props.canvasMap.entries()).map(([key, value]) => (
          <div key={key}>
            {`ID: ${key}, Name: ${value}`}
          </div>
        ))}
      </div>
    );
  }
}

export default DebugWindow;
