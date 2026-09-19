import os
import json
import pandas as pd

def main():
    index = int(os.environ.get("JOB_COMPLETION_INDEX", "0"))
    pod_name = os.environ.get("POD_NAME", "unknown_pod")
    node_name = os.environ.get("NODE_NAME", "unknown_node")

    df = pd.read_csv(f"shards/shard_{index}.csv")
    invalid_count = 0
    for _, row in df.iterrows():
        if pd.isna(row['email']) or '@' not in str(row['email']) or pd.isna(row['name']):
            invalid_count += 1

    result = {
        "completion_index": index,
        "invalid_rows": invalid_count,
        "pod_name": pod_name,
        "node_name": node_name
    }
    print("RESULT_JSON:" + json.dumps(result), flush=True)

if __name__ == "__main__":
    main()
