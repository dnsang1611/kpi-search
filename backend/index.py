from initialize import *
import functools

with open("/mnt/mmlab2024nas/visedit/AIC2024/code/JSON/asr_batch1_1.json", "r") as f:
    asr_data = json.load(f)

with open("/mnt/mmlab2024nas/visedit/AIC2024/code/JSON/asr_batch1_2.json", "r") as f:
    asr_data_2 = json.load(f)

asr_data = asr_data + asr_data_2

app = FastAPI(
    title="InferaSearch - MMLAB",
    description="This is the API we are using at HCMC AI Challenge, please do not use for other purposes.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frame", StaticFiles(directory=KEYFRAME_PATH), name="frame")
app.mount("/mapframe", StaticFiles(directory=MAPFRAME_PATH), name="mapframe")
app.mount("/metadata", StaticFiles(directory=METADATA_PATH), name="metadata")

class RequestMock:
    def __init__(self, body):
        self._body = body

    async def json(self):
        return self._body
    
def measure_time(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print('args:', args)
        print("kwargs: ", kwargs)
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} processed in {end_time - start_time} (s)")
        return result
    
    return wrapper

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content="<h1>InferaSearch API</h1><p>Welcome to the InferaSearch MMLAB API.</p>")

@app.post("/get_transcript")
@measure_time
async def get_transcript(image_name: str):
    result = next((item for item in asr_data if item.get("frame_end") == image_name), None)
    return result["text"]

@app.post("/text_search")
@measure_time
async def semantic_search(query: str = Form(...), topk: int = Form(...)):
    text_feat_arr = semantic_embedd.embed_text(query)
    topk_results = image_semantic_search_engine.search(text_feat_arr, topk)
    return topk_results

@app.post("/image_search")
@measure_time
async def image_search(query: List[str] = Form(...), topk: int = Form(...)):
    image_feats = []
    for image_url in query:
        if not image_url.startswith("http"):
            image_url = os.path.join(KEYFRAME_PATH, image_url.split("/", maxsplit=3)[-1])

        image_feat = semantic_embedd.embed_image(image_url)
        image_feats.append(image_feat)

    avg_image_feat = np.vstack(image_feats).mean(axis=0)
    topk_results = image_semantic_search_engine.search(avg_image_feat, topk)
    return topk_results

@app.post("/video_search")
@measure_time
async def video_search(query: str = Form(...), topk: int = Form(...)):
    text_feat_arr = video_text_embedd.get_text_embedding(query)
    topk_results = video_semantic_search_engine.search(text_feat_arr, topk)
    return topk_results

@app.post("/temporal_search")
@measure_time
async def normal_temporal_search(query: List[str] = Form(...), topk: int = Form(...)):
    '''We use trick in this function. Specifically, we represent each frame name as a number:
    batch_id (2 digits), video_id (3 digits), frame_id (5 digits); then we use numpy to determine
    which pairs are nearby. This trick is only used when the those constraints are satisfited. 
    If not, you will suffer from overflow in number, because np.int32 can only represent -2^63 -> 2^63
    '''
    assert len(query) >= 2, "Error: Number of queries < 2"
    
    # Get frames of each event
    pre_topk = 10000
    events_results = []

    for event in query:
        event_result = await semantic_search(event, pre_topk)
        events_results.append(event_result)

    # Convert frame_name to number
    events_frames = []
    events_scores = []
    for result in events_results:
        events_frames.append(np.array([frame_name_to_number(frame_item["frame"]) for frame_item in result], dtype=np.int64))
        events_scores.append(np.array([frame_item["score"] for frame_item in result]))

    # Calculate f1-scores and check adjacency
    frame_name_mats = []
    score_mats = []
    eps = 5 # Seconds
    fps = 30 # Default

    for i in range(len(query) - 1):
        frame_name_mat = events_frames[i + 1].reshape(1, -1) - events_frames[i].reshape(-1, 1)
        frame_name_mat = np.where((0 < frame_name_mat) & (frame_name_mat <= eps * fps), True, False)
        score_mat = calculate_f1(events_scores[i].reshape(-1, 1), events_scores[i + 1].reshape(1, -1))
        
        frame_name_mats.append(frame_name_mat)
        score_mats.append(score_mat)
    
    # Find sequences
    ids_1, ids_2 = np.where(frame_name_mats[0] == True)
    prev_seq_items = []
    
    for id_1, id_2, score in zip(ids_1, ids_2, score_mats[0][ids_1, ids_2]):
        prev_seq_items.append({
            "sequence": [id_1, id_2],
            "scores": [score]
        })

    for i in range(1, len(score_mats), 1):
        cur_frame_name_mat = frame_name_mats[i]
        cur_score_mat = score_mats[i]

        cur_seq_items = []
        for prev_seq_item in prev_seq_items:
            frame_id_1 = prev_seq_item["sequence"][-1]
            frame_ids_2 = np.where(cur_frame_name_mat[frame_id_1] == True)[0]
            
            for frame_id_2 in frame_ids_2:
                cur_seq_item = copy.deepcopy(prev_seq_item)
                cur_seq_item["sequence"].append(frame_id_2)
                cur_seq_item["scores"].append(cur_score_mat[frame_id_1, frame_id_2])
                cur_seq_items.append(cur_seq_item)
        
        prev_seq_items = cur_seq_items
        cur_seq_items = []
    
    # Calculate hmean
    for seq_item in prev_seq_items:
        seq_item["scores"] = harmonic_mean(seq_item["scores"])

    # Sort
    sorted_seq_items = sorted(prev_seq_items, key=lambda x: -x["scores"])

    # Convert number to frame_name
    final_results = []
    for seq_item in sorted_seq_items:
        for id, frame_id in enumerate(seq_item["sequence"]):
            final_results.append({
                "frame": number_to_frame_name(events_frames[id][frame_id]),
                "score": seq_item["scores"]
            })

    return final_results[:topk]

