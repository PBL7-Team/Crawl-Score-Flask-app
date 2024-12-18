import os
import json
import csv
import numpy as np
import pandas as pd
from datetime import datetime
from Model_Here.keyphrase import TextEntities_Score, caculate_average_dict
from Model_Here.synonyms_prediction import synonyms_matrix, cluster_words
from Crawler_Here.translate_tool import final_translate_text
import math

current_directory = os.path.dirname(os.path.abspath(__file__))
J_FOLDER = os.path.join(current_directory, 'Crawler_Here', 'Scrape_Data', 'attraction')

def get_json_file_paths(JSON_FOLDER = J_FOLDER):
    json_file_paths = []
    for root, dirs, files in os.walk(JSON_FOLDER):
        for file in files:
            if file.endswith('.json'):
                json_file_paths.append(os.path.join(root, file))
    return json_file_paths

def days_difference(date_str):
    # Loại bỏ từ "Written "
    cleaned_date_str = date_str.replace("Written ", "")
    
    # Chuyển đổi chuỗi ngày tháng thành đối tượng datetime
    date_obj = datetime.strptime(cleaned_date_str, "%B %d, %Y")
    
    # Lấy thời gian hiện tại
    now = datetime.now()
    
    # Tính số ngày cách biệt
    difference = now - date_obj
    return difference.days

def adjust_dict_value(my_dict, A):
    if A <= 30:
        factor = 2
    elif 30 < A <= 180:
        factor = 1.5
    elif 180 < A <= 730:
        factor = 1
    else:
        factor = 0.5
    
    adjusted_dict = {key: [value * factor for value in values] for key, values in my_dict.items()}
    return adjusted_dict, factor

def remove_trailing_phrases(text):
    phrases = ["Đọc thêm", "Read More", "đọc thêm", "read more", "Read more", "Đọc Thêm", "Xem thêm", "Xem"]
    
    for phrase in phrases:
        if text.endswith(phrase):
            text = text[:len(text) - len(phrase)].rstrip()
            break
            
    return text

def process_json_file(json_path):
    temp_i = 0
    print("Reading this file...  " + json_path)
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if not data or not isinstance(data, list) or not isinstance(data[0], dict):
        print("Finish editing this file :" + json_path)
        return
    
    first_dict = data[0]
    if 'location' not in first_dict or not isinstance(first_dict['location'], list):
        print("Finish editing this file  :" + json_path)
        return
    
    if not first_dict['location'] or ('Việt Nam' not in first_dict['location'] and 'Vietnam' not in first_dict['location']):
        os.remove(json_path)
        print("Finish editing this file :" + json_path)
        return

    unique_reviews = set()

    for d in data:
        if d.get('caculated') == True:
            if 'reviews' in d and isinstance(d['reviews'], list):
                for review in d['reviews']:
                    unique_reviews.add(review)

    for d in data:
        if d.get('caculated') != True or not d.get('caculated'):
            d.setdefault('caculated', False)
            d.setdefault('dicts_sentiment_average', {})
            d.setdefault('dicts_adj', {})
            d.setdefault('list_proper_noun', [])
            d.setdefault('factor value', {})

            if 'reviews' in d and isinstance(d['reviews'], list):
                len_reviews = min(len(d['reviews']), 11)
                for i in range(len_reviews):
                    review = d['reviews'][i]
                    print("Processing " + str(temp_i) + " reviews...")
                    temp_i += 1
                    if review in unique_reviews:
                        continue
                    review = remove_trailing_phrases(review)
                    review_time = d.get('reviews_time', [])[i] if 'reviews_time' in d and i < len(d['reviews_time']) else d.get('reviews_time', [])[-1]
                    try:
                        days_diff = days_difference(review_time)
                    except:
                        days_diff = 500
                    dicts_sentiment, dicts_adj_feature, list_noun_feature , list_proper_noun_feature = TextEntities_Score(review)
                    dicts_sentiment, factor = adjust_dict_value(dicts_sentiment, days_diff)

                    for key, value in dicts_sentiment.items():
                        if key in d['dicts_sentiment_average']:
                            d['dicts_sentiment_average'][key].extend(value)
                            d['factor value'][key] += factor
                        else:
                            d['dicts_sentiment_average'][key] = value
                            d['factor value'][key] = factor

                    for key, value in dicts_adj_feature.items():
                        if key in d['dicts_adj']:
                            d['dicts_adj'][key].extend(value)
                        else:
                            d['dicts_adj'][key] = value
                    
                    d['list_proper_noun'].extend(list_proper_noun_feature)
                
                d['dicts_sentiment_average'] =  caculate_average_dict(d['dicts_sentiment_average'], d['factor value'])
                d['caculated'] = True
                unique_reviews.update(d['reviews'])

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("Finish editing this file :" + json_path)

