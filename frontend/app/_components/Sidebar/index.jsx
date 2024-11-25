"use client";

import Logos from "./Logos";
import React from "react";
import SearchCard from "../SearchCard";
import { useSelector, useDispatch } from 'react-redux';
import Reranking from "../Reranking";
import { setTopK } from "@/_store/slices/searchSlice";
import Login from "@/_components/Auth/Login";

const Sidebar = () => {
  const dispatch = useDispatch();

  const topK = useSelector(state => state.search.topK)

  const handleTopKChange = (e) => {
    const newValue = parseInt(e.target.value, 10);
    if (!isNaN(newValue) && newValue >= 1 && newValue <= 500) {
      dispatch(setTopK(newValue))
    }
  };

  return (
    <>
      <aside className="z-40 w-[30%] h-screen transition-transform -translate-x-full sm:translate-x-0 bg-blue-100 mx-2">
        <div className="h-full overflow-y-auto">
          <div className="grid grid-cols-4 mb-1">
            <div></div>
            <div className="col-span-2">
              <Logos />
            </div>
            <div className="self-center justify-self-end">            
              <Login />
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <div className="flex flex-col gap-1 mb-1">
              <div className="flex flex-row gap-2 justify-between items-center">
                <label htmlFor="topk" className="block text-sm font-medium text-gray-900">
                  Top K
                </label>
                <input
                  id="topk"
                  type="number"
                  value={topK}
                  onChange={handleTopKChange}
                  min="0"
                  max="500"
                  step={50}
                  className="border rounded-md px-1 py-1 text-gray-900 text-xs w-20"
                />
              </div>
              {/* Custom Slider */}
              <input
                type="range"
                id="topk-slider"
                min="0"
                max="500"
                step={50}
                value={topK}
                onChange={handleTopKChange}
                className="w-full h-1 bg-blue-200 rounded-lg appearance-none cursor-pointer 
                                           focus:outline-none"
              />
            </div>
            <SearchCard topk={topK} />

            {/* User feedback */}
            <Reranking />
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
