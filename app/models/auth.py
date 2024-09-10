from pydantic import BaseModel


class AuthBase(BaseModel):
    username: str
    password: str


class AuthQuery(BaseModel):
    jwt: str

