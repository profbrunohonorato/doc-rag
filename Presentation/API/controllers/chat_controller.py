from fastapi import APIRouter, Depends, HTTPException, Query
from Application.dto.ask_dto import AskRequest, ReviewRequest
from Infra.IoC.dependencies_helper import get_services

router = APIRouter()


@router.post('/chat/ask')
def ask(body: AskRequest, services=Depends(get_services)):
    return services.rag.ask(body.question, body.top_k)


@router.get('/answers')
def answers(status: str | None = None, offset: int = Query(0, ge=0), services=Depends(get_services)):
    return services.repository.answers(status, offset)


@router.post('/answers/{answer_id}/review')
def review(answer_id: str, body: ReviewRequest, services=Depends(get_services)):
    try:
        return services.repository.review(answer_id, body.decision, body.reviewer, body.note)
    except KeyError:
        raise HTTPException(404, 'Resposta não encontrada')
    except ValueError as exc:
        raise HTTPException(409, str(exc))


@router.get('/audit')
def audit(offset: int = Query(0, ge=0), services=Depends(get_services)):
    return services.repository.audit(offset)
