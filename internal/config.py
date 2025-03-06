import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class TildaConfig:
    """Конфигурация для работы с Tilda API"""
    def __init__(self):
        # API ключи
        self.public_key = os.environ.get('TILDA_PUBLIC_KEY')
        self.secret_key = os.environ.get('TILDA_SECRET_KEY')
        self.project_id = os.environ.get('TILDA_PROJECT_ID')
        
        # Настройки сервера
        self.host = os.environ.get('TILDA_HOST', '0.0.0.0')
        self.port = int(os.environ.get('TILDA_PORT', 8000))
        
        # Базовые пути
        self.base_path = os.environ.get('TILDA_STATIC_PATH_PREFIX', 'static/')
        self.paths = {
            'html': Path(os.environ.get('TILDA_HTML_PATH', self.base_path)),
            'images': Path(os.environ.get('TILDA_IMAGES_PATH', self.base_path + 'images/')),
            'css': Path(os.environ.get('TILDA_CSS_PATH', self.base_path + 'css/')),
            'js': Path(os.environ.get('TILDA_JS_PATH', self.base_path + 'js/'))
        }

        # Настройки Git
        self.push_to_git = os.environ.get('PUSH_TO_GIT', 'false').lower() == 'true'
        self.git_username = os.environ.get('GIT_USERNAME')
        self.git_password = os.environ.get('GIT_PASSWORD')
        self.git_remote_url = os.environ.get('GIT_REMOTE_URL')
        self.git_config_name = os.environ.get('GIT_CONFIG_NAME', 'Tilda Exporter')
        self.git_config_email = os.environ.get('GIT_CONFIG_EMAIL', 'tilda-exporter@example.com')
        
    @property
    def is_valid(self) -> bool:
        """Проверка валидности конфигурации"""
        return bool(self.public_key and self.secret_key and self.project_id)
    
    def get_path(self, asset_type: str) -> Path:
        """Получение пути для определенного типа файлов"""
        return self.paths.get(asset_type, self.paths['html'])