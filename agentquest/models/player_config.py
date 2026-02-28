from pydantic import BaseModel
from typing import Optional

class PlayerConfig(BaseModel):
    name: str
    character_class: str
    personality: str
    goal: str
    alignment: str
    backstory: Optional[str] = None
