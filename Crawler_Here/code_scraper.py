import requests
import json
from pprint import pprint
import threading
import os
from difflib import SequenceMatcher
from Crawler_Here.reading_info_attraction import read_html_attraction
from Crawler_Here.reading_info_hotel import read_html_hotel
from Crawler_Here.reading_info_restaurant import read_html_restaurant

import time
import random

SERVICE_ACC  = 'Bach2k2_1Ygdh'
SERVICE_PASS = 'Bach20021234'

# Global flag for stopping the crawl
stop_flag = threading.Event()

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
    response_path = os.path.join(current_directory, 'response.json')
    # Check if request was successful
    if response.status_code == 200:
        # Create a file named "response.json" and write the content of response.json() to it.
        with open(response_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=4)
        print("File 'response.json' created successfully.")
    else:
        print(f"Failed to create file. Status code: {response.status_code}")

def scrape_tourist_destination_data(url, file_path):

    global stop_flag
    if stop_flag.is_set():
        print("Crawl stopped.")
        return 
    print("Crawling " + url + " ...")

    crawl_1_url(url)
    new_links = []
    location = []
    # if "Hotel_Review" in url:
    #     new_links = read_html_hotel()
    if "Attraction_Review" in url:
        new_links, location, url_next, _ = read_html_attraction()
    is_vietnam = True
    if len(location) == 0 or ("Vietnam" not in location and 'Việt Nam' not in location):
        is_vietnam = False
        new_links = []
    # elif "Restaurant_Review" in url:
    #     new_links = read_html_restaurant()
    used_urls = add_used_urls(url)
    if len(new_links) > 0:
        new_links = remove_used_urls(new_links, used_urls)
    updated_urls_file(file_path, new_links, used_urls)
    # next_url = find_most_similar_url(url, file_path)
    
    if url_next != "" and check_review_page(url_next) == False and is_vietnam == True:
        next_url = url_next
    else:
        next_url = get_random_url(file_path)
    # time.sleep(3)
    scrape_tourist_destination_data(next_url, file_path)

# crawl_1_url('https://www.tripadvisor.com/Attraction_Review-g293923-d1968469-Reviews-Halong_Bay-Halong_Bay_Quang_Ninh_Province.html')

def add_used_urls(url):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    url_list_directory = os.path.join(current_directory, 'url_list')
    file_name = "used_urls.txt"
    file_path = os.path.join(url_list_directory, file_name)
    url_list = []
    url_list.append(url)
    used_urls = updated_urls_file(file_path, url_list) 

    return used_urls

def remove_used_urls(original_urls, used_urls):
    stripped_original_urls = [url.strip() for url in original_urls]
    stripped_used_urls = [url.strip() for url in used_urls]

    for url in stripped_used_urls:
        if url in stripped_original_urls:
            stripped_original_urls.remove(url)
    
    return  [link + '\n' for link in stripped_original_urls]

def check_review_page(link):
    # Tách link thành các phần bằng dấu "-"
    parts = link.split("-")
    try:
        # Duyệt qua các phần để tìm phần chứa "or"
        for part in parts:
            if part.startswith("or") and len(part) <= 5:
                # Lấy chỉ số của "or" và loại bỏ chữ "or" để lấy số
                number = part[2:]
                # Kiểm tra số và trả về True nếu lớn hơn 100
                return int(number) > 90
    except:
        return True
    # Trả về False nếu không tìm thấy số lớn hơn 100
    return False

def process_links(links):
    processed_links = []
    seen_links = set()

    for link in links:
        # Chỉ giữ lại các đường link cho dòng subtext "Hotel_Review", "Attraction_Review" hoặc "Restaurant_Review"
        if check_review_page(link) == True:
            continue
        # if "Hotel_Review" in link or "Attraction_Review" in link or "Restaurant_Review" in link:
        if "Attraction_Review" in link:
            # Xóa phần "#REVIEWS" khỏi đường link
            link = link.split('#')[0]

            # Nếu đường link bắt đầu bằng dấu "/", thêm string "https://www.tripadvisor.com" vào trước đường link đó
            if link.startswith("/"):
                link = "https://www.tripadvisor.com" + link

            # Kiểm tra và loại bỏ những đường link bị trùng lặp
            if link not in seen_links:
                processed_links.append(link)
                seen_links.add(link)

    return processed_links

