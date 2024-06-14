import os
from huggingface_hub import snapshot_download

def download_model_if_not_exists(repo_id, local_dir):
    if not os.path.exists(local_dir):
        print(f"Thư mục {local_dir} không tồn tại. Bắt đầu tải về model...")
        snapshot_download(repo_id=repo_id, local_dir=local_dir)
        print(f"Model đã được tải về và lưu tại {local_dir}.")
    else:
        print(f"Thư mục {local_dir} đã tồn tại. Không cần tải về model.")


def dowwload_model():
    download_model_if_not_exists('mr4/phobert-base-vi-sentiment-analysis', './Model_Here/BERT_Sentiment/bert-base-sentiment-analysis')
    download_model_if_not_exists('tekraj/avodamed-synonym-generator1', './Model_Here/SynonymsModel/avodamed-synonym-generator1')
    download_model_if_not_exists('trituenhantaoio/bert-base-vietnamese-uncased', './Model_Here/KeyPhraseModel/bert-base-vietnamese-uncased')
    download_model_if_not_exists('vinhnado/bert-bilstm-crf-keyphrase', './Model_Here/KeyPhraseModel/bert-bilstm-crf-keyphrase')
