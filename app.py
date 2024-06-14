import json
from re import S
from flask import Flask, jsonify, request, send_file
import threading
from datetime import datetime
import os
import time
from Model_Here.auto_download_models import  dowwload_model
dowwload_model()

from recommend import recommend_system, get_new_contentbase_df
from search import query_attraction
from service_crawl import get_all_json_data, update_csv_with_json_data, start_crawl, stop_crawl, get_json_statistics, start_crawl_mode_2
from service_model import sentiment_analysis_all, fully_updated_sentiment_csv, export_synonyms_clusters
from dotenv import load_dotenv
from functools import wraps
from flask import Flask, request
from flask_apscheduler import APScheduler

app = Flask(__name__)

scheduler = APScheduler()

load_dotenv()


# Lấy các giá trị của các biến môi trường
API_KEY_1 = os.getenv("API_KEY_1")
API_KEY_2 = os.getenv("API_KEY_2")


crawl_thread = None
crawl_thread_mode_2 = None
crawl_starttime = None

sentiment_scoring_thread = None
sentiment_scoring_starttime = None

update_sentiment_thread = None

clusing_thread = None

content_base_thread = None

# test_variable = 0

def require_api_key(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('API-Key')
        if not api_key:
            return jsonify({'error': 'Unauthorized access!'}), 401
        # Kiểm tra xem API key có trong danh sách các keys hợp lệ không
        if api_key == API_KEY_1 or api_key == API_KEY_2:
            return func(*args, **kwargs)
        else:
            return jsonify({'error': 'Unauthorized access!'}), 401

    return decorated_function

def start_crawl_thread():
    with app.app_context():
        start_crawl()

def start_crawl_mode_2_thread():
    with app.app_context():
        start_crawl_mode_2()

def start_sentiment_scoring_thread():
    with app.app_context():
        try:
            sentiment_analysis_all()
            fully_updated_sentiment_csv()
            export_synonyms_clusters()
            get_new_contentbase_df()
            print("Hoàn tất tiến trình!")
        except Exception as e:
            print("Error :" + e)

def update_sentiment_csv_thread():
    with app.app_context():
        fully_updated_sentiment_csv()

def update_clustring_thread():
    with app.app_context():
        export_synonyms_clusters()

def caculate_content_base_thread():
    with app.app_context():
        get_new_contentbase_df()
        print("Hoàn tất tiến trình trích content base !")

@app.route('/caculate-content-base', methods=['GET'])
@require_api_key
def start_caculate_content_base_route():
    global content_base_thread

    if content_base_thread is None or not content_base_thread.is_alive():
        content_base_thread = threading.Thread(target=caculate_content_base_thread)

        content_base_thread.start()
        return jsonify({"message": "Content base caculate started."}), 200
    else:
        return jsonify({"message": "Content base caculate is already running."}), 400

@app.route('/json-files', methods=['GET'])
@require_api_key
def get_json_files():
    json_data = get_all_json_data()
    return jsonify(json_data)

@app.route('/update-backlog', methods=['GET'])
@require_api_key
def update_backlog():
    last_updated, new_json_amount, updated_json_amount = update_csv_with_json_data()
    return jsonify({
        "last_updated": last_updated,
        "new_json_amount": new_json_amount,
        "updated_json_amount": updated_json_amount
    }), 200

@app.route('/start-crawl', methods=['GET'])
@require_api_key
def start_crawl_route():
    global crawl_thread
    global crawl_starttime

    if crawl_thread is None or not crawl_thread.is_alive():
        crawl_thread = threading.Thread(target=start_crawl_thread)
        crawl_starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        crawl_thread.start()
        return jsonify({"message": "Crawler started."}), 200
    else:
        return jsonify({"message": "Crawler is already running."}), 400

@app.route('/start-crawl-mode-2', methods=['GET'])
@require_api_key
def start_crawl_mode_2_route():
    global crawl_thread_mode_2

    if crawl_thread_mode_2 is None or not crawl_thread_mode_2.is_alive():
        crawl_thread_mode_2 = threading.Thread(target=start_crawl_mode_2_thread)
        crawl_thread_mode_2.start()
        return jsonify({"message": "Crawler started."}), 200
    else:
        return jsonify({"message": "Crawler is already running."}), 400

@app.route('/get-crawl-info', methods=['GET'])
@require_api_key
def get_crawl_info():
    global crawl_starttime
    if crawl_starttime is not None:
        new_json_amount, updated_json_amount = get_json_statistics(crawl_starttime)
        return jsonify({
        "new_json_amount": new_json_amount,
        "updated_json_amount": updated_json_amount,
        "message": "Crawl Info received."
        }), 200
    else:
        return jsonify({"message": "Crawler has not started."}), 200

@app.route('/stop-crawl', methods=['GET'])
@require_api_key
def stop_crawl_route():
    stop_crawl()
    global crawl_starttime
    global crawl_thread
    if crawl_starttime is not None:
        new_json_amount, updated_json_amount = get_json_statistics(crawl_starttime)
        crawl_starttime = None
        crawl_thread = None
        return jsonify({
        "new_json_amount": new_json_amount,
        "updated_json_amount": updated_json_amount,
        "message": "Crawler stopped."
        }), 200
    else:
        return jsonify({"message": "Crawler has not started."}), 200


@app.route('/sentiment-caculate', methods=['GET'])
@require_api_key
def sentiment_caculate():
    global sentiment_scoring_thread
    global sentiment_scoring_starttime

    if sentiment_scoring_thread is None or not sentiment_scoring_thread.is_alive():
        sentiment_scoring_thread = threading.Thread(target=start_sentiment_scoring_thread)
        sentiment_scoring_starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sentiment_scoring_thread.start()
        return jsonify({"message": "Sentiment Scoring started."}), 200
    else:
        return jsonify({"message": "Sentiment Scoring is already running."}), 400
    # try:
    #     sentiment_analysis_all()
    #     return jsonify({"message": "Re-caculating Sentiment..."}), 200
    # except Exception as e:
    #     return jsonify({"message": "Sentiment analysis failed to start! " + e}), 400

@app.route('/update-sentiment-csv', methods=['GET'])
@require_api_key
def update_sentiment_csv():
    global update_sentiment_thread
    if update_sentiment_thread is None or not update_sentiment_thread.is_alive():
        update_sentiment_thread = threading.Thread(target=update_sentiment_csv_thread)
        update_sentiment_thread.start()
        return jsonify({"message": "Update Sentiment-csv started."}), 200
    else:
        return jsonify({"message": "Update Sentiment-csv is already running."}), 400

@app.route('/download-score-csv', methods=['GET'])
@require_api_key
def download_score_csv():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(current_directory, 'sentiment_value.csv')
    # Kiểm tra xem tệp CSV tồn tại không
    if not os.path.isfile(CSV_PATH):
        return jsonify({'message': 'CSV file not found'}), 404

    # Gửi tệp CSV nếu mã API hợp lệ và tệp tồn tại
    return send_file(CSV_PATH, as_attachment=True)

@app.route('/get-synonyms-clusters', methods=['GET'])
@require_api_key
def update_synonyms_clusters():
    global clusing_thread
    if clusing_thread is None or not clusing_thread.is_alive():
        clusing_thread = threading.Thread(target=update_clustring_thread)
        clusing_thread.start()
        return jsonify({"message": "Update Synonyms started."}), 200
    else:
        return jsonify({"message": "Update Synonyms is already running."}), 400
    # try:
    #     vi_clusters = export_synonyms_clusters()
    #     return jsonify(vi_clusters)
    # except FileNotFoundError as e:
    #     return jsonify({"error": str(e)}), 404
    # except ValueError as e:
    #     return jsonify({"error": str(e)}), 400
    # except Exception as e:
    #     return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500
    
    
@app.route('/recommend', methods=['GET'])
@require_api_key
def recommend():
    msg = recommend_system(request.args.get('message'))
    return jsonify({
        "message": msg,
    }), 200
    
from rapidfuzz import process, fuzz

import os
import json

def get_attraction_info(directory_path):
    print(directory_path)
    attractions_dict = {}
    for filename in os.listdir(directory_path):
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
    current_directory = os.getcwd()
    attractions_dict = get_attraction_info(os.path.join(current_directory, 'Crawler_Here', 'Scrape_Data', 'attraction'))
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

    
@app.route('/search', methods = ['GET'])
@require_api_key
def search_attraction():
    msg = find_best_match(request.args.get('query'))
    return jsonify({
        "message": msg,
    }), 200    

  
@app.route('/test-api', methods=['GET'])
def test():
    return jsonify({
        "message": "API is working!",
    }), 200
    
    
@app.route('/cleanup', methods=['GET'])
def cleanup_files():
    
    current_directory = os.getcwd()
    J_FOLDER = os.path.join(current_directory, 'Crawler_Here', 'Scrape_Data', 'attraction')
    deleted_files_count = 0
    delete_path = []
    for filename in os.listdir(J_FOLDER):
        file_path = os.path.join(J_FOLDER, filename)

        if "Undefined" in filename:
            delete_path.append(file_path)
            deleted_files_count += 1
            continue
        
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                for attraction in data:
                    location = attraction.get('location', [])
                    
                    if not any("Việt Nam" in loc for loc in location):
                        print(f'Xóa file {file_path} vì không chứa "Việt Nam" trong location.')
                        delete_path.append(file_path)
                        deleted_files_count += 1
                        break 
                                
                    name = attraction.get('attraction_name', '')
                    keywords = ['tour', 'tours', 'travel', 'trip', 'motobike', 'bike', 'express']

                    if any(keyword in name.lower() for keyword in keywords):
                        delete_path.append(file_path)
                        deleted_files_count += 1
                        break 
                    
    for path in delete_path:
        try:
            os.remove(path)
            print(f'Đã xóa file: {path}')
        except OSError as e:
            print(f'Lỗi khi xóa file {path}: {e}')

                    
    return jsonify({"deleted_files_count": deleted_files_count})
    
@app.route('/get-crawl-calc-info', methods=['GET'])
def get_crawl_calc_info():
    current_directory = os.getcwd()
    J_FOLDER = os.path.join(current_directory, 'Crawler_Here', 'Scrape_Data', 'attraction')
    results = []

    for file_name in os.listdir(J_FOLDER):
        if file_name.endswith('.json'):
            file_path = os.path.join(J_FOLDER, file_name)
            
            # Load the JSON data
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                
                # Initialize counters
                total_review_count = 0
                total_review_count_non_calc = 0
                
                for entry in data:
                    attraction_name = entry.get('attraction_name', 'N/A')
                    attraction_name_vi = entry.get('attraction_name_vi', 'N/A')
                    attraction_summary = entry.get('attraction_summary', 'N/A')
                    
                    reviews = entry.get('reviews', [])
                    total_review_count += len(reviews)
                    
                    caculated = entry.get('caculated', False)
                    if not caculated:
                        total_review_count_non_calc += len(reviews)
                    
                result = {
                    'file': file_name,
                    'attraction_name': attraction_name,
                    'attraction_name_vi': attraction_name_vi,
                    'attraction_summary': attraction_summary,
                    'review_count': total_review_count,
                    'review_count_non_calc': total_review_count_non_calc
                }
                results.append(result)
                
    return jsonify(results)

@scheduler.task('cron', id='my_job', hour=7, minute=0)
def crawl_new_data_job():
    global crawl_thread
    global crawl_starttime

    if crawl_thread is None or not crawl_thread.is_alive():
        crawl_thread = threading.Thread(target=start_crawl_thread)
        crawl_starttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        crawl_thread.start()
        print("Crawler started.")
    else:
        print("Crawler is already running.")

@scheduler.task('cron', id='my_job_2', hour=19, minute=0)
def update_old_data_job():
    global crawl_thread_mode_2

    if crawl_thread_mode_2 is None or not crawl_thread_mode_2.is_alive():
        crawl_thread_mode_2 = threading.Thread(target=start_crawl_mode_2_thread)
        crawl_thread_mode_2.start()
        print("Crawler started.")
    else:
        print("Crawler is already running.")


# @app.route('/test-scheduler', methods=['GET'])
# def test_scheduler():
#     global test_variable
#     return jsonify({
#         "message": test_variable,
#     }), 200

# bước 1: Crawl data bằng start-crawl
# bước 2: Thực hiện sentiment caculate (để cập nhật score vào mỗi file json), sử dụng model entity extraction + sentiment analysis
# bước 3: Thực hiện update sentiment csv
# bước 4: Thực hiện download score csv
# bước 5: Thực hiện get synonyms clusters (trong đó bao gồm update entity translate, update file vi_cluster và download vi_cluster)
# bước 6: Thực hiện tạo mới content_base_score_df.csv dựa trên 2 file trên

# bước 1.2: Crawl data bằng mode 2 (để cập nhật dữ liệu review từ địa điểm cũ)
if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(host="0.0.0.0", port=8080)
