import os
import json
import csv
from datetime import datetime
from Crawler_Here.code_scraper import crawl_all, stop_crawl
from Crawler_Here.code_scraper_mode_2 import crawl_all_mode_2

current_directory = os.path.dirname(os.path.abspath(__file__))
JSON_FOLDER = os.path.join(current_directory, 'Crawler_Here', 'Scrape_Data', 'attraction')
CSV_FILE = os.path.join(current_directory, 'backlog.csv')

def get_all_json_data():
    json_files = [f for f in os.listdir(JSON_FOLDER) if f.endswith('.json')]
    json_data = []

    for file_name in json_files:
        file_path = os.path.join(JSON_FOLDER, file_name)
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            json_data.append(data)

    return json_data


def create_csv_if_not_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Last Updated", "New JSON amount", "Updated JSON amount"])
            writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0, 0])

def update_csv_with_json_data():
    create_csv_if_not_exists()
    
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        rows = list(reader)
    
    if rows:
        last_row = rows[-1]
        last_updated = datetime.strptime(last_row[0], '%Y-%m-%d %H:%M:%S')
    else:
        last_updated = datetime.min

    new_json_amount = 0
    updated_json_amount = 0
    now = datetime.now()

    for file_name in os.listdir(JSON_FOLDER):
        if file_name.endswith('.json'):
            file_path = os.path.join(JSON_FOLDER, file_name)
            file_stat = os.stat(file_path)
            creation_time = datetime.fromtimestamp(file_stat.st_ctime)
            modification_time = datetime.fromtimestamp(file_stat.st_mtime)

            if creation_time > last_updated:
                new_json_amount += 1
            elif modification_time > last_updated:
                updated_json_amount += 1

    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([now.strftime('%Y-%m-%d %H:%M:%S'), new_json_amount, updated_json_amount])
    
    return [last_updated, new_json_amount, updated_json_amount]

def get_json_statistics(start_time):
    # Ensure start_time is a datetime object
    if isinstance(start_time, str):
        try:
            # Adjust the format string to match your date string format if necessary
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            raise ValueError("start_time string is not in the correct format") from e

    new_json_amount = 0
    updated_json_amount = 0
    now = datetime.now()

    for file_name in os.listdir(JSON_FOLDER):
        if file_name.endswith('.json'):
            file_path = os.path.join(JSON_FOLDER, file_name)
            file_stat = os.stat(file_path)
            creation_time = datetime.fromtimestamp(file_stat.st_ctime)
            modification_time = datetime.fromtimestamp(file_stat.st_mtime)

            if creation_time > start_time:
                new_json_amount += 1
            elif modification_time > start_time:
                updated_json_amount += 1

    return new_json_amount, updated_json_amount

def start_crawl():
    return crawl_all()

def stop_crawl_service():
    return stop_crawl()

def start_crawl_mode_2():
    return crawl_all_mode_2()
# start_crawl()