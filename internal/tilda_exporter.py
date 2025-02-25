import logging
from pathlib import Path
from typing import List

import requests
from pydantic import BaseModel, Field
from requests.exceptions import RequestException

from internal.config import TildaConfig

logger = logging.getLogger(__name__)

class TildaAsset(BaseModel):
    """Модель для ассетов Tilda"""
    from_url: str = Field(None, alias='from')
    to_path: str = Field(alias='to')
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }

class TildaPage(BaseModel):
    """Модель страницы"""
    id: str
    title: str
    filename: str
    
class TildaPageExport(BaseModel):
    """Модель экспорта страницы"""
    html: str
    filename: str
    images: List[TildaAsset]
    js: List[TildaAsset]
    css: List[TildaAsset]

class TildaExporter:
    """Экспортер статических страниц из Tilda"""
    
    def __init__(self, config: TildaConfig):
        self.config = config
        
    def _save_file(self, source_url: str, local_path: Path) -> None:
        """Сохранение файла"""
        try:
            response = requests.get(source_url, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except RequestException as e:
            logger.error(f"Ошибка при сохранении {source_url}: {e}")
            raise

    def _process_assets(self, assets: List[dict], asset_type: str) -> None:
        """Обработка ассетов"""
        for asset_dict in assets:
            try:
                source_url = asset_dict['from']
                local_path = Path(self.config.local_path_prefix) / Path(asset_dict['to'])
                local_path.parent.mkdir(parents=True, exist_ok=True)
                self._save_file(source_url, local_path)
            except Exception as e:
                logger.error(f"Ошибка обработки {asset_type} {asset_dict.get('from', 'unknown')}: {e}")

    async def extract_project(self, project_id: str) -> None:
        """Экспорт проекта"""
        logger.info(f"Начало экспорта проекта {project_id}")
        
        try:
            # Получаем информацию о проекте
            project_info = requests.get(
                'https://api.tildacdn.info/v1/getprojectinfo/',
                params={
                    'projectid': project_id,
                    'publickey': self.config.public_key,
                    'secretkey': self.config.secret_key
                }
            )
            project_info.raise_for_status()
            project_data = project_info.json()['result']
            self._process_assets(project_data['images'], 'images')

            # Получаем список страниц
            pages_list = requests.get(
                'https://api.tildacdn.info/v1/getpageslist/',
                params={
                    'projectid': project_id,
                    'publickey': self.config.public_key,
                    'secretkey': self.config.secret_key
                }
            )
            pages_list.raise_for_status()

            # Обрабатываем страницы
            for page in [TildaPage.model_validate(p) for p in pages_list.json()['result']]:
                await self._extract_page(project_id, page)
                
            logger.info(f"Проект {project_id} экспортирован")
            
        except Exception as e:
            logger.error(f"Ошибка экспорта проекта {project_id}: {e}")
            raise

    async def _extract_page(self, project_id: str, page: TildaPage) -> None:
        """Экспорт страницы"""
        try:
            page_info = requests.get(
                'https://api.tildacdn.info/v1/getpagefullexport/',
                params={
                    'projectid': project_id,
                    'pageid': page.id,
                    'publickey': self.config.public_key,
                    'secretkey': self.config.secret_key
                }
            )
            page_info.raise_for_status()
            
            result = page_info.json()['result']
            
            # Обрабатываем ассеты
            self._process_assets(result['images'], 'images')
            self._process_assets(result['js'], 'scripts')
            self._process_assets(result['css'], 'styles')

            # Сохраняем HTML
            html_path = Path(self.config.local_path_prefix) / result['filename']
            html_path.parent.mkdir(parents=True, exist_ok=True)
            html_path.write_text(result['html'], encoding='utf-8')
            
            logger.info(f"Страница {page.id} экспортирована")
            
        except Exception as e:
            logger.error(f"Ошибка экспорта страницы {page.id}: {e}")
            raise 