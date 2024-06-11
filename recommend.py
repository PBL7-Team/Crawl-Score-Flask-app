import pandas as pd
import json
import re
import unicodedata
import math
import os
from rapidfuzz import fuzz
from Model_Here.keyphrase import TextEntities_Score, TextEntities_recommend
from Model_Here.score_extract import annotate_text
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
import numpy as np

CONTENT_BASED_DF = pd.read_csv('./content_base_score_df.csv', index_col=0)

def get_new_contentbase_df():
    sentiment_df = pd.read_csv('./sentiment_value.csv')
    with open('./vi_clusters.json', 'r', encoding='utf-8') as f:
        clusters = json.load(f)

    cluster_dict = {}
    for key, values in clusters.items():
        for value in values:
            cluster_dict[value] = key

    all_entities = set(sentiment_df['Entity'])
    clustered_entities = set(cluster_dict.keys())
    unique_entities = all_entities - clustered_entities

    for entity in unique_entities:
        cluster_dict[entity] = entity

    location_groups = sentiment_df.groupby('Attraction Name')
    columns = list(set(cluster_dict.values()))
    result_df = pd.DataFrame(index=sentiment_df['Attraction Name'].unique(), columns=columns).fillna(0.5)

    for location, group in location_groups:
        scores = {}
        weights = {}
        for _, row in group.iterrows():
            entity = row['Entity']
            score = row['Sentiment Score']
            weight = row['Coefficient']
            cluster = cluster_dict[entity]

            if cluster not in scores:
                scores[cluster] = 0
                weights[cluster] = 0

            scores[cluster] += score * weight
            weights[cluster] += weight

        for cluster in scores:
            cluster_weight = weights[cluster]
            # print(cluster_weight)
            if cluster_weight <= 0.5:
                result_df.at[location, cluster] = 0.5 + (0.1 * (scores[cluster] / cluster_weight))
            elif 0.5 < cluster_weight <= 2:
                result_df.at[location, cluster] = 0.5 + (0.4 * (scores[cluster] / cluster_weight))
            elif cluster_weight > 2 and cluster_weight <= 5:
                result_df.at[location, cluster] = 0.5 + (0.45 * (scores[cluster] / cluster_weight))
            else:
                result_df.at[location, cluster] = 0.5 + (0.5 * (scores[cluster] / cluster_weight))
    result_df.to_csv('content_base_score_df.csv', index=True, mode='w')
    return result_df


def recommend_system(text):
    # print("Hi")
    if "Việt Nam" not in text:
        text = text + " tại Việt Nam."
    # dicts_sentiment, _, _, _ = TextEntities_Score(text,True)
    # list_entity = list(dicts_sentiment.keys())
    list_entity = TextEntities_recommend(text)
    # print(list_entity)
    list_proper_noun_feature = [word['wordForm'] for word in annotate_text(text) if word['nerLabel'] in ['B-LOC', 'B-PER']]
    if "Hồ Chí Minh" in list_proper_noun_feature:
        list_proper_noun_feature.append("Ho Chi Minh City")
        if "Hồ Chí Minh" in list_proper_noun_feature:
            list_proper_noun_feature.remove("Hồ Chí Minh")

    # print(list_proper_noun_feature)
    # new_contentbase_df = get_new_contentbase_df()
    # print(dicts_sentiment)
    # print(list_proper_noun_feature)
    # print(list_entity)
    # conduct_content_base(dicts_sentiment, list_proper_noun_feature)
    
    # return conduct_content_base(dicts_sentiment, list_proper_noun_feature)
    return conduct_content_base(list_entity, list_proper_noun_feature)

# def find_cluster(cluster_dict, entity):
#     entity = re.sub(r'[^a-zA-Z0-9\s]', '', entity).strip().lower()
#     entity = unicodedata.normalize('NFC', ''.join(c for c in unicodedata.normalize('NFD', entity) if unicodedata.category(c) != 'Mn'))
#     for key, values in cluster_dict.items():
#         for value in values:
#           value = re.sub(r'[^a-zA-Z0-9\s]', '', value).strip().lower()
#           value = unicodedata.normalize('NFC', ''.join(c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn'))
#           if entity == value:
#             return key

#     return None

