from crewai import Agent
from agentquest.utils import get_configured_llm

def get_consistency_checker() -> Agent:
    return Agent(
        role='Consistency Checker',
        llm=get_configured_llm(),
        goal='Ensure the entire generated game world is geographically and logically consistent.',
        backstory='You are a meticulous editor and logic-checker. You spot contradictions and impossible connections instantly.',
        verbose=True,
        allow_delegation=False,
    )
