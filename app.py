from flask import Flask, jsonify, request, send_file
import threading
from datetime import datetime
import os
import time
from Model_Here.auto_download_models import  dowwload_model

dowwload_model()

from recommend import recommend_system
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
        sentiment_analysis_all()

@app.route('/json-files', methods=['GET'])
@require_api_key
def get_json_files():
    json_data = get_all_json_data()
    return jsonify(json_data)

@app.route('/update-backlog', methods=['POST'])
@require_api_key
def update_backlog():
    last_updated, new_json_amount, updated_json_amount = update_csv_with_json_data()
    return jsonify({
        "last_updated": last_updated,
        "new_json_amount": new_json_amount,
        "updated_json_amount": updated_json_amount
    }), 200

@app.route('/start-crawl', methods=['POST'])
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

@app.route('/start-crawl-mode-2', methods=['POST'])
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

@app.route('/stop-crawl', methods=['POST'])
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


@app.route('/sentiment-caculate', methods=['POST'])
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

@app.route('/update-sentiment-csv', methods=['POST'])
@require_api_key
def update_sentiment_csv():
    fully_updated_sentiment_csv()
    return jsonify({"message": "Update Sentiment CSV completed."}), 200

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
def get_synonyms_clusters():
    try:
        vi_clusters = export_synonyms_clusters()
        return jsonify(vi_clusters)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500
    
    
@app.route('/recommend', methods=['GET'])
@require_api_key
def recommend():
    msg = recommend_system(request.args.get('message'))
    return jsonify({
        "message": msg,
    }), 200
    
    
@app.route('/search', methods = ['GET'])
@require_api_key
def search_attraction():
    msg = query_attraction(request.args.get('query'))
    return jsonify({
        "ok": msg,
    }), 200
    
@app.route('/test-api', methods=['GET'])
def test():
    return jsonify({
        "message": "API is working!",
    }), 200
    
@scheduler.task('interval', id='my_job', seconds=10)
def my_job():
    print('This job is executed every 10 seconds.')
    time.sleep(8)
    print("Hello")

# bước 1: Crawl data bằng start-crawl
# bước 2: Thực hiện sentiment caculate (để cập nhật score vào mỗi file json), sử dụng model entity extraction + sentiment analysis
# bước 3: Thực hiện update sentiment csv
# bước 4: Thực hiện download score csv
# bước 5: Thực hiện get synonyms clusters (trong đó bao gồm update entity translate, update file vi_cluster và download vi_cluster)

# bước 1.2: Crawl data bằng mode 2 (để cập nhật dữ liệu review từ địa điểm cũ)
if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='localhost', port=8080)
