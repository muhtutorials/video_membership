from pydantic import EmailStr, Field, validator

from app.validation import CustomBaseModel, PyObjectId, object_id_to_str


class UserBase(CustomBaseModel):
    username: str
    email: EmailStr


class UserSignUp(UserBase):
    password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v


class UserSignIn(CustomBaseModel):
    username: str
    password: str


class UserOut(UserBase):
    id: PyObjectId = Field(..., alias='_id')

    _object_id_to_str = validator('id', allow_reuse=True)(object_id_to_str)


class UserToDB(UserBase):
    hashed_password: str


class Token(CustomBaseModel):
    access_token: str
    token_type: str


class TokenData(CustomBaseModel):
    username: str
