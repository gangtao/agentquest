from pydantic import BaseModel

class CharacterState(BaseModel):
    name: str
    hp: int
    max_hp: int
    inventory: list[str]
    status_effects: list[str]

class GameState(BaseModel):
    round_number: int
    current_location: str
    characters: list[CharacterState]
    npc_attitudes: dict[str, str]
    quest_progress: dict[str, bool]
    session_history: list[str]  # last N round summaries for context
