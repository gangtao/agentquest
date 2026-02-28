from pathlib import Path
from crewai import Agent
from agentquest.tools import DiceRollerTool, WorldStateTool

def get_dm_agent() -> Agent:
    return Agent(
        role='Dungeon Master',
        goal='Orchestrate the game round, collect player actions, resolve outcomes, and narrate the scene.',
        backstory='You are a master storyteller and fair adjudicator of rules. You keep the game challenging but fun.',
        verbose=True,
        allow_delegation=True,
        tools=[DiceRollerTool(), WorldStateTool()]
    )
