from crewai import Agent
from agentquest.utils import get_configured_llm

def get_quest_designer() -> Agent:
    return Agent(
        role='Quest Designer',
        llm=get_configured_llm(),
        goal='Design one main epic quest and multiple engaging side quests.',
        backstory='You are a veteran campaign designer. You excel at weaving interesting plot twists, complex faction dynamics, and dramatic story arcs.',
        verbose=True,
        allow_delegation=False,
    )
