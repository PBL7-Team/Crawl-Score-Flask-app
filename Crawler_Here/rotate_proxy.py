import requests
from bs4 import BeautifulSoup
import csv
import os
def get_free_proxies():
    url = 'https://sslproxies.org/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table')
    thead = table.find('thead').find_all('th')
    tbody = table.find('tbody').find_all('tr')

    headers = [th.text.strip() for th in thead]

    proxies = []
    for tr in tbody:
        proxy_data = {}
        tds = tr.find_all('td')
        for i in range(len(headers)):
            proxy_data[headers[i]] = tds[i].text.strip()
        proxies.append(proxy_data)
    
    return proxies[:8]


def check_csv(filename='sampleproxies.csv'):
    
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Kết hợp với tên file để tạo đường dẫn đầy đủ
    file_path = os.path.join(current_directory, filename)
    if not os.path.exists(file_path):
        write_proxies_to_csv()
        return
    
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        row_count = sum(1 for row in reader)

    if row_count <= 1:
        write_proxies_to_csv()
    
    return

def write_proxies_to_csv(filename='sampleproxies.csv'):
    proxies = get_free_proxies()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Kết hợp với tên file để tạo đường dẫn đầy đủ
    file_path = os.path.join(current_directory, filename)
    file_exists = os.path.exists(file_path)

    with open(file_path, 'a', newline='') as csvfile:
        fieldnames = proxies[0].keys() if proxies else []  # Sử dụng keys của dictionary đầu tiên trong danh sách proxies làm tên cột
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Nếu file chưa tồn tại, viết tiêu đề của các cột
        if not file_exists:
            writer.writeheader()

        # Viết dữ liệu cho mỗi proxy vào file CSV
        for proxy in proxies:
            writer.writerow(proxy)

def get_1_proxy_data(filename='sampleproxies.csv'):
    check_csv()
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Kết hợp với tên file để tạo đường dẫn đầy đủ
    file_path = os.path.join(current_directory, filename)
    # Kiểm tra xem file đã tồn tại hay không
    if not os.path.exists(file_path):
        print("File not found!")
        return None

    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)

    # Lấy dữ liệu của dòng cuối cùng
    if data:
        proxy_data = data[-1]
    else:
        print("File is empty!")
        return None

    # Xóa dòng cuối cùng khỏi danh sách
    data = data[:-1]

    # Ghi lại nội dung mới vào file CSV
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = proxy_data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Viết tiêu đề của các cột
        writer.writeheader()

        # Viết lại dữ liệu cho mỗi proxy vào file CSV
        for row in data:
            writer.writerow(row)

    return proxy_data

def request_with_proxy(url, proxy_data, json_data = None):
    try:
        proxy_url = f"{proxy_data['IP Address']}:{proxy_data['Port']}"
        proxies = {
            'http': f'http://{proxy_url}',
            'https': f'https://{proxy_url}'
        }
        if json_data:
            response = requests.post(url, proxies=proxies, json=json_data)
        else:
            response = requests.get(url, proxies=proxies)
        return response
    except Exception as e:
        if json_data:
            response = requests.post(url, json=json_data)
        else:
            response = requests.get(url)
        return response