def updated_urls_file(input_file, new_links = [], deleted_url = []):
    # Đọc nội dung của file input và lọc các dòng không chứa từ "review"
    with open(input_file, 'r', encoding="utf-8") as file:
        lines = file.readlines()
    
    new_links_with_newline = ['\n' + link for link in new_links]
    # Nối new_links vào lines
    lines.extend(new_links_with_newline)

    if len(new_links) > 0:
        lines.extend(new_links_with_newline)

    filtered_lines = process_links(lines)

    if len(deleted_url) > 0:
        filtered_lines = remove_used_urls(filtered_lines,deleted_url)


    # Ghi lại các dòng đã lọc vào file mới
    with open(input_file, 'w', encoding="utf-8") as file:
        file.writelines(filtered_lines)
    
    return filtered_lines

def get_first_url(file_path):
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        return first_line

def get_random_url(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if not lines:
            return None  # Trả về None nếu file trống
        random_line = random.choice(lines).strip()
        return random_line

def get_last_url(file_path):
  """
  Reads the last line of a file and returns the content as a URL, assuming one URL per line.

  Args:
      file_path (str): The path to the text file containing URLs.

  Returns:
      str: The last URL found in the file, or None if the file is empty or an error occurs.
  """

  try:
    with open(file_path, 'r') as file:
      # Read lines one by one using a loop
      lines = file.readlines()
      if lines:  # Check if there are any lines in the file
        return lines[-1].strip()  # Return the last line (stripped of whitespaces)
      else:
        return None  # Return None if the file is empty
  except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
    return None
  except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    return None

def find_most_similar_url(url, file_path):
    max_similarity = 0
    most_similar_url = None
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            candidate_url = line.strip()
            similarity = SequenceMatcher(None, url, candidate_url).ratio()
            if similarity > max_similarity and similarity < 1:
                max_similarity = similarity
                most_similar_url = candidate_url
    
    return most_similar_url

def crawl_all():
    # threads = []
    global stop_flag
    stop_flag.clear()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    url_list_directory = os.path.join(current_directory, 'review-url')
    file_name = f"attraction.txt"
    file_path = os.path.join(url_list_directory, file_name)
    updated_urls_file(file_path)
    # url = get_first_url(file_path)
    url = get_random_url(file_path)
    while url and not stop_flag.is_set():
        try:
            url = get_random_url(file_path)
            # url = r"https://www.tripadvisor.com/Attraction_Review-g298085-d6612108-Reviews-or60-Dragon_Bridge-Da_Nang.html"
            scrape_tourist_destination_data(url, file_path)
        except Exception as e:
            print("Xuất hiện lỗi trong khi crawl, 90s tự động khởi động lại... "+ e)
            if not stop_flag.is_set():
                time.sleep(90)
                
def stop_crawl():
    global stop_flag
    stop_flag.set()

def crawl_specific_place(url):
    crawl_1_url(url)
    new_links, location, url_next, _ = read_html_attraction()
    for i in range(9):
        crawl_1_url(url_next)
        new_links, location, url_next, _ = read_html_attraction()
        if url_next == "" or url_next is None:
            break

# crawl_specific_place(r"https://www.tripadvisor.com/Attraction_Review-g298085-d8090733-Reviews-Han_River_Bridge-Da_Nang.html")

# crawl_all()

# crawl_1_url('https://www.tripadvisor.com/Restaurant_Review-g1535794-d10495220-Reviews-Coc_Cafe_Tra_Vinh-Tra_Vinh_Tra_Vinh_Province_Mekong_Delta.html')
# https://www.tripadvisor.com/Attraction_Review-g298085-d12912951-Reviews-Ba_Na_Cable_Car-Da_Nang.html
# https://www.tripadvisor.com/Attraction_Review-g298085-d8115500-Reviews-DHC_Marina-Da_Nang.html
# https://www.tripadvisor.com/Attraction_Review-g298085-d456220-Reviews-Non_Nuoc_Beach-Da_Nang.html
# https://www.tripadvisor.com/Attraction_Review-g298085-d6963730-Reviews-Hoa_Nghiem_Cave-Da_Nang.html
# https://www.tripadvisor.com/Attraction_Review-g298085-d7043562-Reviews-Sun_Wheel-Da_Nang.html
# https://www.tripadvisor.com/Attraction_Review-g298085-d8090733-Reviews-Han_River_Bridge-Da_Nang.html