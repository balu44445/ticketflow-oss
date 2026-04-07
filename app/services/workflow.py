from sqlalchemy.orm import Session, selectinload

from app.models.request import FulfillmentTask, ITRequest, RequestEvent, RequestStatus, RequestType, TaskStatus
from app.schemas.request import ApprovalAction, RequestCreate


TASK_GROUPS = {
    RequestType.LAPTOP: "endpoint-support",
    RequestType.SOFTWARE: "application-support",
    RequestType.VPN: "network-security",
}


class RequestNotFoundError(Exception):
    pass


class InvalidWorkflowAction(Exception):
    pass


def add_event(db: Session, request: ITRequest, event_type: str, message: str) -> None:
    db.add(RequestEvent(request_id=request.id, event_type=event_type, message=message))


def create_request(db: Session, payload: RequestCreate) -> ITRequest:
    req = ITRequest(
        requester_name=payload.requester_name,
        requester_email=payload.requester_email,
        request_type=payload.request_type,
        business_justification=payload.business_justification,
        status=RequestStatus.PENDING_MANAGER,
    )
    db.add(req)
    db.flush()
    add_event(db, req, "request_created", f"Request submitted by {payload.requester_name}.")
    db.commit()
    return get_request(db, req.id)


def get_request(db: Session, request_id: int) -> ITRequest:
    req = (
        db.query(ITRequest)
        .options(selectinload(ITRequest.events), selectinload(ITRequest.tasks))
        .filter(ITRequest.id == request_id)
        .first()
    )
    if not req:
        raise RequestNotFoundError()
    req.events.sort(key=lambda e: e.created_at)
    req.tasks.sort(key=lambda t: t.id)
    return req


def list_requests(db: Session) -> list[ITRequest]:
    rows = db.query(ITRequest).order_by(ITRequest.id.desc()).all()
    return rows


def manager_review(db: Session, request_id: int, payload: ApprovalAction) -> ITRequest:
    req = get_request(db, request_id)
    if req.status != RequestStatus.PENDING_MANAGER:
        raise InvalidWorkflowAction("Manager review is not allowed in the current state.")

    req.manager_approved = payload.approved
    if not payload.approved:
        req.status = RequestStatus.REJECTED
        add_event(db, req, "manager_rejected", f"Manager {payload.actor} rejected the request.")
    elif req.request_type == RequestType.VPN:
        req.status = RequestStatus.PENDING_SECURITY
        add_event(db, req, "manager_approved", f"Manager {payload.actor} approved the request.")
    else:
        req.status = RequestStatus.APPROVED
        add_event(db, req, "manager_approved", f"Manager {payload.actor} approved the request.")
        create_fulfillment_task(db, req)

    db.commit()
    return get_request(db, request_id)


def security_review(db: Session, request_id: int, payload: ApprovalAction) -> ITRequest:
    req = get_request(db, request_id)
    if req.status != RequestStatus.PENDING_SECURITY:
        raise InvalidWorkflowAction("Security review is not allowed in the current state.")

    req.security_approved = payload.approved
    if not payload.approved:
        req.status = RequestStatus.REJECTED
        add_event(db, req, "security_rejected", f"Security reviewer {payload.actor} rejected the request.")
    else:
        req.status = RequestStatus.APPROVED
        add_event(db, req, "security_approved", f"Security reviewer {payload.actor} approved the request.")
        create_fulfillment_task(db, req)

    db.commit()
    return get_request(db, request_id)


def create_fulfillment_task(db: Session, req: ITRequest) -> None:
    task = FulfillmentTask(
        request_id=req.id,
        assignment_group=TASK_GROUPS[req.request_type],
        short_description=f"Fulfill {req.request_type.value} request for {req.requester_name}",
    )
    db.add(task)
    req.status = RequestStatus.FULFILLMENT_IN_PROGRESS
    add_event(db, req, "task_created", f"Task created for assignment group {task.assignment_group}.")


def complete_task(db: Session, request_id: int, task_id: int, actor: str) -> ITRequest:
    req = get_request(db, request_id)
    task = next((t for t in req.tasks if t.id == task_id), None)
    if not task:
        raise InvalidWorkflowAction("Task not found for this request.")
    if task.status == TaskStatus.COMPLETED:
        raise InvalidWorkflowAction("Task is already completed.")

    task.status = TaskStatus.COMPLETED
    add_event(db, req, "task_completed", f"Task {task_id} completed by {actor}.")

    if all(t.status == TaskStatus.COMPLETED for t in req.tasks):
        req.status = RequestStatus.CLOSED
        add_event(db, req, "request_closed", "All fulfillment tasks completed. Request closed.")

    db.commit()
    return get_request(db, request_id)
