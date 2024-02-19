import sys
import json
from validation import get_validation_result

input_path = sys.argv[1]
incomplete_path = sys.argv[2]
invalid_path = sys.argv[3]
next_url_path = sys.argv[4]

count = 0
incomplete_count = 0
invalid_count = 0
next_url_count = 0
with (
        open(input_path) as input_fp,
        open(incomplete_path, mode="w") as incomplete_fp,
        open(invalid_path, mode="w") as invalid_fp,
        open(next_url_path, mode="w") as next_url_fp,
):
    for line in input_fp:
        if not line.startswith("{\"url\":"):
            raise ValueError(f"Unexpected line: {line}")
        
        count += 1

        json_data = json.loads(line)
        url = json_data["url"]
        data = json_data["data"]
        validation_result = get_validation_result(data)
        status = validation_result["status"]
        if status == "valid":
            continue

        json_data["reason"] = validation_result["reason"]
        dumped_json_data = json.dumps(json_data)
        if status == "incomplete":
            print(dumped_json_data, file=incomplete_fp)
            incomplete_count += 1

            print(url, file=next_url_fp)
            next_url_count += 1

        elif status == "invalid":
            print(dumped_json_data, file=invalid_fp)
            invalid_count += 1

            print(url, file=next_url_fp)
            next_url_count += 1

        else:
            raise ValueError(f"Unexpected status: {status}")

print(f"{count=}")
print(f"{incomplete_count=}")
print(f"{invalid_count=}")
print(f"{next_url_count=}")