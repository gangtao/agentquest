from pathlib import Path
from crewai import Agent

def get_character_creator() -> Agent:
    return Agent(
        role='Character Creator',
        goal='Populate the world with interesting NPCs fitting the locations and setting.',
        backstory='You are an expert character writer. You craft NPCs with deep personalities, intertwined backstories, and varied attitudes.',
        verbose=True,
        allow_delegation=False,
    )
