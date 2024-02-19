import json
import os
import re
import sys

raw_invalid_path = sys.argv[1]
invalid_data_folder_path = sys.argv[2]

"""
Temporary data format:
timestamp: 1708211880
summary: [
    count: 923022,
    reason: [
        <reason-1>: 52,
        <reason-2>: 117
    ]
]
data: {
    73: {
        timestamp: ...
        summary: ...
        data: ...
    }
}

Endpoint example: "https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/17/1701/170108/1701082005/1701082005001.json"
Pattern: 

TPS data example:
{
    "timestamp": 1708211880,
    "endpoint": "http://pemilu2024.kpu.go.id/pilpres/hitung-suara/17/1701/170108/1701082005/1701082005001",
    "sirekap_endpoint": "https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/17/1701/170108/1701082005/1701082005001.json"
    "reason": [
        "Jumlah seluruh suara sah dan tidak sah tidak konsisten. Rincian: Jumlah seluruh suara sah dan tidak sah dari data bernilai 226, sedangkan penjumlahan seluruh suara sah (217) dan tidak sah (8) adalah 225.",
        "Jumlah perolehan suara tidak sama dengan jumlah seluruh suara sah. Rincian: Penjumlahan perolehan suara 01 (49), 02 (128), dan 03 (41) bernilai 218, sedangkan jumlah seluruh suara sah bernilai 217."
    ]
}
"""
ENDPOINT_PATTERN = r"https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/(\d{2})/(\d{2}[0-9A-Z]{2})/(\d{2}[0-9A-Z]{2}\d{2})/(\d{2}[0-9A-Z]{2}\d{6})/(\d{2}[0-9A-Z]{2}\d{9}).json"

def sirekap_endpoint_to_kpu_endpoint(sirekap_endpoint):
    match_result = re.match(ENDPOINT_PATTERN, sirekap_endpoint)
    if match_result is None:
        raise ValueError
    
    prov_id = match_result.group(1)
    kota_id = match_result.group(2)
    kec_id = match_result.group(3)
    kel_id = match_result.group(4)
    tps_id = match_result.group(5)

    return f"http://pemilu2024.kpu.go.id/pilpres/hitung-suara/{prov_id}/{kota_id}/{kec_id}/{kel_id}/{tps_id}"

all_data = {}
DEFAULT_TIMESTAMP = 1708211880
def make_data(data, timestamp, sirekap_endpoint, reason_list, id_list):
    if len(id_list) == 0:
        data["timestamp"] = timestamp
        data["endpoint"] = sirekap_endpoint_to_kpu_endpoint(sirekap_endpoint)
        data["sirekap_endpoint"] = sirekap_endpoint
        data["reason"] = reason_list
        return
    
    data["timestamp"] = min(timestamp, data.get("timestamp", DEFAULT_TIMESTAMP))

    summary = data.get("summary", {})
    summary["count"] = summary.get("count", 0) + 1

    summary_reason = summary.get("reason", {})
    for r in reason_list:
        r, _ = r.split(" Rincian: ")
        summary_reason[r] = summary_reason.get(r, 0) + 1
    summary["reason"] = summary_reason

    data_data = data.get("data", {})
    child_id = id_list[0]
    child_data = data_data.get(child_id, {})
    make_data(child_data, timestamp, sirekap_endpoint, reason_list, id_list[1:])

    data_data[child_id] = child_data
    data["data"] = data_data
    data["summary"] = summary

def make_file(folder_path, data):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    child_output_data = {}
    for child_id, child_data in data["data"].items():
        if "summary" in child_data:
            child_output_data[child_id] = child_data["summary"]["count"]
        else:
            child_output_data[child_id] = 1

    output_data = {
        "timestamp": data["timestamp"],
        "summary": data["summary"],
        "data": child_output_data
    }
    with open(f"{folder_path}/all.json", mode="w") as fp:
        json.dump(output_data, fp)

    for child_id, child_data in data["data"].items():
        if "summary" in child_data:
            make_file(f"{folder_path}/{child_id}", child_data)
        else:
            with open(f"{folder_path}/{child_id}.json", mode="w") as fp:
                json.dump(child_data, fp)

with open(raw_invalid_path) as fp:
    for line in fp:
        json_data = json.loads(line)
        timestamp = json_data.get("timestamp", DEFAULT_TIMESTAMP)
        url = json_data["url"]
        match_result = re.match(ENDPOINT_PATTERN, url)
        if match_result is None:
            print(f"Warning: URL {url} is ignored because of unexpected format")
            continue
        
        prov_id = match_result.group(1)
        kota_id = match_result.group(2)
        kec_id = match_result.group(3)
        kel_id = match_result.group(4)
        tps_id = match_result.group(5)

        reason_list = json_data["reason"]

        make_data(all_data, timestamp, url, reason_list, [prov_id, kota_id, kec_id, kel_id, tps_id])

make_file(invalid_data_folder_path, all_data)
