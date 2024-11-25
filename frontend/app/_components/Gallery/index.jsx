'use client'

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { HOST_URL } from '@/_constants/api';
import { fetchCsvData } from '@/_utils/fetchCsvData';
import { useDispatch, useSelector } from "react-redux";
import Video from './Video';
import { ArrowLeft, ArrowRight, PlayCircle, Plus, Minus, ExternalLink } from 'lucide-react';
import {
  addRelevantImage,
  addIrrelevantImage,
  removeRelevantImage,
  removeIrrelevantImage,
} from '@/_store/slices/rerankSlice';
import { addSelectedImage, removeSelectedImage } from '@/_store/slices/imageSearchSlice';
import { toggleActiveButton } from '@/_store/slices/searchSlice';
import { toast } from 'react-toastify';

const Gallery = () => {
  const dispatch = useDispatch()
  const result = useSelector(state => state.search.result);
  const relevantImages = useSelector(state => state.rerank.relevantImages);
  const irrelevantImages = useSelector(state => state.rerank.irrelevantImages);
  const selectedImages = useSelector(state => state.imageSearch.selectedImages);
  const activeButtons = useSelector(state => state.search.activeButtons);

  const [clickedFrame, setClickedFrame] = useState(null);
  const [nearbyFrames, setNearbyFrames] = useState([]);
  const [videoTime, setVideoTime] = useState(0);
  const [showVideo, setShowVideo] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [isQaSubmit, setIsQaSubmit] = useState(false);
  const [qaAnswer, setQaAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const videoModalRef = useRef(null);
  const modalRef = useRef(null);

  // Store image name when clicked on an image
  useEffect(() => {
    if (result && result.length > 0) {
      handleImageClick(result[0].frame);
    }
  }, [result]);

  const getFrameIndex = useCallback((frame) => parseInt(frame.split('/')[2].split('.')[0], 10), []);

  // Show information like nearby frames, image's name,... when clicked on an image
  const handleImageClick = useCallback(async (frame) => {
    try {
      setClickedFrame(frame);
      const frameParts = frame.split('/');

      const csvUrl = `${HOST_URL}mapframe/${frameParts[1]}.csv`;
      const csvData = await fetchCsvData(csvUrl);
      const frameIdx = getFrameIndex(frame);
      const n = csvData.findIndex(row => parseInt(row[3], 10) === frameIdx);
      if (n !== -1) {
        const nValue = parseInt(csvData[n][0], 10);
        displayNearbyFrames(nValue, csvData);
        const clickedFrameData = csvData[n];
        console.log(clickedFrameData[1])
        if (clickedFrameData) {
          setVideoTime(parseFloat(clickedFrameData[1]));
        }
      }
    } catch (err) {
      console.error('Failed to handle image click:', err);
    }
  }, [setClickedFrame, setVideoTime, setNearbyFrames, getFrameIndex]);

  // Display 6 nearby frames of a chosen image (3 previous, 3 next)
  const displayNearbyFrames = useCallback((nValue, frames) => {
    const idx = frames.findIndex(row => parseInt(row[0], 10) === nValue);
    if (idx === -1) return;

    const nearby = [];
    const range = 3;

    for (let i = -range; i <= range; i++) {
      const targetIdx = idx + i;

      if (targetIdx >= 0 && targetIdx < frames.length) {
        nearby.push(frames[targetIdx]);
      }
    }

    setNearbyFrames(
      nearby.map(row => ({
        frameIdx: row[3], // frame_idx column
        ptsTime: row[1],  // pts_time column
      }))
    );
  }, []);

  const findNearbyFrame = useCallback((offset) => {
    const currentIdx = getFrameIndex(clickedFrame);
    const totalFrames = nearbyFrames.length;
    const currentNearbyIdx = nearbyFrames.findIndex(item => parseInt(item.frameIdx, 10) === currentIdx);
    if (currentNearbyIdx !== -1) {
      const newNearbyIdx = (currentNearbyIdx + offset + totalFrames) % totalFrames;
      const newFrame = nearbyFrames[newNearbyIdx];
      const newFrameSrc = `${clickedFrame.split('/')[0]}/${clickedFrame.split('/')[1]}/${newFrame.frameIdx.padStart(7, '0')}.jpg`;
      return newFrameSrc;
    }
    return null;
  }, [clickedFrame, nearbyFrames, getFrameIndex]);

  const handlePrev = useCallback(() => {
    const newFrameSrc = findNearbyFrame(-1);
    if (newFrameSrc) handleImageClick(newFrameSrc);
  }, [findNearbyFrame, handleImageClick]);

  const handleNext = useCallback(() => {
    const newFrameSrc = findNearbyFrame(1);
    if (newFrameSrc) handleImageClick(newFrameSrc);
  }, [findNearbyFrame, handleImageClick]);

  const isImageAdded = useCallback((frame) => {
    return relevantImages.includes(frame) || irrelevantImages.includes(frame);
  }, [relevantImages, irrelevantImages]);

  const handleAddRelevantImage = (frame) => {
    if (!isImageAdded(frame)) {
      dispatch(addRelevantImage(frame));
    } else {
      dispatch(removeRelevantImage(frame));
    }
  };

  const handleAddIrrelevantImage = (frame) => {
    if (!isImageAdded(frame)) {
      dispatch(addIrrelevantImage(frame));
    } else {
      dispatch(removeIrrelevantImage(frame));
    }
  };

  // Handle right click to search similar image or add to selected images
  const handleImageContextMenu = async (e, imagePath) => {
    e.preventDefault();

    const finalImagePath = `/aic2024/Data/Newframe/${imagePath}`.trim();

    if (selectedImages.includes(finalImagePath)) {
      dispatch(removeSelectedImage(finalImagePath));
    } else {
      dispatch(addSelectedImage(finalImagePath));
    }

    if (!activeButtons.includes("image") && selectedImages.length === 0) {
      dispatch(toggleActiveButton("image"));
    }
    // Optionally, handle image search on right-click without adding to selected images
    /*
    const requestBody = new FormData();
    requestBody.append("image_path", imagePath);
    requestBody.append("topk", topK);
    try {
      const response = await fetch(`${HOST_URL}image_search`,{
        method: "POST",
        body: requestBody,
      });
      if (!response.ok) {
        throw new Error("Failed to fetch results from the API.");
      }
      const result = await response.json();
      setresult(result);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    */
  };

  const handlePlayVideo = () => {
    setShowVideo(true);
  };

  const handleCloseVideo = () => {
    setShowVideo(false);
  };

  const handleClickOutside = useCallback(event => {
    if (!videoModalRef.current?.contains(event.target)) {
      setShowVideo(false);
    }
    if (!modalRef.current?.contains(event.target)) {
      setIsModalOpen(false);
    }
  }, []);

  // Close when clicked outside video modal
  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [handleClickOutside]);

  // const submitAnswer = async (imagePath) => {
  //   let item = imagePath.split("/")[1];
  //   let frame = parseInt(imagePath.split("/")[2], 10);
  //   let url = `https://eventretrieval.one/api/v1/submit?item=${item}&frame=${frame}&session=${session}`;
  //   try {
  //     let response = await fetch(url, { method: "GET", headers: { Authorization: `Bearer ${session}` } });
  //     if (response.ok) {
  //       toast.success("Success! Result submitted.");
  //       // Log the response data
  //       const data = await response.json();
  //       console.log(data)
  //     } else {
  //       toast.error("Error submitting the result.");
  //       // Log the error response data
  //       const errorData = await response.json();
  //       console.log(errorData)
  //     }
  //   } catch (error) {
  //     console.error("An error occurred:", error);
  //   }
  // };


  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  // Handle QA Submission
  const handleQaSubmit = async (imagePath) => {
    const frameParts = imagePath.split('/');

    const csvUrl = `${HOST_URL}mapframe/${frameParts[1]}.csv`;
    const csvData = await fetchCsvData(csvUrl);
    const frameIdx = getFrameIndex(frame);
    const n = csvData.findIndex(row => parseInt(row[3], 10) === frameIdx);
    let item = imagePath.split("/")[1];
    let frame = parseInt(imagePath.split("/")[2], 10);
    console.log(item, frame)
    if (!qaAnswer.trim()) {
      toast.error('Please enter an answer.');
      return;
    }

    // try {
    //   setIsSubmitting(true);
    //   const submitData = {
    //     answer: qaAnswer,
    //     frame,
    //   };
    //   const response = await submitServices.submit_qa(
    //     { evaluationId, sessionId },
    //     submitData
    //   );
    //   toast.success('QA submission successful!');
    //   console.log(response); // Handle response if needed
    // } catch (error) {
    //   console.error('QA Submission failed:', error);
    //   toast.error('Failed to submit QA answer.');
    // } finally {
    //   setIsSubmitting(false);
    //   setQaAnswer('');
    // }
  };

  // Handle Regular Submission
  const handleRegularSubmit = async (imagePath) => {
    let item = imagePath.split("/")[1];
    let frame = parseInt(imagePath.split("/")[2], 10);
    try {
      setIsSubmitting(true);
      const submitData = {
        frame,
        ms: 0,
      };
      const response = await submitServices.submit_media(
        { evaluationId, sessionId },
        submitData
      );
      toast.success('Submission successful!');
      console.log(response); // Handle response if needed
    } catch (error) {
      console.error('Submission failed:', error);
      toast.error('Failed to submit.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className='w-3/4 flex flex-col h-screen justify-between bg-blue-100'>
      <div className="grid grid-cols-5 overflow-y-auto flex-grow-0" style={{ maxHeight: `${Math.min(100 * 7 / 8, 100)}vh` }}>
        {result && result.map((item, index) => (
          <div key={index} className="relative">
            <img
              src={`/aic2024/Data/Newframe/${item.frame}`}
              alt={`Image ${index}`}
              className={`w-full object-cover cursor-pointer box-border ${clickedFrame === item.frame ? 'outline outline-4 -outline-offset-4 outline-blue-600' : ''}`}
              onClick={() => handleImageClick(item.frame)}
              onContextMenu={(event) => handleImageContextMenu(event, item.frame)}
            />
            {/* <p className="absolute top-2 left-2 bg-white bg-opacity-75 px-1 rounded text-xs">{item.score}</p> */}
            <button
              className="absolute top-1 right-1"
              onClick={() => handleAddRelevantImage(item.frame)}
              aria-label="Add as Relevant"
            >
              <Plus
                size={14}
                className={`cursor-pointer rounded-sm ${relevantImages.includes(item.frame) ? 'bg-green-500 text-white' : 'text-green-500 border border-green-500 bg-white hover:bg-green-500 hover:text-white'}`}
              />
            </button>
            <button
              className="absolute top-1 left-1"
              onClick={() => handleAddIrrelevantImage(item.frame)}
              aria-label="Add as Irrelevant"
            >
              <Minus
                size={14}
                className={`cursor-pointer rounded-sm ${irrelevantImages.includes(item.frame) ? 'bg-red-500 text-white' : 'text-red-500 border border-red-500 bg-white hover:bg-red-500 hover:text-white'}`}
              />
            </button>
            {/* <button
              className='absolute bottom-1 right-1 text-[8px] text-white bg-blue-600 rounded-sm p-1 hover:bg-blue-700'
              onClick={() => {
                // submitAnswer(item.frame)
                console.log(item.frame)
              }}
            >
              Submit
            </button> */}
            {/* Regular Submission Button */}
            <button
              onClick={handleRegularSubmit}
              disabled={isSubmitting}
              className="absolute bottom-1 right-1 text-[8px] p-1 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Submit KIS
            </button>

            {/* QA Submission Toggle Button */}
            <button
              onClick={() => setIsQaSubmit(!isQaSubmit)}
              className="absolute bottom-1 left-1 text-[8px] p-1 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Submit QA
            </button>
          </div>
        ))}
        {/* QA Submission Form */}
        {isQaSubmit && (
          <div className="absolute flex gap-1 items-start bg-white rounded p-2 transition-colors border border-slate-700">
            <input
              type="text"
              value={qaAnswer}
              onChange={(e) => setQaAnswer(e.target.value)}
              placeholder="Enter your answer"
              className="resize-none px-0 m-0 w-full text-gray-900 border-none outline-none text-sm bg-transparent"
            />
            <button
              onClick={handleQaSubmit}
              disabled={isSubmitting}
              className="flex items-center text-xs gap-1 bg-blue-600 text-white p-1 rounded hover:bg-blue-700 transition"
            >
              Submit
            </button>
          </div>
        )}
      </div>
      {clickedFrame && (
        <>
          <div className='flex flex-col bg-white'>
            <div className="flex justify-between p-2 items-center">
              <div className='flex flex-row gap-2 items-center'>
                <p className='text-base'>{clickedFrame.split('/')[1]}, {getFrameIndex(clickedFrame)}</p>
                <button onClick={handleOpenModal}>
                  <ExternalLink size={16} className={`cursor-pointer rounded-sm text-black text-lg`} />
                </button>
              </div>
              <button
                onClick={handlePlayVideo}
                className="w-fit bg-blue-600 text-white rounded-full cursor-pointer hover:bg-blue-700 transition duration-300"
              >
                <PlayCircle size={24} />
              </button>
              <div className='flex gap-4'>
                <button
                  onClick={handlePrev}
                  className="text-blue-600 hover:text-blue-700 cursor-pointer font-medium"
                >
                  <ArrowLeft size={20} />
                </button>
                <button
                  onClick={handleNext}
                  className="text-blue-600 hover:text-blue-700 cursor-pointer font-medium"
                >
                  <ArrowRight size={20} />
                </button>
              </div>
            </div>
            <div className="grid grid-cols-7">
              {nearbyFrames.map((item, index) => {
                const imgSrc = `${clickedFrame.split('/')[0]}/${clickedFrame.split('/')[1]}/${(item.frameIdx).padStart(7, '0')}.jpg`;
                return (
                  <div key={index} className="relative">
                    <img
                      src={`/aic2024/Data/Newframe/${imgSrc}`}
                      alt={`Nearby Frame ${index}`}
                      className={`w-full max-h-20 object-contain cursor-pointer box-border ${getFrameIndex(clickedFrame) == item.frameIdx ? 'outline outline-4 -outline-offset-4 outline-blue-600' : ''}`}
                      onClick={() => handleImageClick(imgSrc)}
                      onContextMenu={(event) => handleImageContextMenu(event, imgSrc)}
                    />
                  </div>
                );
              })}
            </div>
          </div>
          {showVideo && (
            <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
              <div ref={videoModalRef} className="rounded relative">
                <button onClick={handleCloseVideo} className="absolute top-2 right-2 text-xl text-white px-2.5 py-0.5 rounded-full bg-red-500">&times;</button>
                <Video path={clickedFrame.split('/')[1]} videoTime={videoTime} />
              </div>
            </div>
          )}
          {isModalOpen && (
            <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
              <div className="rounded relative" ref={modalRef}>
                <button onClick={closeModal} className="absolute top-2 right-2 text-xl text-white px-2.5 py-0.5 rounded-full bg-red-500">&times;</button>
                <img src={`/aic2024/Data/Newframe/${clickedFrame}`} alt="Modal Content" className="max-w-full max-h-full" />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
};

export default Gallery;
