import React, { useState } from "react"
import { useSessionContext } from "../SessionContext"


const ImageGallery = () => {
    const { video } = useSessionContext();
    return (
        <div className="w-4/5 text-center">
            {video && video.groups.map((group, idx1) => {
                return (
                    <div
                        key={idx1}
                        className={`group-container flex flex-wrap w-full ${idx1 % 2 ? "bg-blue-400" : "bg-gray-400"}
                                        p-[10px]`}
                    >
                        {group.map((frame, idx2) => {
                            const caption = frame.frame.split("/")[2];

                            return (
                                <div
                                    key={idx2}
                                    className={`frame-container w-[20%] ${frame.kept ? "border-[5px] border-green-400" : ""}`}
                                >
                                    <img src={`/Data/Newframe/${frame.frame}`} alt="Hello" />
                                    <p>
                                        {caption}
                                    </p>
                                </div>
                            )
                        })}
                    </div>
                )
            })}
        </div>
    )
}

export default ImageGallery;