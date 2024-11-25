// import React, { useState } from 'react';
// import { SketchPicker } from 'react-color';

// const Color = () => {
//   const initialColors = Array(9).fill('#000000');
//   const [colors, setColors] = useState(initialColors);
//   const [RGBColors, setRGBColors] = useState(initialColors.map(hexToRgb));
//   const [selectedCell, setSelectedCell] = useState(0);
//   const [colorHistory, setColorHistory] = useState([]);
//   const [redoHistory, setRedoHistory] = useState([]);

//   console.log(RGBColors)

//   function hexToRgb(hex) {
//     hex = hex.replace(/^#/, '');
//     if (hex.length === 3) {
//       hex = hex.split('').map(char => char + char).join('');
//     }
//     const r = parseInt(hex.slice(0, 2), 16);
//     const g = parseInt(hex.slice(2, 4), 16);
//     const b = parseInt(hex.slice(4, 6), 16);
//     return [r, g, b];
//   }

//   const handleColorChange = (color) => {
//     if (selectedCell !== null) {
//       const newColors = [...colors];
//       const newRGBColors = [...RGBColors];
//       const newColorHistory = [...colorHistory];

//       // Save the current state before changing the color
//       newColorHistory.push([...colors]);

//       newColors[selectedCell] = color.hex;
//       newRGBColors[selectedCell] = hexToRgb(color.hex);

//       setColors(newColors);
//       setRGBColors(newRGBColors);
//       setColorHistory(newColorHistory);
//       setRedoHistory([]); // Clear redo history on new action
//     }
//   };

//   const handleCellClick = (index) => {
//     setSelectedCell(index);
//   };

//   const handleReset = () => {
//     setColors(initialColors);
//     setRGBColors(initialColors.map(hexToRgb));
//     setColorHistory([]);
//     setRedoHistory([]);
//   };

//   const handleRedo = () => {
//     if (redoHistory.length > 0) {
//       const newColors = redoHistory.pop();
//       setColors(newColors);
//       setRGBColors(newColors.map(hexToRgb));
//       setColorHistory([...colorHistory, [...colors]]);
//       setRedoHistory(redoHistory);
//     }
//   };

//   const handleUndo = () => {
//     if (colorHistory.length > 0) {
//       const previousColors = colorHistory.pop();
//       setRedoHistory([...redoHistory, [...colors]]);
//       setColors(previousColors);
//       setRGBColors(previousColors.map(hexToRgb));
//       setColorHistory(colorHistory);
//     }
//   };

//   return (
//     <div className="flex flex-col gap-5">
//       <div className="flex gap-3">
//         <button onClick={handleReset} className="text-xs text-blue-700 font-medium">Reset</button>
//         <button onClick={handleUndo} className="text-xs text-blue-700 font-medium">Undo</button>
//         <button onClick={handleRedo} className="text-xs text-blue-700 font-medium">Redo</button>
//       </div>

//       <div>
//         {selectedCell !== null && (
//           <SketchPicker
//             color={colors[selectedCell]}
//             onChangeComplete={handleColorChange}
//             className="!shadow-none"
//           />
//         )}
//       </div>

//       <div className="inline-grid grid-cols-3 w-full gap-[1px] p-[1px] bg-gray-400 border border-gray-400" style={{ aspectRatio: '16/9' }}>
//         {colors.map((color, index) => (
//           <div
//             key={index}
//             className={`${(index === selectedCell && colors[selectedCell] === "#000000") && "opacity-70" } cursor-pointer`}
//             style={{ backgroundColor: color }}
//             onClick={() => handleCellClick(index)}
//           />
//         ))}
//       </div>
//     </div>
//   );
// };

// export default Color;
