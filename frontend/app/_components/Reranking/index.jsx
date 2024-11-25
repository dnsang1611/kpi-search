'use client'

import React, { useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  removeRelevantImage,
  removeIrrelevantImage
} from '@/_store/slices/rerankSlice';
import { HOST_URL } from "@/_constants/api";
import clsx from 'clsx';

const Reranking = () => {
  const dispatch = useDispatch();
  const { relevantImages, irrelevantImages } = useSelector(state => state.rerank);

  const handleRemoveRelevant = (image) => {
    dispatch(removeRelevantImage(image));
  };

  const handleRemoveIrrelevant = (image) => {
    dispatch(removeIrrelevantImage(image));
  };

  const isReranking = relevantImages.length === 0 && irrelevantImages.length === 0;

  const handleReranking = async () => {
    const requestData = {
      original_query: "",
      relevant_images: relevantImages,
      irrelevant_images: irrelevantImages,
      topk: topK
    }

    try {
      const response = await fetch(`${HOST_URL}rerank_search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error('Failed to rerank search results.');
      }

      const resultData = await response.json();

      dispatch(setResult(resultData))
    } catch (error) {
      console.error('Error during reranking:', error);
    }
  }

  const handleClear = () => {
    dispatch(resetRerank());
  }

  return (
    <>
      <div className="flex flex-col gap-2 bg-white p-3 rounded-lg">
        <div className="flex">
          <button
            className="text-xs font-medium text-blue-700 hover:underline"
            onClick={handleClear}
          >
            Clear
          </button>
        </div>
        <div className="flex flex-col gap-2 bg-white p-2 rounded-lg">
          <div className="grid grid-cols-2 gap-2">

            {/* Irrelevant Images Section */}
            <div className="flex flex-col gap-2">
              <h3 className="text-sm self-center font-semibold">Irrelevant Images</h3>
              <div className="grid gap-2">
                {irrelevantImages.map((image, index) => (
                  <div key={index} className="relative border rounded-md">
                    <button
                      className="absolute top-1 right-1 bg-red-500 text-white px-1.5 py-0.25 rounded-full"
                      onClick={() => handleRemoveIrrelevant(image)}
                    >
                      &times;
                    </button>
                    <img
                      src={`${HOST_URL}frame/${image}`}
                      alt={`Irrelevant Image ${index}`}
                      className="w-full h-auto cursor-pointer"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Relevant Images Section */}
            <div className="flex flex-col gap-2">
              <h3 className="text-sm self-center font-semibold">Relevant Images</h3>
              <div className="grid gap-2">
                {relevantImages.map((image, index) => (
                  <div key={index} className="relative border rounded-md">
                    <button
                      className="absolute top-1 right-1 bg-red-500 text-white px-1.5 py-0.25 rounded-full"
                      onClick={() => handleRemoveRelevant(image)}
                    >
                      &times;
                    </button>
                    <img
                      src={`${HOST_URL}frame/${image}`}
                      alt={`Relevant Image ${index}`}
                      className="w-full h-auto cursor-pointer"
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <button
          className={clsx('bg-blue-600 text-white p-2 rounded-full mt-2 hover:bg-blue-700', isReranking ? "opacity-50 cursor-not-allowed" : ""
          )}
          disabled={isReranking}
          onClick={handleReranking}
        >
          Reranking
        </button>
      </div>
    </>
  );
};

export default Reranking;
