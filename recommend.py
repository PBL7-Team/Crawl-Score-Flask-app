import pandas as pd
import json

from Model_Here.keyphrase import TextEntities_Score


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
            
    return result_df


def recommend_system(text):
    dicts_sentiment, dicts_adj_feature, list_noun_feature, list_proper_noun_feature = TextEntities_Score(text,True)
    new_contentbase_df = get_new_contentbase_df()
    
    return 'ok'
