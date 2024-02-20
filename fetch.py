import asyncio
import aiohttp
import json
import time
import os
import shutil
from tqdm import tqdm

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
    if os.path.exists(output_path):
        old_output_path = f"{output_folder_path}/old_all_tps_data.jsonl"
        shutil.move(output_path, old_output_path)

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
            
    duration_seconds = time.time()-main_start_time
    print(f"fetch result: {duration_seconds=:.2f};{result_count=};{success_count=};{failed_count=}")

def fetch_procedure(urls, update_folder_path, num_threads):
    asyncio.run(main(urls, update_folder_path, num_threads))