def find_cluster(cluster_dict, entity):
    entity = entity.lower()
    best_score = 0
    best_key = None
    for key, values in cluster_dict.items():
        for value in values:
            score = fuzz.ratio(value.lower(), entity)
            if score > best_score and score >= 70:
                best_score = score
                best_key = key
                
    return best_key

# get_new_contentbase_df()
def conduct_content_base(dicts_sentiment, list_proper_noun_feature):

    
    with open('./vi_clusters.json', 'r', encoding='utf-8') as f:
        clusters_dict = json.load(f)
    
    # keys_list = list(dicts_sentiment.keys())
    keys_list = dicts_sentiment
    storage_key_list = []

    # print(keys_list)
    # print(list_proper_noun_feature)
    comment_cluster_list = []

    for key in keys_list:
        in_cluster = find_cluster(clusters_dict, key)
        if in_cluster is None:
            comment_cluster_list.append(key)
            CONTENT_BASED_DF[key] = 0
            storage_key_list.append(key)
        else:
            comment_cluster_list.append(in_cluster)

    update_json(storage_key_list)

    # print(comment_cluster_list)
    comment_cluster_list += list_proper_noun_feature
    # print(comment_cluster_list)

    # Thêm các cột mới vào DataFrame nếu chưa tồn tại
    for proper_noun in list_proper_noun_feature:
        if proper_noun not in CONTENT_BASED_DF.columns:
            CONTENT_BASED_DF[proper_noun] = 0
    
    filtered_df = CONTENT_BASED_DF[comment_cluster_list]
    len_n = len(filtered_df.columns)
    vector = [1] * len_n
    # print(vector)
    # print(filtered_df.columns)
    # print(filtered_df.loc['Thanh Spa'])
    # # Duyệt qua từng tên cột và kiểm tra
    # for i, col in enumerate(column_names):
    #     if col in comment_cluster_list:
    #         vector[i] = 1

    # Tạo DataFrame từ lịch sử hoạt động của User1
    user_history_df = pd.DataFrame([vector], columns=filtered_df.columns)
    # Tính toán độ tương tự cosine giữa lịch sử hoạt động của người dùng và các địa danh
    user_similarity = 1 - euclidean_distances(user_history_df, filtered_df)/len_n

    # Chuyển ma trận độ tương tự thành DataFrame để dễ xử lý
    user_similarity_df = pd.DataFrame(user_similarity, index=user_history_df.index, columns=filtered_df.index)

    # Sắp xếp ma trận user_similarity_df theo thứ tự giảm dần của các giá trị tương tự
    sorted_user_similarity_df = user_similarity_df.apply(lambda row: row.sort_values(ascending=False), axis=1)
    # print(sorted_user_similarity_df)

    threshold = 1 - math.sqrt(len_n * 0.3 ** 2)/len_n
    # print(threshold)
    sorted_user_similarity_df = sorted_user_similarity_df.T
    list_valid_attraction = sorted_user_similarity_df[sorted_user_similarity_df[0] >= threshold].sort_values(by=0, ascending=False).index.tolist()

    return list_valid_attraction

def update_json(key_list, json_path='comment_storage.json'):
    # Kiểm tra nếu tệp JSON đã tồn tại
    if not os.path.exists(json_path):
        # Nếu tệp chưa tồn tại, khởi tạo một list chứa một dict rỗng và lưu vào tệp JSON
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump([{}], file, ensure_ascii=False, indent=4)
    
    # Đọc nội dung từ tệp JSON
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Lấy dict đầu tiên trong list
    first_dict = data[0]
    
    # Khởi tạo các trường nếu chưa tồn tại
    if 'dicts_sentiment_average' not in first_dict:
        first_dict['dicts_sentiment_average'] = {}
    if 'factor_value' not in first_dict:
        first_dict['factor value'] = {}
    if 'dicts_adj' not in first_dict:
        first_dict['dicts_adj'] = {}
    
    # Cập nhật các key trong key_list vào các trường tương ứng
    for key in key_list:
        first_dict['dicts_sentiment_average'][key] = 1
        first_dict['factor value'][key] = 1
        first_dict['dicts_adj'][key] = []
    
    # Lưu lại các thay đổi vào tệp JSON
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# text = "giới thiệu cho tôi 1 chỗ nhà hàng đồ ăn và 1 kỳ quan thế giới, bảo tàng."
# print(recommend_system(text))
