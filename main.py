from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager

import bcrypt
from utils import (
    get_hashed_password,
    create_access_token,
    verify_password
)

class UserBase(SQLModel):
    username: str = Field(index=True, primary_key=True)
    hashed_password: str = Field(index=True) 

class User(UserBase, table=True):
    email: str = Field(index=True)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    
app = FastAPI(lifespan=lifespan)

# Default, getting a message to ensure that this works
@app.get("/")
async def running():
    return {"message": "Hello World!"}

# Generates a JWT token and the valid amount of time this is valid for
@app.post('/validate', summary="Create access and refresh tokens for user")
async def login(session: SessionDep, user: UserBase):
    databaseQuery = session.get(User, user.username)

    if databaseQuery is None:
        raise HTTPException(
            status_code=404,
            detail="Incorrect email or password"
        )

    existingPassword = databaseQuery.hashed_password
    providedPassword = user.hashed_password

    if not verify_password(providedPassword, existingPassword):
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )

    return {
        "token": create_access_token("validated: true"),
        "expiration": "600"
    }

@app.post("/reset_password")
async def reset_password(session, SessionDep, User):
    return True

@app.post("/users")
def create_user(user: User, session: SessionDep) -> User:

    check = session.get(User, user.username)

    if check is not None:
        raise HTTPException(
            status_code=400, detail="User with this email already exists!"
        )

    user.hashed_password = get_hashed_password(user.hashed_password)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@app.get("/users")
def see_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@app.delete("/users/{username}", status_code=201)
def delete_user(username: str, session: SessionDep):
    user = session.get(User, username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()
    return {"deleted": "true"} 