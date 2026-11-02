"""
Cursor of a paginated list (rides, accounts): opaque for the phone, which
sends it back as is. Inside, the creation time and the id of the last item of
the page: the next page starts after them (keyset pagination).
"""

import base64
import binascii
from datetime import datetime

_SEPARATOR = "|"
INVALID_CURSOR = "Lien de page invalide. Rechargez la liste."


def encode(created_at: datetime, item_id: int) -> str:
    raw = f"{created_at.isoformat()}{_SEPARATOR}{item_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode(cursor: str) -> tuple[datetime, int]:
    """ValueError if the cursor was not made by encode()."""
    try:
        created_at, item_id = base64.urlsafe_b64decode(cursor.encode()).decode().split(_SEPARATOR)
        position = datetime.fromisoformat(created_at), int(item_id)
    except (binascii.Error, UnicodeDecodeError, ValueError):
        raise ValueError(INVALID_CURSOR) from None
    if position[0].tzinfo is None:
        raise ValueError(INVALID_CURSOR)
    return position
