// ==============================================================================
// 2. FIXED DigitalGarden.tsx
// ==============================================================================

import React, { useEffect, useRef, useState, useCallback } from "react";
import { Stage, Layer, Rect, Circle, Text } from "react-konva";

interface GardenElement {
  id: string;
  x: number;
  y: number;
  type: 'flower' | 'tree' | 'thought';
  color: string;
  size: number;
  content?: string;
}

interface DigitalGardenProps {
  width?: number;
  height?: number;
  interactive?: boolean;
}

const DigitalGarden: React.FC<DigitalGardenProps> = ({ 
  width = 800, 
  height = 600, 
  interactive = true 
}) => {
  const stageRef = useRef(null);
  const [elements, setElements] = useState<GardenElement[]>([]);
  const [stageSize, setStageSize] = useState({
    width: width,
    height: height
  });

  // Initialize garden with some default elements
  useEffect(() => {
    const initialElements: GardenElement[] = [
      {
        id: '1',
        x: 200,
        y: 200,
        type: 'flower',
        color: '#FF69B4',
        size: 20,
        content: 'Beauty'
      },
      {
        id: '2',
        x: 400,
        y: 150,
        type: 'tree',
        color: '#8B4513',
        size: 40,
        content: 'Growth'
      },
      {
        id: '3',
        x: 300,
        y: 300,
        type: 'thought',
        color: '#9370DB',
        size: 15,
        content: 'What is reality?'
      }
    ];
    setElements(initialElements);
  }, []);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (width === window.innerWidth && height === window.innerHeight) {
        setStageSize({
          width: window.innerWidth,
          height: window.innerHeight
        });
      }
    };

    if (width === window.innerWidth && height === window.innerHeight) {
      window.addEventListener('resize', handleResize);
      handleResize();
      
      return () => window.removeEventListener('resize', handleResize);
    }
  }, [width, height]);

  // Add new element on click
  const handleStageClick = useCallback((e: any) => {
    if (!interactive) return;

    const stage = e.target.getStage();
    const point = stage.getPointerPosition();
    
    if (point) {
      const types: ('flower' | 'tree' | 'thought')[] = ['flower', 'tree', 'thought'];
      const colors = ['#FF69B4', '#FFD700', '#9370DB', '#FF4500', '#32CD32'];
      const thoughts = ['Wonder...', 'Curiosity', 'Growth', 'Beauty', 'Wisdom'];
      
      const newElement: GardenElement = {
        id: Date.now().toString(),
        x: point.x,
        y: point.y,
        type: types[Math.floor(Math.random() * types.length)],
        color: colors[Math.floor(Math.random() * colors.length)],
        size: 10 + Math.random() * 30,
        content: thoughts[Math.floor(Math.random() * thoughts.length)]
      };
      
      setElements(prev => [...prev, newElement]);
    }
  }, [interactive]);

  const renderElement = (element: GardenElement) => {
    const commonProps = {
      key: element.id,
      x: element.x,
      y: element.y,
      fill: element.color,
    };

    switch (element.type) {
      case 'flower':
        return (
          <React.Fragment key={element.id}>
            <Circle
              {...commonProps}
              radius={element.size}
              opacity={0.8}
            />
            {element.content && (
              <Text
                x={element.x - 20}
                y={element.y + element.size + 5}
                text={element.content}
                fontSize={10}
                fill="#333"
                width={40}
                align="center"
              />
            )}
          </React.Fragment>
        );
      case 'tree':
        return (
          <React.Fragment key={element.id}>
            <Rect
              x={element.x - element.size / 4}
              y={element.y}
              width={element.size / 2}
              height={element.size}
              fill="#8B4513"
            />
            <Circle
              x={element.x}
              y={element.y - element.size / 4}
              radius={element.size / 2}
              fill="#228B22"
            />
            {element.content && (
              <Text
                x={element.x - 20}
                y={element.y + element.size + 5}
                text={element.content}
                fontSize={10}
                fill="#333"
                width={40}
                align="center"
              />
            )}
          </React.Fragment>
        );
      case 'thought':
        return (
          <React.Fragment key={element.id}>
            <Circle
              {...commonProps}
              radius={element.size}
              opacity={0.6}
              stroke="#333"
              strokeWidth={1}
            />
            {element.content && (
              <Text
                x={element.x - 30}
                y={element.y - 5}
                text={element.content}
                fontSize={8}
                fill="#333"
                width={60}
                align="center"
              />
            )}
          </React.Fragment>
        );
      default:
        return null;
    }
  };

  return (
    <div className="digital-garden">
      <Stage 
        width={stageSize.width} 
        height={stageSize.height} 
        ref={stageRef}
        onClick={handleStageClick}
      >
        <Layer>
          {/* Garden background */}
          <Rect 
            x={0} 
            y={0} 
            width={stageSize.width} 
            height={stageSize.height} 
            fill="#a8d5ba" 
          />
          
          {/* Grass texture */}
          <Rect
            x={0}
            y={0}
            width={stageSize.width}
            height={stageSize.height}
            fill="url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8ZGVmcz4KICAgIDxwYXR0ZXJuIGlkPSJncmFzcyIgeD0iMCIgeT0iMCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj4KICAgICAgPHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjYThkNWJhIi8+CiAgICAgIDxwYXRoIGQ9Ik0wIDQwTDQwIDAgTTQwIDQwTDAgMCIgc3Ryb2tlPSIjOWNjYmI1IiBzdHJva2Utd2lkdGg9IjEiIG9wYWNpdHk9IjAuMyIvPgogICAgPC9wYXR0ZXJuPgogIDwvZGVmcz4KPC9zdmc+)"
            opacity={0.3}
          />
          
          {/* Render all garden elements */}
          {elements.map(renderElement)}
        </Layer>
      </Stage>
      
      {interactive && (
        <div className="absolute top-4 left-4 bg-white bg-opacity-80 p-2 rounded text-sm">
          Click anywhere to plant thoughts! 🌱
        </div>
      )}
    </div>
  );
};

export default DigitalGarden;