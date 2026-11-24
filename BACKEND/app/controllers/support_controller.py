"""Help requests ("Être rappelé", module M0)."""

from flask import Blueprint, jsonify, request
from flask_pydantic_spec import Response

from ..dtos.base import ErrorDto
from ..dtos.support_dto import CallbackBody, CallbackListDto, callbacks_to_dto
from ..extensions import spec
from ..services import support_service
from ..utils.access import current_user_id, optional_user_id, require_login

# The people who call back: the call centre and the administrators.
_STAFF = ("operator", "admin")

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


@support_bp.get("/callbacks")
@require_login(*_STAFF)
@spec.validate(resp=Response(HTTP_200=CallbackListDto, HTTP_401=ErrorDto, HTTP_403=ErrorDto), tags=_TAGS)
def list_callbacks():
    """The callbacks to make, the oldest first (operator, administrator)."""
    callbacks = support_service.open_callbacks()
    return jsonify(callbacks_to_dto(callbacks).to_json()), 200


@support_bp.post("/<int:request_id>/handled")
@require_login(*_STAFF)
@spec.validate(resp=Response(HTTP_204=None, HTTP_401=ErrorDto, HTTP_403=ErrorDto, HTTP_404=ErrorDto), tags=_TAGS)
def mark_handled(request_id: int):
    """Called back: the request leaves the list; it is deleted 3 months later."""
    support_service.mark_callback_handled(staff_id=current_user_id(), request_id=request_id)
    return "", 204
