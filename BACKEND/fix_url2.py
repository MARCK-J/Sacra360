import sys

with open("docker-compose.yml", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    "postgres:password@aws-1-us-east-1.pooler.supabase.com:5432", 
    "postgres.user:password@aws-1-us-east-1.pooler.supabase.com:6543"
)

with open("docker-compose.yml", "w", encoding="utf-8") as f:
    f.write(text)

with open(".env", "r", encoding="utf-8") as f:
    env_text = f.read()

env_text = env_text.replace(
    "postgres:password@db.example.supabase.co:5432", 
    "postgres.user:password@aws-1-us-east-1.pooler.supabase.com:6543"
)
env_text = env_text.replace(
    "postgres:password@aws-1-us-east-1.pooler.supabase.com:5432", 
    "postgres.user:password@aws-1-us-east-1.pooler.supabase.com:6543"
)

with open(".env", "w", encoding="utf-8") as f:
    f.write(env_text)

print("Done")