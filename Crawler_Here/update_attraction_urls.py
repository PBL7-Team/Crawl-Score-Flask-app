def process_urls(file_path):
    with open(file_path, 'r') as file:
        urls = file.readlines()

    # Loại bỏ các URL trùng lặp
    unique_urls = list(set(url.strip() for url in urls))

    # Hàm kiểm tra cấu trúc "or + number"
    def has_or_number_part(url):
        parts = url.split('-')
        for part in parts:
            if part.startswith('or') and part[2:].isdigit():
                return True
        return False

    # Loại bỏ các URL có phần chứa cấu trúc "or + number"
    filtered_urls = [url for url in unique_urls if not has_or_number_part(url)]

    # Ghi kết quả vào file txt
    with open(file_path, 'w') as file:
        for url in filtered_urls:
            file.write(url + '\n')


# Sử dụng hàm và in kết quả
file_path = r'E:\PBL7_CodeModel\Crawler_Here\review-url\attraction.txt'
filtered_urls = process_urls(file_path)
