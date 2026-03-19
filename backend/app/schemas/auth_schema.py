from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    dni: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class UserPayload(BaseModel):
    user_id: int
    email: str
    rol: str
