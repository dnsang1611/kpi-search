'use client'

import clsx from 'clsx'
import React, { useState, useEffect } from "react";
import { HOST_URL } from "@/_constants/api";
import ObjectSearch from "../ObjectSearch";
// import Sketch from "../Sketch";
// import Pose from "../Pose";
import Color from "../Color";
import Temporal from "../Temporal"
import ImageSearch from "../ImageSearch";
import { useDispatch, useSelector } from "react-redux";
import { resetActiveButtons, toggleActiveButton, setResult, setObjectData, setQuery, resetData, setSketchData, setPoseData, setColorData } from "@/_store/slices/searchSlice";
import { resetSelectedImages } from "@/_store/slices/imageSearchSlice";
import { resetRerank } from '@/_store/slices/rerankSlice';

const SearchCard = ({ topk }) => {
	const dispatch = useDispatch()

	const activeButtons = useSelector(state => state.search.activeButtons)
	const selectedImages = useSelector(state => state.imageSearch.selectedImages)
	const topK = useSelector(state => state.search.topK)
	const objectData = useSelector(state => state.search.objectData)
	const temporalData = useSelector(state => state.search.temporalData)
	// const sketchData = useSelector(state => state.search.sketchData)
	const poseData = useSelector(state => state.search.poseData)
	const colorData = useSelector(state => state.search.colorData)

	// State for storing user input with type and value
	const [inputValues, setInputValues] = useState(new Map());

	// State for redo action
	const [redoStack, setRedoStack] = useState([]);

	// State for handling using sketch
	// const [sketchCanvasRef, setSketchCanvasRef] = useState(null);

	// Ref for the file input
	// const fileInputRef = useRef();

	// const [object, setObject] = useState([]);

	useEffect(() => {
		const newInputValues = new Map(inputValues); // Copy existing inputs
		activeButtons.forEach(type => {
			if (!newInputValues.has(type)) {
				switch (type) {
					case 'text':
					case 'ocr':
					case 'asr':
						newInputValues.set(type, "");
						break;
					case 'object':
						newInputValues.set(type, objectData);
						break;
					case 'color':
						newInputValues.set(type, colorData);
						break;
					case 'temporal':
						newInputValues.set(type, temporalData);
						break;
					case 'pose':
						newInputValues.set(type, poseData);
						break;
					case 'image':
						newInputValues.set(type, selectedImages);
						break;
					default:
						newInputValues.set(type, "");
						break;
				}
			}
		});
		setInputValues(newInputValues);
	}, [activeButtons, objectData, colorData, temporalData, poseData, selectedImages]);

	// Make the button activate when clicked
	const handleButtonClick = (buttonType) => {
		dispatch(toggleActiveButton(buttonType));

		setInputValues(prevInputValues => {
			const newInputValues = new Map(prevInputValues);
			if (newInputValues.has(buttonType)) {
				newInputValues.delete(buttonType);
			} else {
				newInputValues.set(buttonType, "");
			}
			return newInputValues;
		});
	};


	// Close an input query
	const handleCloseClick = (type) => {
		dispatch(toggleActiveButton(type));

		// Reset corresponding state based on type
		switch (type) {
			case "text":
			case "ocr":
			case "asr":
				dispatch(setQuery(""));
				break;
			case "object":
				dispatch(setObjectData([]));
				break;
			case "sketch":
				dispatch(setSketchData(""));
				break;
			case "pose":
				dispatch(setPoseData([]));
				break;
			case "color":
				dispatch(setColorData(Array(25).fill(null)));
				break;
			case "image":
				// Handle image state reset
				break;
			case "temporal":
				// Handle temporal state reset
				break;
			default:
				break;
		}

		setInputValues(prevInputValues => {
			const newInputValues = new Map(prevInputValues);
			newInputValues.delete(type);
			return newInputValues;
		});
	};

	// Update value when changed an input query 
	const handleInputChange = (type, e) => {
		setInputValues((prevInputValues) => {
			const newInputValues = new Map(prevInputValues);
			newInputValues.set(type, e.target.value);

			if (type === "text") {
				dispatch(setQuery(e.target.value));
			}

			return newInputValues;
		});
	};

	// Undo the action
	const handleUndo = () => {
		if (inputValues.size > 1) {
			const keys = Array.from(inputValues.keys());
			const removedType = keys[keys.length - 1];
			const removedValue = inputValues.get(removedType);
			setInputValues(prevInputValues => {
				const newInputValues = new Map(prevInputValues);
				newInputValues.delete(removedType);
				return newInputValues;
			});
			setRedoStack([...redoStack, { type: removedType, value: removedValue }]);

			dispatch(toggleActiveButton(removedType));
		}
	};

	// Redo the action
	const handleRedo = () => {
		if (redoStack.length > 0) {
			const restoredItem = redoStack[redoStack.length - 1];
			setInputValues(prevInputValues => {
				const newInputValues = new Map(prevInputValues);
				newInputValues.set(restoredItem.type, restoredItem.value);
				return newInputValues;
			});
			setRedoStack(redoStack.slice(0, -1));

			dispatch(toggleActiveButton(restoredItem.type));
		}
	};

	// Reset all input query to the beginning (only use text query)
	const handleReset = (e) => {
		e.preventDefault();
		setInputValues(new Map());
		setRedoStack([]);
		dispatch(resetActiveButtons());
		dispatch(resetData());
		dispatch(resetRerank());
		dispatch(resetSelectedImages());
	};

	const fetchImageSearch = async (imagePaths, topK) => {
		const apiEndpoint = `${HOST_URL}image_search`;
		const requestBody = new FormData();

		imagePaths.forEach((imagePath) => {
			const cleanedPath = imagePath.trim();
			requestBody.append("query", cleanedPath);
		});

		requestBody.append("topk", topK);

		try {
			const response = await fetch(apiEndpoint, {
				method: "POST",
				body: requestBody,
			});

			if (!response.ok) {
				const errorText = await response.text();
				throw new Error(`Failed to fetch results from the Image Search API: ${errorText}`);
			}

			const res = await response.json();
			dispatch(setResult(res));
		} catch (error) {
			console.error("Error fetching image search data:", error);
		}
	};

	// Logic to fetch result from API
	const fetchResults = async (queryValues) => {
		// Construct the API endpoint based on the type of query
		let apiEndpoint = `${HOST_URL}`;
		let requestBody = null;
		let headers = {};

		// Single search type handling
		if (queryValues.length === 1) {
			const { type, value } = queryValues[0];
			apiEndpoint += `${type}_search`;

			if (["object", "pose"].includes(type)) {
				requestBody = JSON.stringify({ query_input: type === "pose" ? value : value.map(coord => ({ ...coord })), topk });
				headers = { "Content-Type": "application/json" };
			} else if (["color", "temporal"].includes(type)) {
				requestBody = new FormData();
				value.forEach((item) => {
					requestBody.append("query", item);
				});
				requestBody.append("topk", topk);
			}
			else {
				requestBody = new FormData();
				requestBody.append("query", value);
				requestBody.append("topk", topk);
			}
		} else {
			// Combine search type handling
			apiEndpoint += "combine_search";
			requestBody = JSON.stringify({
				query: queryValues.map(q => q.value),
				methods: queryValues.map(q => q.type),
				topk,
			});
			headers = { "Content-Type": "application/json" };
		}

		try {
			const response = await fetch(apiEndpoint, {
				method: "POST",
				body: requestBody,
				headers: headers
			});

			console.log(apiEndpoint)

			if (!response.ok) {
				throw new Error("Failed to fetch results from the API.");
			}

			const res = await response.json();
			dispatch(setResult(res))
		} catch (error) {
			console.error("Error fetching data:", error);
		}
	};

	// Handle when clicked submit button
	const handleSubmit = async () => {
		// Construct the query values for the search
		const queryValues = [];

		inputValues.forEach((value, type) => {
			if (value !== "") {
				queryValues.push({ type, value });
			}
		});

		// Check if 'object' search is active and objectData is not empty
		if (activeButtons.includes("object") && objectData.length > 0) {
			console.log(objectData)
			queryValues.push({ type: "object", value: objectData });
		}

		// if (activeButtons.includes("sketch")) {
		//   if (sketchData) {
		//     queryValues.push({ type: "sketch", value: sketchData });
		//   } else if (sketchCanvasRef && sketchCanvasRef.current) {
		//     const drawnSketchData = await sketchCanvasRef.current.exportImage("jpeg");
		//     console.log(drawnSketchData);
		//     queryValues.push({ type: "sketch", value: drawnSketchData });
		//   }
		// }

		if (activeButtons.includes("color")) {
			// Trigger error when all data is null
			if (colorData.every((value) => value === null)) {
				console.log("Must be at least 1 value different from null");
				return;
			}

			queryValues.push({ type: "color", value: colorData })
		}

		if (activeButtons.includes("temporal")) {
			// Trigger error when at least 1 event is empty
			console.log(temporalData);
			if (temporalData.some((event, index) => event === "")) {
				console.log("All events must be not empty")
				return
			}

			queryValues.push({ type: "temporal", value: temporalData });
		}

		if (activeButtons.includes("pose") && poseData && poseData.length > 0) {
			queryValues.push({ type: "pose", value: poseData });
		}

		if (activeButtons.includes("image") && selectedImages && selectedImages.length > 0) {
			fetchImageSearch(selectedImages, topK);
		}

		// Proceed with the search if there are valid query values
		if (queryValues.some(data => data.value !== "")) {
			await fetchResults(queryValues);
		}
	};

	// const handleFilter = async () => {
	//   console.log(object)
	//   const requestBody = JSON.stringify({ object: object });
	//   try {
	//     const response = await fetch(`${HOST_URL}filter`, {
	//       method: 'POST',
	//       headers: {
	//         'Content-Type': 'application/json'
	//       },
	//       body: requestBody
	//     });

	//     if (!response.ok) {
	//       throw new Error(`HTTP error! status: ${response.status}`);
	//     }

	//     const result = await response.json();
	//     console.log('Filter results:', result);
	//   } catch (error) {
	//     console.error('Error during fetch:', error);
	//   }
	// }

	const showObject = activeButtons.includes("object");
	// const showPose = activeButtons.includes("pose");
	const showColor = activeButtons.includes("color");
	const showImage = activeButtons.includes("image");
	const showTemporal = activeButtons.includes("temporal");

	// const showSketchCanvas = activeButtons.includes("sketch");

	// Handle file change for the sketch upload
	// const handleSketchUpload = useCallback((e) => {
	//   const file = e.target.files[0];
	//   if (file) {
	//     const reader = new FileReader();
	//     reader.onload = (e) => {
	//       setSketchData(e.target.result);
	//     };
	//     reader.readAsDataURL(file);
	//   }
	// }, []);

	// Function to clear the uploaded sketch
	// const handleClearUploadedSketch = () => {
	//   setSketchData("");
	//   if (fileInputRef.current) {
	//     fileInputRef.current.value = "";  // Reset the file input
	//   }
	// };

	useEffect(() => {
		const textareas = document.querySelectorAll("textarea");
		textareas.forEach((textarea) => {
			textarea.style.height = "auto";
			textarea.style.height = `${textarea.scrollHeight}px`;

			textarea.addEventListener("input", () => {
				textarea.style.height = "auto";
				textarea.style.height = `${textarea.scrollHeight}px`;
			});
		});
	}, [inputValues]);

	return (
		<div className="flex flex-col gap-2 bg-white p-3 rounded-lg">
			<div className="flex flex-col gap-1 relative">
				<div className="flex flex-row justify-between text-xs text-blue-600 font-semibold">
					<div className="flex flex-row gap-2">
						<button onClick={handleUndo} className="hover:text-blue-800">
							Undo
						</button>
						<button onClick={handleRedo} className="hover:text-blue-800">
							Redo
						</button>
					</div>
					<button className="cursor-pointer mb-1 hover:text-blue-800" onClick={handleReset}>
						Reset
					</button>
				</div>
				<div className="grid grid-cols-4 gap-1 text-gray-900">
					{["text", "ocr", "asr", "object", "color", "video", "image", "temporal"].map((type) => (
						<div
							key={type}
							className={clsx(
								'col-start self-stretch p-1 text-center rounded-md text-xs font-medium cursor-pointer',
								activeButtons.includes(type) ? "bg-blue-600 text-white" : "bg-blue-100"
							)}
							onClick={() => handleButtonClick(type)}
						>
							<button className="uppercase">{type}</button>
						</div>
					))}
				</div>
				{[...inputValues.keys()].map((type) => {
					const input = { type, value: inputValues.get(type) };
					return !["object", "sketch", "pose", "color", "image", "temporal"].includes(type) && (
						<div key={type} className='pt-2'>
							<div className="flex gap-1 items-start w-full rounded p-3 transition-colors bg-slate-100 border border-slate-700">
								<textarea
									id={type}
									value={input.value || ''}
									onChange={(e) => handleInputChange(type, e)}
									onKeyDown={(e) => {
										if (e.key === 'Enter') {
											e.preventDefault()
											handleSubmit();
										}
									}}
									placeholder={type}
									tabIndex={0}
									dir="auto"
									rows={1}
									className="resize-none px-0 m-0 max-h-32 w-full text-gray-900 border-none outline-none placeholder:uppercase placeholder:text-sm bg-transparent overflow-y-auto"
								/>
								<button onClick={() => handleCloseClick(type)}>
									&times;
								</button>
							</div>
						</div>
					)
				})}
				{showImage &&
					<ImageSearch />
				}
				{showTemporal &&
					<Temporal />
				}
				{showObject &&
					<div className="relative pt-2">
						<button onClick={() => handleCloseClick("object")} className="absolute top-0 right-0">
							&times;
						</button>
						<ObjectSearch />
					</div>
				}
				{showColor &&
					<div className="relative pt-2">
						<button onClick={() => handleCloseClick("color")} className="absolute top-1 right-0 cursor-pointer">
							&times;
						</button>
						<Color />
					</div>
				}
				{/* {showSketchCanvas &&
          <div className="relative pt-5">
            <button onClick={() => handleCloseClick("sketch")} className="absolute top-0 right-0 cursor-pointer">
              &times;
            </button>
            {!sketchData && (
              <Sketch setCanvasRef={setSketchCanvasRef} />
            )}
            {sketchData && (
              <img src={sketchData} className="w-full h-auto" alt="Uploaded" />
            )}
            <div className="flex justify-between gap-2 mt-2 items-end">
              <div className="w-full">
                <label htmlFor="sketchUpload" className="text-sm font-medium text-gray-700 mb-1">Upload sketch</label>
                <input
                  ref={fileInputRef}
                  type="file"
                  id="sketchUpload"
                  accept="image/*"
                  onChange={handleSketchUpload}
                  className="block w-full text-sm text-gray-900 rounded-md border border-gray-300 cursor-pointer focus:border-blue-500"
                />
              </div>
              <button
                onClick={handleClearUploadedSketch}
                className="bg-red-500 text-white text-xs p-1.5 rounded-md hover:bg-red-600"
              >
                Clear
              </button>
            </div>
          </div>
        } */}
				{/* {showPose &&
          <div className="relative pt-5">
            <p className="mb-2 text-sm">Move the stick man joints</p>
            <button onClick={() => handleCloseClick("pose")} className="absolute top-0 right-0 cursor-pointer">
              &times;
            </button>
            <Pose />
          </div>
        } */}
				<button onClick={handleSubmit} onKeyDown={(e) => {
					if (input.type === "text" && e.key === "Enter") {
						e.preventDefault();
						handleSubmit();
					}
				}} className="bg-blue-600 text-white p-2 rounded-full mt-2 hover:bg-blue-700">Search</button>
			</div>
		</div>
	);
};

export default SearchCard;