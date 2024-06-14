import os
import json
import re

def get_crawl_calc_info():
    # Assuming current directory is set to where the JSON files are located
    current_directory = os.getcwd()
    J_FOLDER = os.path.join(current_directory, 'Crawler_Here', 'Scrape_Data', 'attraction')

    results = []

    for file_name in os.listdir(J_FOLDER):
        if file_name.endswith('.json'):
            file_path = os.path.join(J_FOLDER, file_name)
            
            # Load the JSON data
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                
                # Extract required details
                for entry in data:
                    attraction_name = entry.get('attraction_name', 'N/A')
                    attraction_name_vi = entry.get('attraction_name_vi', 'N/A')
                    attraction_summary = entry.get('attraction_summary', 'N/A')
                    
                    reviews = entry.get('reviews', [])
                    review_count = len(reviews)
                    
                    review_count_non_calc = sum(1 for review in reviews if isinstance(review, dict) and not review.get('calculated', False))
                    
                    result = {
                        'file': file_name,
                        'attraction_name': attraction_name,
                        'attraction_name_vi': attraction_name_vi,
                        'attraction_summary': attraction_summary,
                        'review_count': review_count,
                        'review_count_non_calc': review_count_non_calc
                    }
                    results.append(result)
    print(results)
    
get_crawl_calc_info()