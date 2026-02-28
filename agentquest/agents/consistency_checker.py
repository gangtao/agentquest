from pathlib import Path
from crewai import Agent

def get_consistency_checker() -> Agent:
    return Agent(
        role='Consistency Checker',
        goal='Ensure the entire generated game world is geographically and logically consistent.',
        backstory='You are a meticulous editor and logic-checker. You spot contradictions and impossible connections instantly.',
        verbose=True,
        allow_delegation=False,
    )
