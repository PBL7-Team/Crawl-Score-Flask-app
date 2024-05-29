from dotenv import load_dotenv
import gdown
import os
import patoolib

def download_model(url,output):
    required_subdirectories = ['BERT_Sentiment', 'KeyPhraseModel', 'SynonymsModel']
    for subdir in required_subdirectories:
        subdir_path = os.path.join('Model_Here', subdir)
        if os.path.exists(subdir_path):
            return 

    directory = './'
    gdown.download(url, output)
    supported_extensions = ('.rar', '.zip', '.7z')

    for filename in os.listdir(directory):
        if filename.endswith(supported_extensions):
            file_path = os.path.join(directory, filename)
            try:
                patoolib.extract_archive(file_path, outdir='Model_Here')
                print(f"Extracted: {file_path}")
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error when extracting {file_path}: {e}")


load_dotenv()

GDRIVE_URL = os.getenv("GDRIVE_URL")
MODEL_DOWNLOAD_FILE = os.getenv("MODEL_DOWNLOAD_FILE")

download_model(GDRIVE_URL, MODEL_DOWNLOAD_FILE)