from fastapi import HTTPException, status

from src.models.mechanic_request import MechanicRequestStatus


ALLOWED_MECHANIC_TRANSITION = {
    MechanicRequestStatus.pending: [
        MechanicRequestStatus.confirmed
    ],
    MechanicRequestStatus.confirmed: [
        MechanicRequestStatus.under_repair
    ],
    MechanicRequestStatus.under_repair: [
        MechanicRequestStatus.repaired
    ],
    MechanicRequestStatus.repaired: [
        MechanicRequestStatus.delivered
    ],
    MechanicRequestStatus.delivered: []
}


def validate_transition(current, new):
    if new not in ALLOWED_MECHANIC_TRANSITION[current]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from {current} to {new}"
        )
