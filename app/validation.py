from bson import ObjectId
import json

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError, validator


class CustomBaseModel(BaseModel):
    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectId')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


def object_id_to_str(id: PyObjectId) -> str:
    return str(id)


def str_to_object_id(id: str) -> PyObjectId:
    return PyObjectId(id)


class ObjectIDModel(BaseModel):
    id: PyObjectId

    _str_to_object_id = validator('id', allow_reuse=True)(str_to_object_id)


async def validate_form(request, model):
    errors = {}
    error_str = None

    data = await request.form()
    try:
        data = model(**data).dict()
    except ValidationError as e:
        error_str = e.json()
    if error_str is not None:
        try:
            errors = json.loads(error_str)
        except Exception:
            errors = [{'loc': 'non_field_error', 'msg': 'Unknown error'}]
    return data, errors


def validate_path(model, **param):
    try:
        data = model(**param).dict()
    except ValidationError as e:
        raise RequestValidationError(str(e))
    return data
