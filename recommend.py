import pandas as pd
import json
import re
import unicodedata
import os
from Model_Here.keyphrase import TextEntities_Score
from Model_Here.synonyms_prediction import re_cluster
from Model_Here.score_extract import annotate_text
from Crawler_Here.translate_tool import final_translate_text
from sklearn.metrics.pairwise import cosine_similarity

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
    result_df = pd.DataFrame(index=sentiment_df['Attraction Name'].unique(), columns=columns).fillna(0)

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
            result_df.at[location, cluster] = scores[cluster] / weights[cluster]
    
    result_df.to_csv('content_base_score_df.csv', index=True, mode='w')
    return result_df


def recommend_system(text):
    # print("Hi")
    dicts_sentiment, _, _, _ = TextEntities_Score(text,True)
    list_proper_noun_feature = [word['wordForm'] for word in annotate_text(text) if word['nerLabel'] in ['B-LOC', 'B-PER']]
    # new_contentbase_df = get_new_contentbase_df()
    # print(dicts_sentiment)
    # print(list_proper_noun_feature)
    # conduct_content_base(dicts_sentiment, list_proper_noun_feature)
    
    return conduct_content_base(dicts_sentiment, list_proper_noun_feature)

def find_cluster(cluster_dict, entity):
    entity = re.sub(r'[^a-zA-Z0-9\s]', '', entity).strip().lower()
    entity = unicodedata.normalize('NFC', ''.join(c for c in unicodedata.normalize('NFD', entity) if unicodedata.category(c) != 'Mn'))
    for key, values in cluster_dict.items():
        for value in values:
          value = re.sub(r'[^a-zA-Z0-9\s]', '', value).strip().lower()
          value = unicodedata.normalize('NFC', ''.join(c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn'))
          if entity == value:
            return key

    return None

# get_new_contentbase_df()
def conduct_content_base(dicts_sentiment, list_proper_noun_feature):
    sentiment_df = pd.read_csv('./sentiment_value.csv')
    content_base_df = pd.read_csv('./content_base_score_df.csv', index_col=0)
    
    with open('./vi_clusters.json', 'r', encoding='utf-8') as f:
        clusters_dict = json.load(f)
    
    keys_list = list(dicts_sentiment.keys())
    storage_key_list = []

    # print(keys_list)
    # print(list_proper_noun_feature)
    comment_cluster_list = []

    for key in keys_list:
        in_cluster = find_cluster(clusters_dict, key)
        if in_cluster == None:
            comment_cluster_list.append(key)
            content_base_df[key] = 0
            storage_key_list.append(key)
        else:
            comment_cluster_list.append(in_cluster)

    update_json(storage_key_list)

    # print(comment_cluster_list)
    comment_cluster_list = comment_cluster_list + list_proper_noun_feature
    # print(comment_cluster_list)

    column_names = content_base_df.columns
    for proper_noun in list_proper_noun_feature:
        if proper_noun not in column_names:
            content_base_df[proper_noun] = -2
    
    filtered_df = content_base_df[comment_cluster_list]

    vector = [2] * len(filtered_df.columns)
    # # Duyệt qua từng tên cột và kiểm tra
    # for i, col in enumerate(column_names):
    #     if col in comment_cluster_list:
    #         vector[i] = 1

    # Tạo DataFrame từ lịch sử hoạt động của User1
    user_history_df = pd.DataFrame([vector], columns=filtered_df.columns)
    # Tính toán độ tương tự cosine giữa lịch sử hoạt động của người dùng và các địa danh
    user_similarity = cosine_similarity(user_history_df, filtered_df)

    # Chuyển ma trận độ tương tự thành DataFrame để dễ xử lý
    user_similarity_df = pd.DataFrame(user_similarity, index=user_history_df.index, columns=filtered_df.index)

    # Sắp xếp ma trận user_similarity_df theo thứ tự giảm dần của các giá trị tương tự
    sorted_user_similarity_df = user_similarity_df.apply(lambda row: row.sort_values(ascending=False), axis=1)

    # print(sorted_user_similarity_df)

    threshold = 0.5
    sorted_user_similarity_df = sorted_user_similarity_df.T
    list_valid_attraction = sorted_user_similarity_df[sorted_user_similarity_df[0] > threshold].sort_values(by=0, ascending=False).index.tolist()


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
