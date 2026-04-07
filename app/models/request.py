from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class RequestType(str, Enum):
    LAPTOP = "laptop"
    SOFTWARE = "software"
    VPN = "vpn"


class RequestStatus(str, Enum):
    SUBMITTED = "submitted"
    PENDING_MANAGER = "pending_manager"
    PENDING_SECURITY = "pending_security"
    APPROVED = "approved"
    REJECTED = "rejected"
    FULFILLMENT_IN_PROGRESS = "fulfillment_in_progress"
    CLOSED = "closed"


class TaskStatus(str, Enum):
    OPEN = "open"
    COMPLETED = "completed"


class ITRequest(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    requester_name: Mapped[str] = mapped_column(String(120), nullable=False)
    requester_email: Mapped[str] = mapped_column(String(200), nullable=False)
    request_type: Mapped[RequestType] = mapped_column(SAEnum(RequestType), nullable=False)
    business_justification: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        SAEnum(RequestStatus), default=RequestStatus.PENDING_MANAGER, nullable=False
    )
    manager_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    security_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    events: Mapped[list["RequestEvent"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["FulfillmentTask"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )


class RequestEvent(Base):
    __tablename__ = "request_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    request: Mapped[ITRequest] = relationship(back_populates="events")


class FulfillmentTask(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"), nullable=False)
    assignment_group: Mapped[str] = mapped_column(String(120), nullable=False)
    short_description: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), default=TaskStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    request: Mapped[ITRequest] = relationship(back_populates="tasks")
