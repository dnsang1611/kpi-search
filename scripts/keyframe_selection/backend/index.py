from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import os
import json

app = FastAPI()

# Global variables
groups_dir = "/mnt/mmlab2024nas/visedit/AIC2024/code/Script/keyframe_selection/backend/db/videos_groups"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/metadata")
def get_metadata():
    video_names = [video_file.split(".")[0] for video_file in  sorted(os.listdir(groups_dir))]
    return video_names

@app.get("/video/{video_name}")
def get_video(video_name: str):
    with open(os.path.join(groups_dir, video_name + ".json"), "r") as rf:
        video_groups = json.load(rf)

    return {"name": video_name, "groups": video_groups} 

if __name__ == "__main__":
    uvicorn.run("index:app", host="0.0.0.0", port=7778, reload=False)