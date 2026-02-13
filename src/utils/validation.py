from fastapi import HTTPException, status

from src.models.mechanic_car_request import MechanicCarRequestStatus


ALLOWED_MECHANIC_TRANSITION = {
    MechanicCarRequestStatus.pending: [MechanicCarRequestStatus.confirmed],
    MechanicCarRequestStatus.confirmed: [MechanicCarRequestStatus.under_repair],
    MechanicCarRequestStatus.under_repair: [MechanicCarRequestStatus.repaired],
    MechanicCarRequestStatus.repaired: [MechanicCarRequestStatus.delivered],
    MechanicCarRequestStatus.delivered: [],
}


def validate_mechanic_car_status_transition(
    current: MechanicCarRequestStatus, new: MechanicCarRequestStatus
):
    if new not in ALLOWED_MECHANIC_TRANSITION[current]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can't change status from {current} to {new}",
        )
