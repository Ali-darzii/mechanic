import json
from typing import Any, Type, List
from abc import ABC, abstractmethod

from fastapi import Depends
from redis import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.core.redis import get_redis
from src.core.postgres import get_postdb
from src.models.base import Base

class ISqlRepository(ABC):

    model: Type[Base] | None = None

    def __init__(self, db: AsyncSession = Depends(get_postdb)):
        if self.model is None:
            raise NotImplementedError(f"model attribute need to be specified in `{self.__class__.__name__}`")
        
        self.db = db

    @abstractmethod
    async def create(self, schema: Type[BaseModel]) -> Type[Base]:
        pass

    @abstractmethod
    async def update(self, db_obj: Type[Base], schema: Type[BaseModel], partial: bool) -> Type[Base]:
        pass

    @abstractmethod
    async def delete(self, db_obj: Type[Base]) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, pk: int | str) -> Type[Base] | None:
        pass

    @abstractmethod
    async def list_all(self, limit=100, offset=0) -> List[Type[Base]]:
        pass


class SqlRepository(ISqlRepository):

    """
    - Simple Crud opratons from pydantic BaseModel to sql databases.
    - Don't forget rewrite model
    - Needs to use fastAPI Depends in services to can intract with.
    - If need sync method, add `sync` at last of method name.

    Exmaple::

        from fastapi import Depends    
        from src.repositories.base import SqlRepository
        
        class ExampleRepository(SqlRepository):
            model = ExmapleModel 

        class ExmalpeService():
            def __init__(self, repository: Depends(ExampleRepository)):
                self.repository = repository
    
    """

    async def create(self, schema):
        db_obj = self.model(**schema.model_dump())
        
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        return db_obj

    async def update(self, db_obj, schema, partial):
        update_data = schema.model_dump(exclude_unset=partial)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        return db_obj

    async def delete(self, db_obj):
        await self.db.delete(db_obj)
        await self.db.commit()

    async def get_by_id(self, pk):
        result = await self.db.execute(select(self.model).where(self.model.id == pk))
        return result.scalar_one_or_none()
    
    async def list_all(self, limit, offset):
        result = await self.db.execute(select(self.model).limit(limit).offset(offset))
        return result.scalars().all()



class RedisRepository:
    def __init__(self, redis: Redis = Depends(get_redis)):
        self.redis = redis

    async def get(self, key: str) -> Any | None:
        value = await self.redis.get(key)
        if value is not None:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, expire: int | None = None) -> None:
        await self.redis.set(key, json.dumps(value), ex=expire)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def incr(self, key: str) -> int:
        return await self.redis.incr(key)