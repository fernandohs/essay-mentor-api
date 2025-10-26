from pydantic import BaseModel, Field
from typing import Annotated
from .types import MAX_LEN

class EssayRequest(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=MAX_LEN, strip_whitespace=True)]
