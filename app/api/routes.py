from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.request import ApprovalAction, RequestCreate, RequestOut
from app.services.workflow import (
    InvalidWorkflowAction,
    RequestNotFoundError,
    complete_task,
    create_request,
    get_request,
    list_requests,
    manager_review,
    security_review,
)

router = APIRouter()


@router.post("/requests", response_model=RequestOut, status_code=201)
def create_request_endpoint(payload: RequestCreate, db: Session = Depends(get_db)):
    return create_request(db, payload)


@router.get("/requests", response_model=list[RequestOut])
def list_requests_endpoint(db: Session = Depends(get_db)):
    return list_requests(db)


@router.get("/requests/{request_id}", response_model=RequestOut)
def get_request_endpoint(request_id: int, db: Session = Depends(get_db)):
    try:
        return get_request(db, request_id)
    except RequestNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Request not found") from exc


@router.post("/requests/{request_id}/manager-review", response_model=RequestOut)
def manager_review_endpoint(request_id: int, payload: ApprovalAction, db: Session = Depends(get_db)):
    try:
        return manager_review(db, request_id, payload)
    except RequestNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Request not found") from exc
    except InvalidWorkflowAction as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/requests/{request_id}/security-review", response_model=RequestOut)
def security_review_endpoint(request_id: int, payload: ApprovalAction, db: Session = Depends(get_db)):
    try:
        return security_review(db, request_id, payload)
    except RequestNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Request not found") from exc
    except InvalidWorkflowAction as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/requests/{request_id}/tasks/{task_id}/complete", response_model=RequestOut)
def complete_task_endpoint(request_id: int, task_id: int, actor: str, db: Session = Depends(get_db)):
    try:
        return complete_task(db, request_id, task_id, actor)
    except RequestNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Request not found") from exc
    except InvalidWorkflowAction as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
