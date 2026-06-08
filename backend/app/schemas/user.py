from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for user registration input."""

    username: str
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "alice",
                "email": "alice@example.com",
                "password": "securepassword123"
            }
        }


class UserProfile(BaseModel):
    """Schema for returning authenticated user profile data."""

    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    """Schema for updating user profile information."""

    username: str | None = None
    email: EmailStr | None = None

    class Config:
        schema_extra = {
            "example": {
                "username": "alice",
                "email": "alice@example.com"
            }
        }


class ProfileUpdateResponse(BaseModel):
    username: str
    email: EmailStr
    access_token: str | None = None
    token_type: str | None = None

    class Config:
        orm_mode = True
