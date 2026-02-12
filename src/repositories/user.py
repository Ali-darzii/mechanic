from sqlalchemy import select
from src.models.user import User as UserModel, UserRole
from src.repositories.base import SqlRepository


class UserRepository(SqlRepository):

    model = UserModel

    async def get_by_phone_number(self, phone_number: str) -> UserModel | None:
        result = await self.db.execute(
            select(self.model).where(
                self.model.phone_number == phone_number,
            )
        )
        return result.scalar_one_or_none()

    async def user_status(self, db_obj: UserModel, is_active: bool) -> UserModel:
        db_obj.is_active = is_active

        self.db.add(db_obj)
        await self.db.commit()

        return db_obj

    async def reset_password(self, db_obj: UserModel, password: str) -> UserModel:
        db_obj.password = password

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)

        return db_obj

    async def soft_delete(self, db_obj: UserModel) -> None:
        db_obj.is_delete = False
        db_obj.is_active = False

        self.db.add(db_obj)
        await self.db.commit()

    async def out_of_soft_delete(self, db_obj: UserModel) -> None:
        db_obj.is_delete = True

        self.db.add(db_obj)
        await self.db.commit()

    async def chenge_user_role(self, db_obj: UserModel, role: UserRole) -> UserModel:
        db_obj.role = role

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)

        return db_obj