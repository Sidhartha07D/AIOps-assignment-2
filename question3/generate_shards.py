import pandas as pd
import numpy as np
import os

os.makedirs("shards", exist_ok=True)
for i in range(8):
    np.random.seed(42 + i)
    df = pd.DataFrame({
        "user_id": range(1, 101),
        "name": ["User" + str(x) for x in range(1, 101)],
        "email": ["user" + str(x) + "@example.com" for x in range(1, 101)]
    })
    
    # Inject random errors
    error_indices = np.random.choice(100, np.random.randint(5, 15), replace=False)
    for idx in error_indices:
        err_type = np.random.choice(["missing_email", "bad_email", "missing_name"])
        if err_type == "missing_email": df.at[idx, "email"] = np.nan
        elif err_type == "bad_email": df.at[idx, "email"] = "invalid-no-at-sign"
        else: df.at[idx, "name"] = np.nan

    df.to_csv(f"shards/shard_{i}.csv", index=False)

print("8 shards generated successfully.")
