from pydantic import BaseModel, EmailStr, Field, ConfigDict


class AdminCreateUser(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=8, max_length=72)
    role: str = Field(pattern="^(Admin|Doctor)$")


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)