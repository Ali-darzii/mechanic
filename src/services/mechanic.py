from src.repositories.mechanic import MechanicRepository

from fastapi import Depends

class MechanicService:
    def __init__(self, repository: MechanicRepository = Depends()):
        self._repository = repository

    def create(self, creeate):
        pass