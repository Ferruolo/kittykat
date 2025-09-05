from typing import TypeVar, Type

import pydantic
from fastapi import HTTPException
from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


def validate_input(input_data: dict, schema: Type[T]) -> T:
    try:
        validated_input = schema(**input_data)
        return validated_input
    except pydantic.ValidationError as e:
        print(e)
        raise HTTPException(status_code=400, detail="Invalid Parameter - please check documentation")

