import os
from pymongo import MongoClient

def load_env(path='backend/.env'):
    env = {}
    with open(path) as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k,v=line.split('=',1)
                env[k]=v
    return env

env = load_env()
uri = env.get('MONGODB_URL')
dbname = env.get('DATABASE_NAME')
print('Using DB:', dbname)
client = MongoClient(uri)
db = client[dbname]
collections = ['restaurants','products','orders','users','reviews','admin','admin_log']
for c in collections:
    try:
        col = db[c]
        cnt = col.count_documents({})
        sample = col.find_one() or {}
        print(f"{c}: {cnt} documents; sample keys: {list(sample.keys())[:10]}")
    except Exception as e:
        print(f"Error reading {c}: {e}")
