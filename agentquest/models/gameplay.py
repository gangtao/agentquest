from pydantic import BaseModel
from typing import Optional

class PlayerAction(BaseModel):
    player_name: str
    action: str
    target: Optional[str] = None

class RoundResult(BaseModel):
    narration: str
    state_changes: dict  # diffs applied to GameState
    game_over: bool
    game_over_reason: Optional[str] = None
