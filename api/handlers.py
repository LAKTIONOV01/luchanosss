from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import *
from db.models import User
from db.session import async_session, get_db
from db.dals import UserDAL
from typing import Union, List
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from hashing import Hasher
import settings
from jose import jwt, JWTError
from security import create_access_token
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm

user_router = APIRouter()
login_router = APIRouter()


async def _create_new_user(body: UserCreate, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
                hashed_password=Hasher.get_password_hash(body.password)
            )
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )

async def _delete_user(user_id, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            deleted_user_id = await user_dal.delete_user(
                user_id=user_id
            )
            return deleted_user_id

async def _get_user_by_id(user_id, db) -> Union[ShowUser, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get_user_by_id(
                user_id=user_id
            )
            if user is not None:
                return ShowUser(
                    user_id=user.user_id,
                    name=user.name,
                    surname=user.surname,
                    email=user.email,
                    is_active=user.is_active
                )

async def _update_user(body: dict, user_id: UUID, db) -> Union[UUID, None]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            updated_user_id = await user_dal.update_user(
                user_id=user_id,
                **body
            )
            return updated_user_id

async def _get_all_users(db) -> [ShowUser]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            all_users = await user_dal.get_all_users()
            return all_users




@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as e:
        raise HTTPException(status_code=503, detail=f'Database error: {e}')


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(status_code=404, detail=f'User with id {user_id} not found')
    return DeleteUserResponse(deleted_user_id=deleted_user_id)

@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowUser:
   user = await _get_user_by_id(user_id, db)
   if user is None:
       raise HTTPException(status_code=404, detail=f'User with id {user_id} not found')
   return user


@user_router.get("/all")
async def get_all_users(db: AsyncSession = Depends(get_db)) -> ShowUser:
   users = await _get_all_users(db)
   if users is None:
       raise HTTPException(status_code=404, detail=f'Usersnot found')
   return users


@user_router.patch("/", response_model=UpdateUserResponse)
async def get_user_by_id(user_id: UUID, body: UpdateUserRequest, db: AsyncSession = Depends(get_db)) -> UpdateUserResponse:
    if body.dict(exclude_none=True) == {}:
        raise HTTPException(status_code=422)
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404)
    try:
        updated_user_id = await _update_user(
            body=body, db=db, user_id=user_id
        )
    except IntegrityError as err:
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdateUserResponse(updated_user_id=updated_user_id)

async def _get_user_by_email_for_auth(email: str, db: AsyncSession):
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            return await user_dal.get_user_by_email(
                email=email
            )
async def authenticate_user(email: str, password: str, db: AsyncSession):
    user = await _get_user_by_email_for_auth(email=email, db=db)
    if user is None:
        return False
    if not Hasher.verify_password(password, user.hashed_password):
        return False
    return user


@login_router.post("/token", response_model=Token)
async def login_for_access_token(
     form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
 ):
     user = await authenticate_user(form_data.username, form_data.password, db)
     if not user:
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Incorrect username or password",
         )
     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
     access_token = create_access_token(
         data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
         expires_delta=access_token_expires,
     )
     return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login/token')


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials'
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get('sub')
        print("username/email extracted is ", email)
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await _get_user_by_email_for_auth(email=email, db=db)
    if user is None:
        raise credentials_exception
    return user


@login_router.get('/test_auth_endpoints')
async def sample_endpoint_under_jwt(current_user: User = Depends(get_current_user_from_token)):
    return {'success': True, 'current_user': current_user}