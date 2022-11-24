import json

from pydantic import BaseModel, Field, validator
from datetime import datetime

from pydantic.json import isoformat
from pydantic.utils import to_lower_camel
from typing_extensions import Annotated


class DocumentItem(BaseModel):
    product_id: str
    quantity: float
    price: float
    product_name: str
    quantitative_unit: str

    class Config:
        alias_generator = to_lower_camel


def extract_id(raw_id: str) -> str:
    return json.loads(raw_id)['$oid']


class Document(BaseModel):
    id: Annotated[str, Field(alias='_id', )]
    partner_name: str
    validate_stock_availability: bool
    direction: int
    price: float
    owner: str
    status: str
    date: datetime
    items: list[DocumentItem]

    # custom input conversion for that field
    _normalize_id = validator(
        "id",
        allow_reuse=True)(extract_id)
    _normalize_updated_at = validator(
        "date",
        allow_reuse=True)(isoformat)

    class Config:
        alias_generator = to_lower_camel
