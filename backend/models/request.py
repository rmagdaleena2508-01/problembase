from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    product: str
    limit: Optional[int] = 10

    class Config:
        json_schema_extra = {
            "example": {
                "product": "Notion",
                "limit": 10
            }
        }
