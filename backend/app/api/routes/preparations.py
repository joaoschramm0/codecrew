from pathlib import Path
import shutil
import tempfile
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile, status

from backend.app.api.dependencies import PreparationServiceDependency
from backend.app.exceptions import InvalidPreparationInputError
from backend.app.schemas import AnswerRequest, MentorRequest, MentorResponse, MentorshipPublic, PreparationPublic

router = APIRouter(prefix="/preparations", tags=["preparations"])

@router.post("", response_model=PreparationPublic, status_code=status.HTTP_201_CREATED)
def create_preparation(service: PreparationServiceDependency, job_url: Annotated[str, Form(min_length=1)], cv: Annotated[UploadFile, File()]) -> PreparationPublic:
    if not cv.filename or Path(cv.filename).suffix.lower() != ".pdf":
        raise InvalidPreparationInputError("O currículo deve ser um arquivo PDF.")
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary:
            shutil.copyfileobj(cv.file, temporary)
            temporary_path = Path(temporary.name)
        return service.create(job_url, temporary_path, 3)
    finally:
        cv.file.close()
        if temporary_path:
            temporary_path.unlink(missing_ok=True)

@router.get("/{session_id}", response_model=PreparationPublic)
def get_preparation(session_id: UUID, service: PreparationServiceDependency) -> PreparationPublic:
    return service.get(session_id)

@router.put("/{session_id}/diagnostic/answers/{question_id}", response_model=PreparationPublic)
def save_answer(session_id: UUID, question_id: str, payload: AnswerRequest, service: PreparationServiceDependency) -> PreparationPublic:
    return service.save_answer(session_id, question_id, payload)

@router.post("/{session_id}/diagnostic/submit", response_model=PreparationPublic)
def submit_diagnostic(session_id: UUID, service: PreparationServiceDependency) -> PreparationPublic:
    return service.submit(session_id)

@router.post("/{session_id}/diagnostic/retry", response_model=PreparationPublic)
def retry_diagnostic(session_id: UUID, service: PreparationServiceDependency) -> PreparationPublic:
    return service.retry(session_id)

@router.get("/{session_id}/challenges", response_model=list)
def get_challenges(session_id: UUID, service: PreparationServiceDependency):
    return service.get(session_id).recommendations

@router.get("/{session_id}/mentorships/{challenge_slug}", response_model=MentorshipPublic)
def get_mentorship(session_id: UUID, challenge_slug: str, service: PreparationServiceDependency):
    return service.mentorship(session_id, challenge_slug)

@router.post("/{session_id}/messages", response_model=MentorResponse)
def create_mentor_message(session_id: UUID, payload: MentorRequest, service: PreparationServiceDependency) -> MentorResponse:
    mentorship = service.reply(session_id, payload.challenge_slug, payload.message)
    return MentorResponse(message=mentorship.messages[-1], help_stage=mentorship.help_stage)
