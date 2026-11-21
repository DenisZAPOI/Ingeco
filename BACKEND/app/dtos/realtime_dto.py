"""
Messages received on the real-time channel (contract, part 5).

Validated like the bodies of the HTTP routes: same camelCase, unknown fields refused.
"""

from pydantic import Field

from .base import ApiModel, InputModel


class FollowRideInput(InputModel):
    """ride:follow and ride:unfollow: the ride whose changes the page wants to hear of."""

    ride_id: int = Field(gt=0)


class SubscriptionAck(ApiModel):
    """Answer to a subscription: refused when the caller may not read the ride (or the offers)."""

    accepted: bool
