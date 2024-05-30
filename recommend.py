import pandas as pd
import json
import re
import unicodedata
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
    print(dicts_sentiment)
    print(list_proper_noun_feature)
    conduct_content_base(dicts_sentiment, list_proper_noun_feature)
    
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

    comment_cluster_list = []
    for key in keys_list:
        in_cluster = find_cluster(clusters_dict, key)
        if in_cluster != None:
            comment_cluster_list.append(in_cluster)

    column_names = content_base_df.columns
    for proper_noun in list_proper_noun_feature:
        if proper_noun in column_names:
            comment_cluster_list.append(proper_noun)
    
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

    return sorted_user_similarity_df

text = "giới thiệu cho tôi 1 chỗ nhà hàng đồ ăn tại Đà Nẵng."
print(recommend_system(text))