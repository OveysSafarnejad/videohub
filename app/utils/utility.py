import json
from pydantic import (
    BaseModel,
    error_wrappers
)


def validate_schema(raw_data: dict, SchemaModel: BaseModel):
    data = {}
    errors = []
    msg = None

    try:
        data = SchemaModel(**raw_data)
        data = data.dict()
    except error_wrappers.ValidationError as error:
        msg = error.json()

    if msg:
        try:
            errors = json.loads(msg)
        except Exception as error:
            errors = [{"loc":"non_field_error", "msg":"Unknown"}]

    return data, errors