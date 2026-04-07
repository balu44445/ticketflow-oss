from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.request import RequestStatus, RequestType, TaskStatus


class RequestCreate(BaseModel):
    requester_name: str = Field(..., min_length=2, max_length=120)
    requester_email: EmailStr
    request_type: RequestType
    business_justification: str = Field(..., min_length=5, max_length=1000)


class ApprovalAction(BaseModel):
    approved: bool
    actor: str = Field(..., min_length=2, max_length=120)
    comments: str | None = Field(default=None, max_length=500)


class EventOut(BaseModel):
    id: int
    event_type: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskOut(BaseModel):
    id: int
    assignment_group: str
    short_description: str
    status: TaskStatus
    created_at: datetime

    class Config:
        from_attributes = True


class RequestOut(BaseModel):
    id: int
    requester_name: str
    requester_email: EmailStr
    request_type: RequestType
    business_justification: str
    status: RequestStatus
    manager_approved: bool
    security_approved: bool
    created_at: datetime
    updated_at: datetime
    events: list[EventOut] = []
    tasks: list[TaskOut] = []

    class Config:
        from_attributes = True
