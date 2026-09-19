import json
import re
import sys
import pandas as pd
from kubernetes import client, config

def main():
    # Load the local kubeconfig (connect to minikube)
    try:
        config.load_kube_config()
    except Exception:
        print("Failed to load kube config", file=sys.stderr)
        sys.exit(1)
        
    v1 = client.CoreV1Api()
    
    # Find all pods created by our Job
    pods = v1.list_namespaced_pod(
        namespace="default", 
        label_selector="job-name=shard-validator-job"
    )
    
    if not pods.items:
        print("No pods found for the job.")
        return

    rows = []
    result_re = re.compile(r"RESULT_JSON:(\{.*\})")
    
    for pod in pods.items:
        pod_name = pod.metadata.name
        try:
            logs = v1.read_namespaced_pod_log(name=pod_name, namespace="default")
            match = result_re.search(logs)
            if match:
                result = json.loads(match.group(1))
                rows.append(result)
        except Exception as e:
            print(f"Error reading logs for {pod_name}: {e}")

    # Format and display the results
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("completion_index").reset_index(drop=True)
        print(df.to_string(index=False))
        
        total_invalid = df["invalid_rows"].sum()
        print(f"\nTotal invalid rows across all shards: {total_invalid}")
    else:
        print("No results found in logs.")

if __name__ == "__main__":
    main()
