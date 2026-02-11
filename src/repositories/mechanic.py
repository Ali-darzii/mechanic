from src.repositories.base import SqlRepository
from src.models.mechanic import Mechanic as MechanicModel



class MechanicRepository(SqlRepository):
    model  = MechanicModel

    
