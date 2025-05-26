from http import HTTPStatus
from fastapi import Depends, FastAPI, HTTPException
from fastapi_zero.database import get_session
from fastapi_zero.models import User

from fastapi_zero.schemas import (
    Message,
    UserDB,
    UserList,
    UserPublic,
    UserSchema,
)

from sqlalchemy import select

app = FastAPI(title='Minha API')

database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session = Depends(get_session)):
       

    db_user = session.scalar(
        select(User).where(User.username == user.username or User.email == user.email)
    )
    if db_user:
        # Retornar erro
        if db_user.username == user.username:
            raise HTTPException(
                status_code= HTTPStatus.CONFLICT,
                detail='Username already exists'
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code= HTTPStatus.CONFLICT,
                detail='Email already exists'
            )

    # Se não der erro
    db_user = User(
        username=user.username,
        email=user.email,
        password=user.password    
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
    return {'users': database}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def update_user(user_id: int, user: UserSchema):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found!'
        )

    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', response_model=Message)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    del database[user_id - 1]

    return {'message': 'User deleted'}


@app.get(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic
)
def get_one_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return database[user_id - 1]
