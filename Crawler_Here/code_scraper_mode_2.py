import requests
import json
from pprint import pprint
import threading
import os
from difflib import SequenceMatcher
from Crawler_Here.reading_info_attraction import read_html_attraction
# from reading_info_hotel import read_html_hotel
# from reading_info_restaurant import read_html_restaurant
import time
import random
import math

SERVICE_ACC  = 'ndst1_oDWXL'
SERVICE_PASS = '9r9ym8bRuqCN3d'

def crawl_1_url(url):
    payload = {
        'source': 'universal',
        'url': url,
        'user_agent_type': 'desktop',
        'geo_location': 'United States'
    }

    # Get response.
    response = requests.request(
        'POST',
        'https://realtime.oxylabs.io/v1/queries',
        auth=(SERVICE_ACC, SERVICE_PASS),
        json=payload
    )
    # Lấy đường dẫn của thư mục hiện tại
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Kết hợp với tên file để tạo đường dẫn đầy đủ
    response_path = os.path.join(current_directory, 'response2.json')
    # Check if request was successful
    if response.status_code == 200:
        # Create a file named "response.json" and write the content of response.json() to it.
        with open(response_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)
        print("File 'response2.json' created successfully.")
    else:
        print(f"Failed to create file. Status code: {response.status_code}")

def crawl_all_mode_2():
    current_directory = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa chương trình đang chạy
    scrape_directory = os.path.join(current_directory, "Scrape_Data")  # Kết hợp với tên thư mục chứa model
    attraction_directory = os.path.join(scrape_directory, "attraction")
    # Kiểm tra xem thư mục tồn tại không
    if os.path.exists(attraction_directory):
        # Lặp qua tất cả các file trong thư mục
        for filename in os.listdir(attraction_directory):
            # Kiểm tra nếu là file JSON
            if filename.endswith(".json"):
                # Đường dẫn đầy đủ của file
                file_path = os.path.join(attraction_directory, filename)
                # Đọc nội dung của file JSON
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                urls_need, need_deleted, review_increase = get_urls_for_new_reviews(data)
                if need_deleted == True:
                    os.remove(file_path)
                    continue
                if review_increase <= len(urls_need):
                    for url in reversed(urls_need):
                        crawl_1_url(url)
                        read_html_attraction(html_path = r"format2.html", json_file = 'response2.json')
                else:
                    url = urls_need[0]
                    for i in range(review_increase):
                        crawl_1_url(url)
                        new_links, location, url, _ = read_html_attraction(html_path = r"format2.html", json_file = 'response2.json') #url thực chất là url_next


def process_json_data(json_data):
    # Lấy list 'location' của dict đầu tiên
    location = json_data[-1]['location'] if json_data else []

    # Lấy giá trị 'review_amount' của dict cuối cùng
    review_amount = json_data[-1]['review_amount'] if json_data else 0

    # Tạo list 'urls' từ giá trị 'url' của tất cả dict và lọc đi các url bị trùng
    urls = []
    seen_urls = set()
    for item in json_data:
        url = item['url']
        if url not in seen_urls:
            seen_urls.add(url)
            urls.append(url)

    attraction_name = json_data[-1]['attraction_name'] if json_data else 'N/A'

    return location, review_amount, urls, attraction_name

def get_urls_for_new_reviews(json_data):
    need_deleted = False
    urls = []
    location, review_amount, urls, attraction_name = process_json_data(json_data)
    if review_amount == 0 or ("Vietnam" not in location and 'Việt Nam' not in location) or attraction_name == 'N/A':
        need_deleted = True
        return None, need_deleted
    first_urls = urls[0]
    crawl_1_url(first_urls)
    _, location, _, new_review_amount = read_html_attraction(html_path = r"format2.html", json_file = 'response2.json',saved=False)
    review_increase = math.ceil((new_review_amount - review_amount)/10)
    if review_increase <= len(urls):
        urls_need = urls[:review_increase]
    else:
        urls_need = urls

    return urls_need, need_deleted, review_increase

# print(math.ceil((25 - 23)/10))

# def get_first_n_urls(url_list, n):
#     return url_list[:n]

# # Ví dụ sử dụng
# urls = [
#     "https://example.com/1",
#     "https://example.com/2",
#     "https://example.com/3",
#     "https://example.com/4",
#     "https://example.com/5"
# ]

# n = 0
# first_n_urls = get_first_n_urls(urls, n)
# print(first_n_urls)

# crawl_all()