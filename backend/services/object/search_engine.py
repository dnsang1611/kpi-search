import json
import concurrent.futures
import time
from collections import Counter
import os

class ObjectSearchEngine:
    
    def __init__(self, json_file_path: str, sel_keyframe_dir: str = None):
        # Get all features
        with open(json_file_path, 'r') as file:
            features = json.load(file)

        if sel_keyframe_dir:
            # Get features of selected frames
            new_features = {}
            for video_file in sorted(os.listdir(sel_keyframe_dir)):
                with open(os.path.join(sel_keyframe_dir, video_file), "r") as rf:
                    groups = json.load(rf)

                    for group in groups:
                        frame_name = group[-1]["frame"]
                        new_features[frame_name] = features[frame_name]
            
            features = new_features

        self.data = self.get_inverted_index(features)

    def get_inverted_index(self, features):
        inverted_index = {}

        for frame_name, obj in features.items():
            for cls_name, bboxes in obj.items():
                if cls_name not in inverted_index:
                    inverted_index[cls_name] = {}
                
                inverted_index[cls_name][frame_name] = bboxes
        
        return inverted_index
    
    @staticmethod
    def calculate_iou(box1, box2):
        """
        Calculate the Intersection over Union (IoU) of two bounding boxes.
        """
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[0] + box1[2], box2[0] + box2[2])
        y2 = min(box1[1] + box1[3], box2[1] + box2[3])

        intersection_area = max(0, x2 - x1) * max(0, y2 - y1)
        box1_area = box1[2] * box1[3]
        box2_area = box2[2] * box2[3]

        if box1_area + box2_area - intersection_area == 0:
            return 0
        iou = intersection_area / float(box1_area + box2_area - intersection_area)
        return iou

    def process_bbox_with_iou(self, query):
        """
        Process a single bbox.
        """
        results = {}
        query_box = [query['x'], query['y'], query['w'], query['h']]
        query_label = query['label'] #?

        if query_label in self.data:
            for frame, bboxes in self.data[query_label].items():
                max_iou_for_frame = 0
                for bbox in bboxes:
                    iou = self.calculate_iou(query_box, bbox)
                    max_iou_for_frame = max(max_iou_for_frame, iou)
                if max_iou_for_frame > 0:
                    if frame not in results:
                        results[frame] = {}
                    results[frame][query_label] = max_iou_for_frame
        return results

    def search_image_with_iou(self, query_input, topk=10):
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_bbox_with_iou, query) for query in query_input]
            for future in concurrent.futures.as_completed(futures):
                bbox_results = future.result()
                for frame, label_iou in bbox_results.items():
                    if frame not in results:
                        results[frame] = label_iou
                    else:
                        results[frame].update(label_iou)

        all_labels = {query['label'] for query in query_input}
        filtered_results = {frame: ious for frame, ious in results.items() if all_labels.issubset(ious)}
        final_scores = {frame: sum(ious.values()) for frame, ious in filtered_results.items()}
        sorted_results = [{'frame': frame, 'IOU': iou} for frame, iou in sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:topk]]
        return sorted_results

    def process_bbox_with_comparision(self, query):
        """
        Process a single bbox.
        """
        results = {}
        query_box = [query['x'], query['y'], 
                     query['x'] + query['w'], 
                     query['y'] + query['h']]
        query_label = query['label']
        query_area = query['w'] * query['h']

        if query_label in self.data:
            for frame, bboxes in self.data[query_label].items():
                results[frame] = -1
                for bbox in bboxes: # These bboxes should be sorted in descending order by area
                    x1, y1, x2, y2 = bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]
                    # Check if the bbox is in 
                    if (x1 >= query_box[0] and x2 <= query_box[2] and 
                        y1 >= query_box[1] and y2 <= query_box[3]):
                        results[frame] = max(results[frame], bbox[2] * bbox[3] / query_area)
                if results[frame] <= 0.5: del results[frame]

        return results

    def search_image_with_comparision(self, query_input, topk=10, threshold=None):
        n_objs = len(query_input)
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_bbox_with_comparision, query) for query in query_input]
            for future in concurrent.futures.as_completed(futures):
                bbox_results = future.result()
                for frame, label_iou in bbox_results.items():
                    if frame not in results:
                        results[frame] = [label_iou, 1]
                    else:
                        results[frame][0] += label_iou
                        results[frame][1] += 1
        
        # all_labels = {query['label'] for query in query_input}
        # filtered_results = {frame: ious for frame, ious in results.items() if all_labels.issubset(ious)} ?
        # final_scores = {frame: sum(ious.values()) for frame, ious in filtered_results.items()}
        # print(results)
        sorted_results = [{'frame': frame, 'IOU': iou_cnt_pair[0]} 
                          for frame, iou_cnt_pair in sorted(results.items(), key=lambda x: x[1][0], reverse=True)[:topk]
                          if iou_cnt_pair[1] == n_objs]
        return sorted_results
    
# Example Usage
if __name__ == '__main__':
    retrieval = ObjectSearchEngine('../../JSON/inverted_file.json')
    query_input = [
        {'x': 0.3024, 'y': 0.1845, 'w': 0.0247, 'h': 0.0554, 'label': 'traffic light'},
        # {'x': 0.7295, 'y': 0.4383, 'w': 0.0114, 'h': 0.0505, 'label': 'dog'},
        # {'x': 0.7295, 'y': 0.4383, 'w': 0.0114, 'h': 0.0505, 'label': 'traffic light'}
    ]

    topk = 5  

    n_loops = 1000
    total_time = 0
    for i in range(n_loops):
        start = time.time()
        results = retrieval.search_image_with_comparision(query_input, topk)
        # results = retrieval.search_image_with_iou(query_input, topk)
        total_time += time.time() - start
        
    print(f'Avg processing time: {total_time / n_loops} s')

    for result in results:
        print(result)