"""Help requests ("Être rappelé", module M0)."""

from flask import Blueprint, request
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.support_dto import CallbackBody
from ..extensions import spec
from ..services import support_service
from ..utils.access import optional_user_id

support_bp = Blueprint("support", __name__, url_prefix="/help-requests")

_TAGS = ["Aide"]


@support_bp.post("/callback")
@spec.validate(
    body=CallbackBody,
    resp=Response(HTTP_204=None, HTTP_400=ErrorDto, HTTP_401=ErrorDto, HTTP_429=ErrorDto),
    tags=_TAGS,
)
def request_callback():
    """« Être rappelé » : someone of the structure calls this number back.

    Open to visitors; a logged-in caller's request is linked to the account.
    401 only if a session cookie is sent but no longer valid. 429 beyond
    5 requests in an hour from one network address.
    """
    body: CallbackBody = request.context.body
    support_service.request_callback(body.phone, optional_user_id(), request.remote_addr)
    return "", 204
