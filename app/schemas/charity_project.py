from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from app.schemas.base import BaseDB


class CharityProjectBase(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    full_amount: Optional[PositiveInt] = None

    model_config = ConfigDict(extra='forbid')


class CharityProjectUpdate(CharityProjectBase):

    class Config:
        json_schema_extra = {
            'example': {
                'name': 'Nutrition',
                'description': 'For healthy nutrition for cats',
                'full_amount': 5000
            }
        }


class CharityProjectCreate(CharityProjectUpdate):
    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    full_amount: PositiveInt


class CharityProjectDB(CharityProjectBase, BaseDB):
    pass