
import sys
with open('docker-compose.yml', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('postgres:Arzlpzpooler.supabase.com42026@aws-1-us-east-1.pooler.supabase.com:5432', 'postgres.kzgzkhklvemxajgvzgsr:Arzlpzpooler.supabase.com42026@aws-1-us-east-1.pooler.supabase.com:6543')

with open('docker-compose.yml', 'w', encoding='utf-8') as f:
    f.write(text)

