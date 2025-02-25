import asyncio
import logging
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse

from internal.config import TildaConfig
from internal.tilda_exporter import TildaExporter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация
app = FastAPI(
    title="Tilda Static Page Exporter",
    description="API для экспорта статических страниц из Tilda",
    version="1.0.0"
)

config = TildaConfig()
if not config.is_valid:
    raise RuntimeError("Отсутствуют необходимые переменные окружения")

exporter = TildaExporter(config)

@app.get("/webhook", response_class=PlainTextResponse)
async def handle_webhook(
    publickey: str = Query(..., description="Публичный ключ для верификации")
):
    """Webhook для обработки запросов от Tilda"""
    if publickey != config.public_key:
        raise HTTPException(status_code=403, detail="Неверный публичный ключ")
    
    try:
        await exporter.extract_project(config.project_id)
        return "ok"
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    # Запускаем начальный экспорт при старте
    asyncio.run(exporter.extract_project(config.project_id))
    # Запускаем веб-сервер
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # TODO REMOVE /DOCS!!!
