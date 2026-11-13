import asyncio
import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from Infra.IoC.dependencies_helper import get_services
from Presentation.API.settings import get_settings
from Presentation.API.security import require_access
from Presentation.API.controllers.documents_controller import router as documents
from Presentation.API.controllers.chat_controller import router as chat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('doc-rag')


async def watch(services, stop):
    while not stop.is_set():
        try:
            await asyncio.to_thread(services.ingestion.scan)
        except Exception as exc:
            logger.error('scan_failed type=%s', type(exc).__name__)
        try:
            await asyncio.wait_for(stop.wait(), timeout=get_settings().scan_interval)
        except TimeoutError:
            pass


@asynccontextmanager
async def lifespan(app):
    services = get_services()
    services.db.initialize()
    get_settings().documents_path.mkdir(parents=True, exist_ok=True)
    stop = asyncio.Event()
    worker = asyncio.create_task(watch(services, stop))
    yield
    stop.set()
    await worker
    services.ai.close()
    services.db.dispose()
    get_services.cache_clear()


app = FastAPI(title='Doc RAG', version='0.1.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=get_settings().cors_origins,
                   allow_methods=['GET', 'POST'], allow_headers=['Authorization', 'Content-Type'])


@app.middleware('http')
async def request_context(request: Request, call_next):
    request_id = str(uuid.uuid4())
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error('request_failed id=%s type=%s', request_id, type(exc).__name__)
        response = JSONResponse(status_code=503, content={'detail': 'Serviço indisponível. Confira os modelos e logs.',
                                                         'request_id': request_id})
    response.headers['X-Request-ID'] = request_id
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    return response


prefix = '/doc-rag/api/v1'
app.include_router(documents, prefix=prefix, dependencies=[Depends(require_access)])
app.include_router(chat, prefix=prefix, dependencies=[Depends(require_access)])


@app.get(prefix + '/health/live')
def live():
    return {'status': 'ok'}


@app.get(prefix + '/health/ready', dependencies=[Depends(require_access)])
def ready(services=Depends(get_services)):
    try:
        with services.db.engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        if not services.ai.ready():
            raise ValueError('Modelos ainda não disponíveis')
        services.vectors.collection.count()
        return {'status': 'ok'}
    except Exception:
        return JSONResponse(status_code=503, content={'status': 'starting', 'detail': 'Aguardando banco, índice ou modelos'})
