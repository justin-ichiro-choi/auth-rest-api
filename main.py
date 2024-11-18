from fastapi import FastAPI

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager


class User(SQLModel, table=True):
    username: str = Field(index=True, primary_key=True)
    hashed_password: str = Field(index=True) 
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
@app.get("/users/{username}&{password}")
async def generate_token(username, password):
    return {"message": "Finished"}

@app.post("/users/")
def create_user(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/")
def see_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users