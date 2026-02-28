from pydantic import BaseModel

class Location(BaseModel):
    name: str
    description: str
    connected_to: list[str]
    npcs_present: list[str]

class NPC(BaseModel):
    name: str
    role: str
    personality: str
    attitude_toward_party: str  # friendly / neutral / hostile
    backstory: str

class Quest(BaseModel):
    title: str
    description: str
    objectives: list[str]
    twists: list[str]
    is_main_quest: bool

class WorldState(BaseModel):
    seed: str
    setting: str
    lore: str
    factions: list[str]
    locations: list[Location]
    npcs: list[NPC]
    main_quest: Quest
    side_quests: list[Quest]
    consistency_approved: bool
