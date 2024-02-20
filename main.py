import os
import json
from fetch import fetch_procedure
from update import update_procedure
from validation import validation_procedure

def get_next_url_list(update_folder_path):
    urls = []
    next_url_path = f"{update_folder_path}/next_url.txt"
    if os.path.exists(next_url_path):
        with open(next_url_path) as fp:
            for line in fp:
                urls.append(line.strip())
    else:
        print(f"{next_url_path} doesn't exists. All URLs are taken.")
        urls = make_first_next_url_list()
        with open(next_url_path, mode="w") as fp:
            for url in urls:
                print(url, file=fp)
        
    return urls

def make_first_next_url_list():
    # This is only used for the first time.
    input_dict = load_data("data")
    urls = extract_urls_from_dict(input_dict)
    print("Warning: for testing, we just take first 50 data.")
    urls = urls[:50]
    return urls

def load_data(data_dir: str):
    provinces_filename = os.listdir(data_dir)
    print("jumlah provinsi + 1 (dari luar negeri):", len(provinces_filename))
    validated_provinces_data = {}
    for province_filename in provinces_filename:
        province_name = ".".join(province_filename.split(".")[:-1])
        with open(os.path.join(data_dir, province_filename), "r") as f:
            province_data = json.load(f)
        validated_provinces_data[province_name] = province_data
    return validated_provinces_data

def extract_urls_from_dict(input_dict):
    url_list = []

    def extract_urls(data):
        if isinstance(data, str):
            # Check if the string is a URL
            if data.startswith("http://") or data.startswith("https://"):
                data = data.replace("/wilayah/pemilu/ppwp", "/pemilu/hhcw/ppwp")
                url_list.append(data)
        elif isinstance(data, dict):
            for value in data.values():
                extract_urls(value)
        elif isinstance(data, (list, tuple)):
            for item in data:
                extract_urls(item)

    extract_urls(input_dict)
    return url_list

if __name__ == "__main__":
    import sys
    update_folder_path = sys.argv[1]
    num_fetch_threads = int(sys.argv[2])

    count = 0
    stop = False
    while not stop:
        urls = get_next_url_list(update_folder_path)
        if len(urls) == 0:
            stop = True
        else:
            fetch_procedure(urls, update_folder_path, num_fetch_threads)
            validation_procedure(update_folder_path)
            update_procedure(update_folder_path)
            
            count += 1
            if count >= 5:
                print("Early break just for test")
                break
