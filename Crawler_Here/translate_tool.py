import requests
import json
from Crawler_Here.rotate_proxy import request_with_proxy, get_1_proxy_data
import re
TRANSLATION_ERROR = "Lỗi dịch"
TRANSLATION_PROVIDER = "Google Translate"
# translate_from = "vi"
# translate_to = "en"

def translate_text(text, translate_from = "auto", translate_to = "vi", auth_key=None, proxy_data = None):
    if auth_key:
        url = f"https://translation.googleapis.com/language/translate/v2?format=text&target={translate_to}&key={auth_key}"
        data = {"q": [text], "source": translate_from}
        # response = requests.post(url, json=data)
        if proxy_data:
            response = request_with_proxy(url, proxy_data=proxy_data, json_data=data)
        else:
            response = requests.post(url, json=data)
        if response.status_code == 200:
            translation = json.loads(response.text)["data"]["translations"][0]["translatedText"]
            return True, translation
        else:
            return False, f"{TRANSLATION_ERROR}: {response.text}"
    else:
        url = f"https://translate.google.com/m?sl={translate_from}&tl={translate_to}&q={text}"
        # response = requests.get(url)
        if proxy_data:
            response = request_with_proxy(url, proxy_data=proxy_data)
        else:
            response = requests.get(url)
        if response.status_code == 200:
            start = response.text.find("result-container\">") + 18
            end = response.text.find('<', start)
            translation = response.text[start:end]
            return True, translation
        else:
            return False, f"{TRANSLATION_ERROR}: {response.text}"

def final_translate_text(text, translate_from = "auto", translate_to = "vi", auth_key=None, proxy_data = None):
    text = re.sub(r'[^\w\s?!,;.:_\-]', ' - ', text)
    try:
        is_success, translated_text = translate_text(text, translate_from, translate_to, auth_key, proxy_data)
    except:
        if not proxy_data:
            return final_translate_text(text, translate_from = "auto", translate_to = "vi", auth_key=None, proxy_data = get_1_proxy_data())
    if is_success == True and len(translated_text) <= 1900:
        return translated_text
    else:
        if not proxy_data:
            return final_translate_text(text, translate_from = "auto", translate_to = "vi", auth_key=None, proxy_data = get_1_proxy_data())
        else:
            return text
        
# general_info = [
#             "Mugla Province",
#             "Oludeniz",
#             "Türkiye",
#             "Turkish Aegean Coast",
#             "Babadag Cable Car",
#             "Vietnam",
#             "Things to Do in Oludeniz"
#         ]
# translated_info = [final_translate_text(text) for text in general_info]
# print(translated_info)
