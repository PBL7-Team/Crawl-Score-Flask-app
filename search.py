from rapidfuzz import process, fuzz

# Danh sách các địa điểm
locations = [
    "Phố cổ Hội An",
    "Thành phố Hồ Chí Minh",
    "Hà Nội",
    "Huế",
    "Đà Nẵng",
    "Nha Trang",
    "Phú Quốc",
    "Sapa"
]

# Hàm tìm kiếm địa điểm gần đúng
def find_best_match(query, location_list, threshold=50):
    match = process.extractOne(query, location_list, scorer=fuzz.ratio)
    
    if match[1] >= threshold:
        print(f"Kết quả tìm kiếm cho '{query}': {match[0]} với điểm số {match[1]}")
        return match[0]
    else:
        return None

# Thử nghiệm với một số ví dụ
queries = ["Phố hội", "hue", "danang", "phuquoc", "saigon"]
for query in queries:
    result = find_best_match(query, locations)
    if result is None:
        print(f"Không tìm thấy kết quả phù hợp cho '{query}'")
