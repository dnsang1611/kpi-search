import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { setTemporalData } from "@/_store/slices/searchSlice";

const Temporal = () => {
    const dispatch = useDispatch();
    const temporalData = useSelector((state) => state.search.temporalData);

    const handleAddEvent = () => {
        if (temporalData.length < 5) {
            const newEvents = [...temporalData, ""];
            dispatch(setTemporalData(newEvents));
        }
    };

    const handleRemoveEvent = (index) => {
        if (temporalData.length <= 2) {
            const newEvents = [...temporalData];
            newEvents[index] = "";
            dispatch(setTemporalData(newEvents));
        } else {
            const newEvents = temporalData.filter((_, i) => i !== index);
            dispatch(setTemporalData(newEvents));
        }
    };

    const handleEventChange = (index, value) => {
        const newEvents = [...temporalData];
        newEvents[index] = value;
        dispatch(setTemporalData(newEvents));
    };

    return (
        <div className="pt-2">
            <div className="flex justify-between items-center">
                <p className="text-xs font-bold">Temporal search</p>
                <button
                    className="mb-2 float-right p-1 bg-green-200 text-green-700 rounded text-xs font-medium hover:bg-green-300 disabled:cursor-not-allowed disabled:bg-green-100"
                    onClick={handleAddEvent}
                    disabled={temporalData.length >= 5}
                >
                    Add event
                </button>
            </div>
            <div className="w-full space-y-1">
                {temporalData.map((text, index) => (
                    <div
                        key={index}
                        className="flex gap-2 items-start w-full rounded p-3 transition-colors bg-slate-100 border border-slate-700"                    >
                        <textarea
                            placeholder={`Event ${index + 1}`}
                            value={text || ''}
                            onChange={(e) => handleEventChange(index, e.target.value)}
                            tabIndex={0}
                            dir="auto"
                            rows={1}
                            className="resize-none px-0 m-0 max-h-32 w-full text-gray-900 border-none outline-none placeholder:uppercase placeholder:text-sm bg-transparent overflow-y-auto"
                        />
                        <button onClick={() => handleRemoveEvent(index)} disabled={temporalData.length <= 2} className="disabled:cursor-not-allowed">
                            &times;
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Temporal;