# # Ví dụ sử dụng
# date_str = "Written December 26, 2017"
# days_diff = days_difference(date_str)
# print(f"Số ngày cách biệt: {days_diff}")

# the_dict = {'điểm du lịch hang động': [0.7465577945113182], 'đồi núi': [0.02136726677417755]}
# print(adjust_dict_value(the_dict, 0))

# process_json_file(r'E:\PBL7_Code_Model_and_Scraping\Crawler_Here\Scrape_Data\attraction\Viet Cuisine - Cơm Niêu Việt.json')

def sentiment_analysis_all():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    J_FOLDER = os.path.join(current_directory, 'Crawler_Here', 'Scrape_Data', 'attraction')
    json_file_paths = get_json_file_paths(J_FOLDER)
    for json_path in json_file_paths:
        process_json_file(json_path)

def combine_data_from_json(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    combine_factor_value = {}
    combine_dicts_sentiment_average = {}
    combine_dicts_adj = {}
    # Tổng hợp factor_value và dicts_sentiment_average từ mỗi dict trong list
    for item in data:
        dicts_sentiment_average = item.get('dicts_sentiment_average', {})
        factor_value = item.get('factor value', {})
        dicts_adj = item.get('dicts_adj', {})

        # Tổng hợp factor_value
        for key, value in factor_value.items():
            combine_factor_value[key] = combine_factor_value.get(key, 0) + value

        # Tổng hợp dicts_sentiment_average
        for key, value in dicts_sentiment_average.items():
            if key in factor_value:
                if key in combine_dicts_sentiment_average:
                    combine_dicts_sentiment_average[key] += value * factor_value[key]
                else:
                    combine_dicts_sentiment_average[key] = value * factor_value[key]
        
        # Tổng hợp dicts_adj
        for key, value in dicts_adj.items():
            if key in combine_dicts_adj:
                combine_dicts_adj[key].extend(value)
            else:
                combine_dicts_adj[key] = value

            combine_dicts_adj[key] = list(set(combine_dicts_adj[key]))

    # Chuẩn hóa combine_dicts_sentiment_average bằng cách chia cho tổng factor_value của mỗi key
    for key in combine_dicts_sentiment_average:
        combine_dicts_sentiment_average[key] /= combine_factor_value[key]

    return combine_dicts_sentiment_average, combine_dicts_adj, combine_factor_value


def save_sentiment_csv(json_path):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    sentiment_csv = os.path.join(current_directory, 'sentiment_value.csv')
    print("Reading file ... " + json_path)
    # Kiểm tra xem tập tin CSV có tồn tại không
    csv_exists = os.path.isfile(sentiment_csv)

    combine_dicts_sentiment_average, combine_dicts_adj, combine_factor_value = combine_data_from_json(json_path)

    # Tạo danh sách các key từ combine_dicts_sentiment_average
    entities = list(combine_dicts_sentiment_average.keys())
    print("Đây là list entities:")
    print(entities)

    # Đọc dữ liệu từ file JSON
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    location_values = data[0]['location']
    review_amount = data[0]["review_amount"]

    # Lấy tên tệp JSON mà không có phần mở rộng
    attraction_name = os.path.splitext(os.path.basename(json_path))[0]

    # Lấy tất cả giá trị factor và sắp xếp giảm dần
    factors = [combine_factor_value[entity] if combine_factor_value[entity] else 0 for entity in entities]
    factors_sorted = sorted(factors, reverse=True)
    if len(factors_sorted) >= 1:
        # Tính toán giá trị ngưỡng
        top_75_percent_index = math.ceil(len(factors_sorted) * 0.75)
        top_20_index = min(20, len(factors_sorted))
        threshold_index = min(top_75_percent_index, top_20_index)
        factor_threshold = factors_sorted[threshold_index - 1]  # vì index bắt đầu từ 0
    
    # Mở hoặc tạo tập tin CSV để ghi
    with open(sentiment_csv, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        rename_columns_if_needed(sentiment_csv)

        # Đối với mỗi key trong combine_dicts_sentiment_average
        for entity in entities:
            # Lấy sentiment score và list adj tương ứng
            sentiment_score = combine_dicts_sentiment_average[entity]

            factor = combine_factor_value[entity] if combine_factor_value[entity] else 0

            if factor < factor_threshold:
                factor = 0.25
            
            list_adj = ', '.join(combine_dicts_adj[entity]) if combine_dicts_adj[entity] else ''

            # Kiểm tra xem có hàng dữ liệu nào trùng Entity và Attraction Name không
            rows_to_remove = []
            if csv_exists:
                with open(sentiment_csv, 'r', newline='', encoding='utf-8') as file_read:
                    reader = csv.reader(file_read)
                    for row in reader:
                        if row[0] == attraction_name and row[1] == entity:
                            rows_to_remove.append(row)

                    # Xóa các hàng dữ liệu trùng lặp
                    if rows_to_remove:
                        with open(sentiment_csv, 'w', newline='', encoding='utf-8') as file_write:
                            writer_remove = csv.writer(file_write)
                            for row in reader:
                                if row not in rows_to_remove:
                                    writer_remove.writerow(row)

            # Thêm hàng dữ liệu mới
            writer.writerow([attraction_name, entity, sentiment_score, list_adj, factor])

        for location in location_values:
            if location == "Việt Nam":
                if review_amount <= 50:
                    writer.writerow([attraction_name, location, 0.5, "", 2])
                elif review_amount > 50 and review_amount <= 200:
                    writer.writerow([attraction_name, location, 0.75, "", 2])
                elif review_amount > 200 and review_amount < 500:
                    writer.writerow([attraction_name, location, 0.875, "", 2])
                else:
                    writer.writerow([attraction_name, location, 1, "", 2])
            # Thêm hàng dữ liệu mới
            else:
                writer.writerow([attraction_name, location, 1, "", 5])

def rename_columns_if_needed(file_path):
    # Đọc file CSV vào DataFrame
    df = pd.read_csv(file_path, header=None)
    
    # Kiểm tra xem dòng đầu tiên có phải là tên cột mong muốn không
    expected_columns = ["Attraction Name", "Entity", "Sentiment Score", "List Adj", "Coefficient"]
    if df.iloc[0].tolist() == expected_columns:
        # Dòng đầu tiên là tên cột
        df.columns = expected_columns
        df = df[1:]  # Bỏ dòng đầu tiên vì nó là tên cột
    else:
        # Đặt tên cột vì dòng đầu tiên không phải là tên cột
        df.columns = expected_columns
    
    # Lưu lại DataFrame đã được đặt tên cột vào file CSV
    df.to_csv(file_path, index=False)

    return df

def fully_updated_sentiment_csv():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    J_FOLDER = os.path.join(current_directory, 'Crawler_Here', 'Scrape_Data', 'attraction')
    json_file_paths = get_json_file_paths(J_FOLDER)
    for json_path in json_file_paths:
        save_sentiment_csv(json_path)
    print("Update Sentiment CSV completed.")

def get_synonyms_entities():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    J_FOLDER = os.path.join(current_directory, 'Crawler_Here', 'Scrape_Data', 'attraction')
    json_file_paths = get_json_file_paths(J_FOLDER)
    comment_json_path = os.path.join(current_directory, 'comment_storage.json')

    json_file_paths.insert(0,comment_json_path)

    entity_csv = os.path.join(current_directory, 'entity_translate.csv')

    the_entities_list = []
    for json_path in json_file_paths:
        combine_dicts_sentiment_average, _, _ = combine_data_from_json(json_path)
        for key, value in combine_dicts_sentiment_average.items():
            if key not in the_entities_list:
                the_entities_list.append(key)
    
    the_entities_list = list(set(the_entities_list))

    with open(entity_csv, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        for entity in the_entities_list:
            en_entity, is_take = translate_1_entity(entity)
            if is_take == True:
                writer.writerow([entity, en_entity])
                print("Updated entity <" + entity + "> to the database.")
    
    with open(comment_json_path, 'w', encoding='utf-8') as file_comment:
            json.dump([{}], file_comment, ensure_ascii=False, indent=4)

    # return the_entities_list, list_entities_english(the_entities_list)

def update_translate_entity_csv():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    entity_csv = os.path.join(current_directory, 'entity_translate.csv')

    # Kiểm tra xem tập tin CSV có tồn tại không
    csv_exists = os.path.isfile(entity_csv)
    # Mở hoặc tạo tập tin CSV để ghi
    with open(entity_csv, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Nếu tập tin CSV chưa tồn tại hoặc chưa có dữ liệu gì cả
        if not csv_exists or os.stat(entity_csv).st_size == 0:
            # Ghi tiêu đề cho tập tin CSV
            writer.writerow(["Entity_VI", "Entity_EN"])
        
        # list_entity_vi, list_entity_en = get_synonyms_entities()
        
        # for i in range(len(list_entity_vi)):
        #     if check_value_in_column(entity_csv,'Entity_VI',list_entity_vi[i]) == True:
        #         continue
        #     writer.writerow([list_entity_vi[i], list_entity_en[i]])
    get_synonyms_entities()


def check_value_in_column(csv_path, column_name, value):
    try:
        # Đọc tệp CSV vào DataFrame
        df = pd.read_csv(csv_path)
        
        # Kiểm tra xem cột có tồn tại không
        if column_name not in df.columns:
            return False
        
        # Kiểm tra xem giá trị có tồn tại trong cột không
        return value in df[column_name].values
    except FileNotFoundError:
        print(f"File at path {csv_path} not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def list_entities_english(list_vie_entities):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    entity_csv = os.path.join(current_directory, 'entity_translate.csv')
    csv_exists = os.path.isfile(entity_csv)
    list_en_entities = []
    if not csv_exists:
        return [final_translate_text(entity, translate_to = "en") for entity in list_vie_entities]
    for i in range(len(list_vie_entities)):
        if check_value_in_column(entity_csv,'Entity_VI',list_vie_entities[i]) == False:
            list_en_entities.append(final_translate_text(list_vie_entities[i], translate_to = "en"))
        else:
            list_en_entities.append('ignore')
    return list_en_entities

def translate_1_entity(vie_entity):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    entity_csv = os.path.join(current_directory, 'entity_translate.csv')
    csv_exists = os.path.isfile(entity_csv)
    if not csv_exists:
        return final_translate_text(vie_entity), True

    if check_value_in_column(entity_csv,'Entity_VI',vie_entity) == False:
        return final_translate_text(vie_entity, translate_to = "en"), True
    else:
        return "ignore", False

def convert_json_to_dict(input_file, output_file):
    """
    Hàm chuyển đổi file JSON thành dictionary.

    Args:
        input_file (str): Đường dẫn đến file JSON đầu vào.
        output_file (str): Đường dẫn đến file JSON đầu ra.
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cluster_dict = {}
    for i, cluster in enumerate(data):
        key = f"cluster_{i}"
        cluster_dict[key] = cluster

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cluster_dict, f, ensure_ascii=False, indent=4)


def export_synonyms_clusters():
    update_translate_entity_csv()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    entity_csv = os.path.join(current_directory, 'entity_translate.csv')
    df = pd.read_csv(entity_csv)
    
    # Lập danh sách các từ từ cột "Entity_EN"
    words_list = df['Entity_EN'].tolist()

    # Tính toán ma trận tương đồng và phân cụm từ
    similarity_matrix = synonyms_matrix(words_list)
    clusters = cluster_words(words_list, similarity_matrix, 0.6)

    # Tạo dictionary ánh xạ từ Entity_EN sang Entity_VI
    en_to_vi_map = dict(zip(df['Entity_EN'], df['Entity_VI']))

    # Ánh xạ các cluster từ Entity_EN sang Entity_VI
    vi_clusters = []
    for cluster in clusters:
        vi_cluster = [en_to_vi_map[word] for word in cluster]
        vi_clusters.append(vi_cluster)
    
    cluster_json = os.path.join(current_directory, 'vi_clusters.json')
    os.makedirs(os.path.dirname(cluster_json), exist_ok=True)
    # Lưu trữ vi_clusters dưới dạng file JSON
    with open(cluster_json, 'w', encoding='utf-8') as f:
        json.dump(vi_clusters, f, ensure_ascii=False, indent=4)
    
    convert_json_to_dict(cluster_json,cluster_json)
    print("Hoàn tất trích entity cluster!")

    return vi_clusters

# print(combine_data_from_json(r'E:\PBL7_Code_Model_and_Scraping\Crawler_Here\Scrape_Data\attraction\Viet Cuisine - Cơm Niêu Việt.json'))
# save_sentiment_csv(r'E:\PBL7_Code_Model_and_Scraping\Crawler_Here\Scrape_Data\attraction\Viet Cuisine - Cơm Niêu Việt.json')
# fully_updated_sentiment_csv()

# fully_updated_sentiment_csv()

# sentiment_analysis_all()