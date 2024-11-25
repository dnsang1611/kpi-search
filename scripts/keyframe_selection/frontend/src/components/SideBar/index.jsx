import React, {useState} from "react";
import { useSessionContext } from "../SessionContext";
import { BACKEND_URL } from "../../constants/apis";

const SideBar = () => {
    const {metadata, video, setVideo} = useSessionContext();

    const handleSelectVideo = async (videoName) => {
        const response = await fetch(`${BACKEND_URL}/video/${videoName}`)

        if (response.ok) {
            const data = await response.json();
            console.log(data);
            data.groups = data.groups.filter((group) => group.length > 1);
            setVideo(data);
        }
        else {
            console.log("Error");
        }
    }

    return (
        <div className="w-1/5">
            <h1>Navigation</h1>
            <div>
                {metadata && metadata.map((videoName, index) => {
                    return (
                        <div
                            className="cursor-pointer bg-gray-200"
                            onClick={() => handleSelectVideo(videoName)}
                            key={index}
                        >
                            <p>{videoName}</p>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

export default SideBar;