from collections import Counter
import json
import sys
invalid_path = sys.argv[1]

reason_counter = Counter()
with open(invalid_path) as fp:
    for line in fp:
        data = json.loads(line)
        reasons = data["reason"]
        for r in reasons:
            summary, _ = r.split(" Rincian: ")
            reason_counter[summary] += 1

for k, v in reason_counter.items():
    print(f"{k} -> {v}")
