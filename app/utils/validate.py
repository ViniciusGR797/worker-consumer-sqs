from typing import Type, Union, Tuple
from pydantic import BaseModel, ValidationError


def validate(schema: Type[BaseModel],
             data: dict) -> Tuple[Union[BaseModel, None], Union[str, None]]:
    try:
        validated = schema(**data)
        return validated, None
    except ValidationError as e:
        return None, e.errors()
    except Exception as e:
        return None, str(e)
