from collections import Counter
import json
import sys
incomplete_path = sys.argv[1]

reason_counter = Counter()
with open(incomplete_path) as fp:
    for line in fp:
        data = json.loads(line)
        reasons = data["reason"]
        for r in reasons:
            reason_counter[r] += 1

for k, v in reason_counter.items():
    print(f"{k} -> {v}")