@app.post("/color_search")
@measure_time
async def color_search(query: List[str] = Form(...), topk: int = Form(...)):
    results = color_search_engine.search(query, topk)
    return results
    
@app.post("/ocr_search")
@measure_time
async def ocr_search(query: str = Form(...), topk: int = Form(...)):
    topk_results = ocr_search_engine.query(query, topk)
    for res in topk_results:
        res['frame'] += '.jpg'
    return topk_results

@app.post("/asr_search")
@measure_time
async def asr_search(query: str = Form(...), topk: int = Form(...)):
    asr_results = asr_search_engine.query(query, topk)
    formatted_results = []
    unique_frames = set()

    for result in asr_results:
        frame_start_path = result["frame_start"]
        frame_end_path = result["frame_end"]

        video_folder, start_frame = split_path(frame_start_path)
        _, end_frame = split_path(frame_end_path)
        video_folder_path = os.path.join(KEYFRAME_PATH, video_folder)

        start_frame_index = find_image_position(video_folder_path, start_frame)
        end_frame_index = find_image_position(video_folder_path, end_frame)

        if start_frame_index != -1 and end_frame_index != -1:
            for frame_number in range(start_frame_index, end_frame_index + 1):
                frame_name = natsorted(os.listdir(video_folder_path))[frame_number]
                frame_res_relative = os.path.join(video_folder, frame_name)

                if frame_res_relative not in unique_frames:
                    unique_frames.add(frame_res_relative)
                    formatted_results.append({"frame": frame_res_relative})
                    
    final_results = formatted_results[:topk]
    return final_results

@app.post("/object_search")
@measure_time
async def object_query(request: Request):
    body = await request.json()
    query_input = body['query_input']
    topk = body.get('topk', 10)
    results = obj_search_engine.search_image_with_iou(query_input, topk)
    return results

# @app.post("/pose_search")
# @measure_time
# async def pose_search(request: Request):
#     body = await request.json()
#     query_input = body['query_input']
#     topk = body.get('topk', 10)
#     pose_search_results = pose_search_engine.search(query_input, topk)
#     return pose_search_results

@app.post("/combine_search")
@measure_time
async def combine_search(request: Request):
    body = await request.json()
    query_list = body.get("query", [])
    methods = body.get("methods", [])
    topk = body.get("topk", 10)

    if len(query_list) != len(methods):
        raise HTTPException(status_code=400, detail="The length of queries and methods must be equal.")

    combined_results = {}
    tasks = []
    pre_topk = 100000

    async def search_and_update_results(method, query):
        # Main
        if method == "text":
            result = await semantic_search(query=query, topk=pre_topk)
            combined_results[method] = result
            return
        
        # Filter
        if method == "ocr":
            result = await ocr_search(query=query, topk=pre_topk)
        elif method == "asr":
            result = await asr_search(query=query, topk=pre_topk)
        # elif method == "sketch":
        #     result = await sketch_search(query=query, topk=pre_topk)
        elif method == "color":
            result = await color_search(query=query, topk=pre_topk)
        elif method == "object":
            object_body = {'query_input': query, 'topk': pre_topk}
            result = await object_query(RequestMock(object_body))
        else:
            raise HTTPException(status_code=400, detail=f"Unknown search method: {method}")

        combined_results[method] = [r["frame"] for r in result if "frame" in r]

    for method, query in zip(methods, query_list):
        if method == "object":
            object_query_format = query 
            tasks.append(search_and_update_results(method, object_query_format))
        else:
            tasks.append(search_and_update_results(method, query))

    await asyncio.gather(*tasks)

    shared_results = set.intersection(*[set(results) for method, results in combined_results.items() if method != "text"])
    final_results = [result for result in combined_results["text"] if result["frame"] in shared_results]
    return final_results[:topk]



@app.post("/rerank_search")
@measure_time
async def rerank_search(request: Request):

    body = await request.json()
    original_query = body.get('original_query')
    relevant_images = body['relevant_images']
    irrelevant_images = body['irrelevant_images']
    topk = body.get('topk', 10)

    base_dir = KEYFRAME_PATH
    feats_dir = IMG_SEM_FEAT_DIR

    def get_feature_vectors(images, directory):
        return [vec for img in images if (vec := get_feature_vector(directory, os.path.join(base_dir, img))) is not None]

    relevant_vectors = get_feature_vectors(relevant_images, feats_dir)
    irrelevant_vectors = get_feature_vectors(irrelevant_images, feats_dir)
    original_query_vector = semantic_embedd(original_query) if original_query else None
    modified_query_vector = rerank_images.reformulate(original_query_vector, relevant_vectors, irrelevant_vectors)
    reranked_results = image_semantic_search_engine.search(modified_query_vector, topk)
    return reranked_results

if __name__ == "__main__":
    uvicorn.run("index:app", host="0.0.0.0", port=7777, reload=False)