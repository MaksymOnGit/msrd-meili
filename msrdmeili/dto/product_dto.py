import json
from typing import Union

from pydantic import BaseModel, Field, validator
from datetime import datetime

from pydantic.json import isoformat
from typing_extensions import Annotated


def extract_id(raw_id: str) -> str:
    return json.loads(raw_id)['$oid']


class Product(BaseModel):

    id: Annotated[str, Field(alias='_id', )]
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    price: Union[float, None]
    quantity: Union[float, None]
    quantitative_unit: Union[str, None]

    # custom input conversion for that field
    _normalize_id = validator(
        "id",
        allow_reuse=True)(extract_id)
    _normalize_updated_at = validator(
        "updated_at",
        allow_reuse=True)(isoformat)
    _normalize_created_at = validator(
        "created_at",
        allow_reuse=True)(isoformat)
