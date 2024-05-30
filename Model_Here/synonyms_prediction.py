from sentence_transformers import SentenceTransformer, util
import os
import re
current_directory = os.path.dirname(os.path.abspath(__file__))  # Lấy thư mục chứa chương trình đang chạy
model_directory = os.path.join(current_directory, "SynonymsModel")
model_path = os.path.join(model_directory, "avodamed-synonym-generator1")
model_synonyms = SentenceTransformer(model_path)


def synonyms_matrix(words_list):
    # Lấy đường dẫn tới thư mục chứa model
    
    embeddings = model_synonyms.encode(words_list)
    similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)
    return similarity_matrix
  
def re_cluster(cluster_dict, entity):
    embedding_new_word = model_synonyms.encode(entity)
    for key, values in cluster_dict.items():
        for value in values:
          value = re.sub(r'[^a-zA-Z0-9\s]', '', value).strip()
          embedding_cluster_word = model_synonyms.encode(value)

          similarity_value = util.pytorch_cos_sim(embedding_cluster_word, embedding_new_word).item()
          if similarity_value > 0.5:
            cluster_dict[key].append(entity) 
            return cluster_dict, key
    cluster_dict[entity] = entity
    return cluster_dict, entity
    # Lấy đường dẫn tới thư mục chứa model
    
    # embeddings = model_synonyms.encode(words_list)
    # similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)
    # return similarity_matrix

def cluster_words(words_list, similarity_matrix, thresh_hold):
  """
  Phân cụm danh sách từ dựa trên ma trận tương đồng.

  Args:
    words_list: Danh sách các từ.
    similarity_matrix: Ma trận tương đồng giữa các từ.
    thresh_hold: Ngưỡng độ tương đồng tối thiểu để nhóm hai từ chung cụm.

  Returns:
    Danh sách các cụm, mỗi cụm là một danh sách các từ có độ tương đồng >= thresh_hold.
  """
  clusters = []
  for i in range(len(words_list)):
    already_in_cluster = False
    for c in clusters:
        if words_list[i] in c:
          already_in_cluster = True
          break
    if already_in_cluster == True:
      continue
    cluster = [words_list[i]]
    for j in range(i + 1, len(words_list)):
      if similarity_matrix[i, j] >= thresh_hold:
        if not any(cluster in c for c in clusters):
          cluster.append(words_list[j])
        else:
          for c in clusters:
            if words_list[j] in c:
              cluster += c
              clusters.remove(c)
              break
    clusters.append(cluster)
  return clusters


# word_dict = {"cluster_1": [
#  "set",
#  "that set",
#  "pants set",
#  "set",
#  "accessory set",
#  "seafood set",
#  "play set",
#  "base set"
#  ],
#  "cluster_2": [
#  "skin",
#  "jacket",
#  "sweat",
#  "nose",
#  "fried frog skin",
#  "paint",
#  "face",
#  "clothes -"
#  ]}
# words_list = ["staff", "waiter", "reception", "advice", "breakfast", "massage service"]
# word = "food"
# print(re_cluster(word_dict, word))
# similarity_matrix = synonyms_matrix(words_list)
# clusters = cluster_words(words_list, similarity_matrix, 0.5)
# print(similarity_matrix)
# print(clusters)
# similarity_matrix = synonyms_matrix(words_list)
# clusters = cluster_words(words_list, similarity_matrix, 0.5)
# print(similarity_matrix)
# print(clusters)

