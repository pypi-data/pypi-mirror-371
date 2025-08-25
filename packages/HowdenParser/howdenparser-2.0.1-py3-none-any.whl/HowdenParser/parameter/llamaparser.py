
from typing import Literal
from pydantic import BaseModel

class Hest(BaseModel):
    provider_and_model: str = "huggingface:trocr-large-printed"


class Parameter(BaseModel):
    model1: Hest = Hest()
    provider_and_model: str = "llamaparser:"
    result_type: Literal["md"] = "md"
    mode: bool = False