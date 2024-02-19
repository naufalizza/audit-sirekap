import asyncio
import aiohttp
import json
import time
from tqdm import tqdm
import os

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

async def fetch_and_save_data(url: str, output_path: str, error_log_path: str):
    timestamp = int(time.time() // 1)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()

    except Exception as e:
        with open(error_log_path, "a") as fp:
            print(f"{timestamp} | Warning: Cannot fetching result from {url}. Error info: {repr(e)}")
        result = None

    data = {
        "url": url,
        "data": result, # If it's None, it counts as incomplete data with not-an-object reason.
        # "reason": [], (we are no longer need this)
        "timestamp": timestamp
    }

    # Notice that the output from data path with append mode. Old file is expected to be deleted before using this procedure.
    with open(output_path, "a") as fp:
        print(json.dumps(data), file=fp)
    
    return url, result

async def fetch_and_save_multiple(urls, output_path, error_log_path):
    tasks = [fetch_and_save_data(url, output_path, error_log_path) for url in urls]
    return await asyncio.gather(*tasks)

async def main(urls: list[str], output_folder_path: str, num_threads: int):
    output_path = f"{output_folder_path}/all_tps_data.jsonl"
    error_log_path = f"{output_folder_path}/error_log.txt"

    print(f'fetching from {len(urls)} endpoint(s) ....')
    main_start_time = time.time()

    result_count = 0
    success_count = 0
    failed_count = 0
    for i in tqdm(range(0, len(urls), num_threads)):
        results = await fetch_and_save_multiple(urls[i:i+num_threads], output_path, error_log_path)
        for _, r in results:
            result_count += 1
            if r is not None:
                success_count += 1
            else:
                failed_count += 1
            
    print(f'main elapsed time: {time.time()-main_start_time:.2f} from {len(urls)} endpoints')
    print(f"{result_count=}")
    print(f"{success_count=}")
    print(f"{failed_count=}")

def make_first_next_url_list():
    # This is only used for the first time
    input_dict = load_data("data")
    urls = extract_urls_from_dict(input_dict)
    return urls

if __name__ == "__main__":
    import sys
    update_folder_path = sys.argv[1]
    num_threads = int(sys.argv[2])

    urls = []
    next_url_path = f"{update_folder_path}/next_url.txt"
    if os.path.exists(next_url_path):
        with open(next_url_path) as fp:
            for line in fp:
                urls.append(line.strip())
    else:
        print(f"{next_url_path} doesn't exists. All URLs are taken.")
        urls = make_first_next_url_list()

    print("Warning: for testing, we just take first 50 data.")
    urls = urls[:50]

    if not os.path.exists(update_folder_path):
        os.makedirs(update_folder_path)
    
    asyncio.run(main(urls, update_folder_path, num_threads))
    print("TODO: validate and make")
