import uuid
import hashlib


class FileService:
    def generate_unique_filename(self, original_name: str) -> str:
        ext = ''
        if '.' in original_name:
            ext = '.' + original_name.split('.')[-1]
        return f"{uuid.uuid4().hex}{ext}"

    def calculate_file_hash(self, path: str) -> str:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
