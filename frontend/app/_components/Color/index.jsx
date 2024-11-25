import React, { useState } from 'react';
import clsx from 'clsx'
import { useDispatch, useSelector } from 'react-redux';
import { setColorData } from "@/_store/slices/searchSlice";

const Color = () => {
    const dispatch = useDispatch()
    const colorData = useSelector(state => state.search.colorData);

    const initialColors = Array(25).fill(null);
    const [selectedColor, setSelectedColor] = useState('black');
    const [colorHistory, setColorHistory] = useState([]);
    const [redoHistory, setRedoHistory] = useState([]);
    const colorPalette = [
        'black', 'blue', 'brown', 'grey', 'green',
        'orange', 'pink', 'purple', 'red', 'white', 'yellow', 'aqua', 'beige', 'silver', 'lavender'
    ];

    /**
     * Handle selecting a color from the palette.
     * @param color - The color selected by the user.
     */
    const handleSelectColor = (color) => {
        setSelectedColor(color);
    };

    /**
     * Paint a single cell with the selected color.
     * @param index - The index of the cell to paint.
     */
    const handlePaintCell = (index) => {
        if (selectedColor && colorData[index] !== selectedColor) {
            setColorHistory(prev => [...prev, [...colorData]]);
            setRedoHistory([]);

            const newColorData = [...colorData];
            newColorData[index] = selectedColor;
            dispatch(setColorData(newColorData));
        }
    };

    const handleSelectAll = () => {
        if (selectedColor) {
            setColorHistory(prev => [...prev, [...colorData]]);
            setRedoHistory([]);

            const newColorData = colorData.map(() => selectedColor);
            dispatch(setColorData(newColorData));
        }
    };

    const handleReset = () => {
        // Save current state for undo
        setColorHistory(prev => [...prev, [...colorData]]);
        // Clear redo history on new action
        setRedoHistory([]);

        dispatch(setColorData(initialColors));
    };

    const handleUndo = () => {
        if (colorHistory.length === 0) return;

        const previousColors = colorHistory[colorHistory.length - 1];
        setColorHistory(prev => prev.slice(0, prev.length - 1));
        setRedoHistory(prev => [...prev, [...colorData]]);
        dispatch(setColorData(previousColors));
    };

    const handleRedo = () => {
        if (redoHistory.length === 0) return;

        const nextColors = redoHistory[redoHistory.length - 1];
        setRedoHistory(prev => prev.slice(0, prev.length - 1));
        setColorHistory(prev => [...prev, [...colorData]]);
        dispatch(setColorData(nextColors));
    };

    return (
        <div className="flex flex-col gap-2">
            <p className="text-xs font-bold">Color search</p>
            {/* Action Buttons */}
            <div className="flex gap-3">
                <button
                    onClick={handleReset}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium hover:bg-blue-200"
                >
                    Reset
                </button>
                <button
                    onClick={handleUndo}
                    disabled={colorHistory.length === 0}
                    className={`px-3 py-1 text-xs font-medium rounded ${colorHistory.length === 0
                        ? 'bg-gray-300 text-gray-700 cursor-not-allowed'
                        : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                        }`}
                >
                    Undo
                </button>
                <button
                    onClick={handleRedo}
                    disabled={redoHistory.length === 0}
                    className={`px-3 py-1 text-xs font-medium rounded ${redoHistory.length === 0
                        ? 'bg-gray-300 text-gray-700 cursor-not-allowed'
                        : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                        }`}
                >
                    Redo
                </button>
                <button
                    onClick={handleSelectAll}
                    className="px-3 py-1 bg-green-100 text-green-700 rounded text-xs font-medium hover:bg-green-200"
                >
                    Select All
                </button>
            </div>

            {/* Painting Section */}
            <div className="flex gap-2">
                {/* Color Palette */}
                <div className="flex flex-col items-center p-2 rounded bg-zinc-100">
                    <div className="mb-4 size-10 border-2 border-gray-400 rounded" style={{ backgroundColor: selectedColor }}>
                    </div>
                    <div className="grid grid-cols-3 gap-1 w-max">
                        {colorPalette.map((color, index) => (
                            <div
                                key={index}
                                className={clsx('size-6 rounded cursor-pointer', selectedColor === color && 'border-black border-2')}
                                style={{ backgroundColor: color }}
                                onClick={() => handleSelectColor(color)}
                                title={color.charAt(0).toUpperCase() + color.slice(1)}
                            />
                        ))}
                    </div>
                </div>

                {/* Canvas */}
                <div
                    className="w-full grid grid-cols-5 rounded border border-solid border-zinc-300 ltr"
                >
                    {colorData.map((color, index) => (
                        <div
                            key={index}
                            className="size-full cursor-pointer border border-solid border-zinc-300"
                            style={{ backgroundColor: color || 'transparent' }}
                            onClick={() => handlePaintCell(index)}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Color;
