import urllib.request
import json
import os

url = "http://127.0.0.1:5050/analyze"
ddl_path = "column-volatility-analyzer/sample_ddl_130cols.sql"

with open(ddl_path, "r") as f:
    ddl = f.read()

data = json.dumps({"ddl": ddl, "dialect": "snowflake"}).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req) as f:
        res = json.loads(f.read().decode("utf-8"))
        print("✅ Success")
        print("Table:", res["parsed"]["table_name"])
        print("\nSQL Snippet (Final Result):")
        print("\n".join(res["sql"].splitlines()[-10:]))
except Exception as e:
    print(f"❌ Error: {e}")
