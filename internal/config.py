import os
from dotenv import load_dotenv

load_dotenv()

class TildaConfig:
    """Конфигурация для работы с Tilda API"""
    def __init__(self):
        self.public_key = os.environ.get('TILDA_PUBLIC_KEY')
        self.secret_key = os.environ.get('TILDA_SECRET_KEY')
        self.local_path_prefix = os.environ.get('TILDA_STATIC_PATH_PREFIX', '')
        self.project_id = os.environ.get('TILDA_PROJECT_ID')
        
    @property
    def is_valid(self) -> bool:
        """Проверка валидности конфигурации"""
        return bool(self.public_key and self.secret_key and self.project_id)