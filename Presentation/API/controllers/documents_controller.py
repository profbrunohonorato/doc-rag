import os
from pathlib import Path
import tempfile
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from Domain.enums import SUPPORTED_EXTENSIONS
from Infra.IoC.dependencies_helper import get_services
from Presentation.API.settings import get_settings

router = APIRouter()


@router.get('/documents')
def documents(services=Depends(get_services)):
    return services.repository.documents()


@router.post('/documents/scan')
def scan(services=Depends(get_services)):
    return services.ingestion.scan()


@router.post('/documents/upload', status_code=201)
def upload(file: UploadFile = File(...)):
    settings = get_settings()
    name = file.filename or ''
    if not name or name != Path(name).name or '\\' in name or name.startswith('.'):
        raise HTTPException(400, 'Nome de arquivo inválido')
    if Path(name).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(415, 'Formato não suportado')
    # Uploads ficam em volume próprio; a pasta apontada pelo usuário é somente leitura.
    root = settings.documents_path.resolve() / '_uploads'
    if root.is_symlink():
        raise HTTPException(400, 'Diretório de uploads inválido')
    root.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=root, suffix='.part', delete=False) as output:
            temporary = output.name
            size = 0
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_file_bytes:
                    raise HTTPException(413, 'Arquivo excede o limite configurado')
                output.write(chunk)
        if not size:
            raise HTTPException(400, 'Arquivo vazio')
        os.replace(temporary, root / name)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
        file.file.close()
    return {'name': '_uploads/' + name, 'status': 'pending'}
