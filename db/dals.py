from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from typing import Union
from uuid import UUID
from sqlalchemy import update, and_, select

###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


class UserDAL:
    """Data Access Layer for operating user info"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, name: str, surname: str, email: str, hashed_password: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = update(User).where(and_(User.user_id == user_id, User.is_active == True)).values(is_active=False).returning(User.user_id)
        res = await self.db_session.execute(query)
        deleted_user = res.fetchone()
        if deleted_user is not None:
            return deleted_user[0]

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]


    async def update_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        query = update(User).where(and_(User.user_id == user_id, User.is_active == True)).values(kwargs).returning(User.user_id)
        res = await self.db_session.execute(query)
        updated_user = res.fetchone()
        if updated_user is not None:
            return updated_user[0]

    async def get_all_users(self):
        try:
            query = select(User)
            result = await self.db_session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            print(f"Ошибка базы данных: {e}")
            return []
        finally:
            await self.db_session.close()
