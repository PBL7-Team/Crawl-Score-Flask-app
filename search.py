from rapidfuzz import process, fuzz

import os
import json

def get_attraction_info(directory_path):
    absolute_path = os.path.abspath(directory_path)
    if not os.path.isdir(absolute_path):
        print("Đường dẫn không tồn tại.")
        return {}
    
    attractions_dict = {}
    for filename in os.listdir(absolute_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for attraction in data:
                    attraction_name = attraction["attraction_name"]
                    if attraction_name not in attractions_dict:
                        attractions_dict[attraction_name] = {
                            "attraction_name_en": attraction["attraction_name"],
                            "attraction_name_vi": attraction["attraction_name_vi"],
                            "attraction_summary": attraction["attraction_summary"]
                        }
    return attractions_dict

def find_best_match(query, threshold=70):
    directory_path = 'Crawler_Here/Scrape_data/attraction'
    attractions_dict = get_attraction_info(directory_path)
    best_match = None
    best_score = 0
    best_key = None

    for key, value in attractions_dict.items():
        for name in (value['attraction_name_en'], value['attraction_name_vi']):
            score = fuzz.ratio(query, name)
            if score > best_score:
                best_score = score
                best_match = attractions_dict[value['attraction_name_en']]
                best_key = key

    if best_match and best_score >= threshold:
        matched_attraction = attractions_dict[best_key]
        return matched_attraction
    else:
        return None

def query_attraction(query):
    return find_best_match(query)