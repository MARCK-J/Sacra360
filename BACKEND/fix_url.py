
import sys
with open('docker-compose.yml', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('postgres:password@aws-1-us-east-1.pooler.supabase.com:5432', 'postgres.user:password@aws-1-us-east-1.pooler.supabase.com:6543')

with open('docker-compose.yml', 'w', encoding='utf-8') as f:
    f.write(text)

