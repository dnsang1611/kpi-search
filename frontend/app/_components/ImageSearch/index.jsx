import React, { useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import { addSelectedImage, removeSelectedImage } from "@/_store/slices/imageSearchSlice";
import { toast } from "react-toastify";

const ImageSearch = () => {
    const dispatch = useDispatch();

    const selectedImages = useSelector(state => state.imageSearch.selectedImages);

    const [imageUrl, setImageUrl] = useState("");

    const handleAddImage = () => {
        const trimmedUrl = imageUrl.trim();
        if (trimmedUrl === "") {
            toast.warn("Image URL cannot be empty.");
            return;
        }
        dispatch(addSelectedImage(trimmedUrl));
        setImageUrl("");
    };

    const handleRemoveImage = (url) => {
        dispatch(removeSelectedImage(url));
    };

    const handleKeyPress = (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleAddImage();
        }
    };

    return (
        <div>
            <div className="flex space-x-1">
                <div className="flex gap-1 items-start w-full rounded p-3 transition-colors bg-slate-100 border border-slate-700">
                    <textarea
                        type="text"
                        value={imageUrl}
                        onChange={(e) => setImageUrl(e.target.value)}
                        onKeyPress={handleKeyPress}
                        tabIndex={0}
                        dir="auto"
                        rows={1}
                        placeholder="Enter image URL"
                        className="resize-none px-0 m-0 max-h-32 w-full text-gray-900 border-none outline-none placeholder:uppercase placeholder:text-sm bg-transparent overflow-y-auto"
                    />
                    <button
                        onClick={handleAddImage}
                        className="flex items-center gap-1 bg-blue-600 text-white p-1 rounded hover:bg-blue-700 transition"
                        aria-label="Add image"
                    >
                        <Plus size={14} />
                    </button>
                </div>
            </div>
            {selectedImages.length > 0 && (
                <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    {selectedImages.map((url, index) => (
                        <div key={index} className="relative">
                            <img
                                src={url}
                                alt={`Selected ${index + 1}`}
                                className="w-full h-32 object-cover rounded-md"
                                onError={(e) => { e.target.src = "/placeholder.png"; }}
                            />
                            <button
                                onClick={() => handleRemoveImage(url)} // Pass URL instead of index
                                className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                                aria-label="Remove image"
                            >
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ImageSearch;
