from pathlib import Path
import shutil
import tempfile
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile, status

from backend.app.api.dependencies import PreparationServiceDependency
from backend.app.exceptions import InvalidPreparationInputError
from backend.app.schemas import MentorRequest, MentorResponse, PreparationSession


router = APIRouter(prefix="/preparations", tags=["preparations"])


@router.post(
    "",
    response_model=PreparationSession,
    status_code=status.HTTP_201_CREATED,
)
def create_preparation(
    service: PreparationServiceDependency,
    job_url: Annotated[str, Form(min_length=1)],
    cv: Annotated[UploadFile, File()],
    question_limit: Annotated[int, Form(ge=1, le=100)] = 10,
) -> PreparationSession:
    if not cv.filename or Path(cv.filename).suffix.lower() != ".pdf":
        raise InvalidPreparationInputError(
            "O currículo deve ser um arquivo PDF."
        )

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary:
            shutil.copyfileobj(cv.file, temporary)
            temporary_path = Path(temporary.name)

        return service.create(job_url, temporary_path, question_limit)
    finally:
        cv.file.close()
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


@router.get("/{session_id}", response_model=PreparationSession)
def get_preparation(
    session_id: UUID,
    service: PreparationServiceDependency,
) -> PreparationSession:
    return service.get(session_id)


@router.post("/{session_id}/messages", response_model=MentorResponse)
def create_mentor_message(
    session_id: UUID,
    payload: MentorRequest,
    service: PreparationServiceDependency,
) -> MentorResponse:
    messages = [message.model_dump() for message in payload.messages]
    return MentorResponse(message=service.reply(session_id, messages))
