import asyncio
import logging
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, Query, HTTPException, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager

from internal.committer import Committer
from internal.config import TildaConfig
from internal.tilda_exporter import TildaExporter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Действия при запуске и завершении работы сервера"""
    # Код выполняемый при запуске
    logger.info(f"Запуск сервера на {config.host}:{config.port}")
    logger.info(f"Конфигурация загружена для проекта {config.project_id}")
    try:
        logger.info("Выполняем начальный экспорт проекта")
        logger.info("Пути сохранения файлов:")
        logger.info(f"  HTML: {config.get_path('html')}")
        logger.info(f"  Images: {config.get_path('images')}")
        logger.info(f"  CSS: {config.get_path('css')}")
        logger.info(f"  JS: {config.get_path('js')}")
        await exporter.extract_project(config.project_id)
        logger.info("Начальный экспорт завершен успешно")
        
        # Создаем коммит при старте
        try:
            if config.push_to_git:
                logger.info("Git push отключен")
                # logger.info("Создаем коммит при старте сервера")
                # committer = Committer(config)
                # committer.commit_changes("Автоматический коммит при старте сервера")
                # logger.info("Коммит при старте создан успешно")
        except Exception as e:
            logger.error(f"Ошибка при создании коммита: {str(e)}")
            # Продолжаем работу даже если коммит не удался
            pass
            
    except Exception as e:
        logger.error(f"Ошибка при начальном экспорте: {e}", exc_info=True)
        raise
    
    yield  # Здесь приложение работает
    
    # Код выполняемый при завершении работы
    logger.info("Завершение работы сервера")

# Инициализация
app = FastAPI(
    title="Tilda Static Page Exporter",
    description="API для экспорта статических страниц из Tilda",
    version="1.0.0",
    lifespan=lifespan
)

config = TildaConfig()
if not config.is_valid:
    raise RuntimeError("Отсутствуют необходимые переменные окружения")

exporter = TildaExporter(config)

async def process_webhook_data(projectid: str, pageid: Optional[str], published: Optional[str]):
    """Фоновая обработка данных вебхука"""
    try:
        logger.info(f"Начало фоновой обработки webhook для проекта {projectid}")
        logger.info(f"Параметры: pageid={pageid}, published={published}")
        logger.info(f"Пути сохранения файлов:")
        logger.info(f"  HTML: {config.get_path('html')}")
        logger.info(f"  Images: {config.get_path('images')}")
        logger.info(f"  CSS: {config.get_path('css')}")
        logger.info(f"  JS: {config.get_path('js')}")
        
        await exporter.extract_project(projectid)
        
        # Создаем коммит только если включен push_to_git
        if config.push_to_git:
            logger.info("Git push отключен")
            # current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # commit_message = f"Автоматическое обновление от Tilda {current_date}"
            # committer = Committer(config)
            # committer.commit_changes(commit_message)
            # logger.info("Git push выполнен успешно")
        else:
            logger.info("Git push пропущен (PUSH_TO_GIT=false)")
        
        logger.info(f"Фоновая обработка webhook завершена успешно")
    except Exception as e:
        logger.error(f"Ошибка при фоновой обработке webhook: {e}", exc_info=True)

async def export_project():
    try:
        logger.info(f"Начало экспорта файлов")
        if config.push_to_git:
            logger.info("Git push отключен")
            # committer = Committer(config)
            # committer.commit_changes()
            # logger.info("Git push выполнен успешно")
        else:
            logger.info("Git push пропущен (PUSH_TO_GIT=false)")
        logger.info(f"Экспорт завершен успешно")
    except Exception as e:
        logger.error(f"Ошибка при экспорте файлов: {e}", exc_info=True)

@app.get("/webhook", response_class=PlainTextResponse)
async def handle_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    projectid: str = Query(..., description="ID проекта Tilda"),
    publickey: str = Query(..., description="Публичный ключ для верификации"),
    pageid: Optional[str] = Query(None, description="ID страницы"),
    published: Optional[str] = Query(None, description="Время публикации")
):
    """Webhook для обработки запросов от Tilda"""
    client_host = request.client.host
    logger.info(f"Получен webhook запрос от {client_host}")
    logger.info(f"Параметры запроса: {dict(request.query_params)}")
    
    if publickey != config.public_key:
        logger.warning(f"Попытка доступа с неверным ключом от {client_host}")
        raise HTTPException(status_code=403, detail="Неверный публичный ключ")
    
    # Добавляем задачу в фоновую обработку и сразу возвращаем ответ
    background_tasks.add_task(process_webhook_data, projectid, pageid, published)
    logger.info(f"Webhook запрос принят в обработку")
    return "ok"

if __name__ == '__main__':
    uvicorn.run(app, host=config.host, port=config.port)
    # TODO REMOVE /DOCS!!!
