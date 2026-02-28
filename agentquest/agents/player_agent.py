from crewai import Agent
from agentquest.models import PlayerConfig
from agentquest.tools import CharacterSheetTool
from agentquest.utils import get_configured_llm

def get_player_agent(player_config: PlayerConfig) -> Agent:
    backstory = f"Class: {player_config.character_class}\\nAlignment: {player_config.alignment}\\nPersonality: {player_config.personality}\\nGoal: {player_config.goal}"
    if player_config.backstory:
        backstory += f"\\nBackstory: {player_config.backstory}"
        
    return Agent(
        role=player_config.name,
        llm=get_configured_llm(),
        goal=f'Act as {player_config.name}, a {player_config.character_class}, and decide your next action based on your personality.',
        backstory=backstory,
        verbose=True,
        allow_delegation=False,
        tools=[CharacterSheetTool()]
    )
