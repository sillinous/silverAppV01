from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    password: str

class UserOut(User):
    # UserOut inherits from User and does not include hashed_password
    # This schema is used for responses to avoid exposing sensitive data.
    pass
