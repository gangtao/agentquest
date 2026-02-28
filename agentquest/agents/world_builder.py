from pathlib import Path
from crewai import Agent

def get_world_builder() -> Agent:
    return Agent(
        role='World Builder',
        goal='Create a cohesive setting, lore, factions, and locations based on the world seed.',
        backstory='You are a master world-builder for tabletop RPGs, known for creating incredibly immersive and logical fantasy/sci-fi settings.',
        verbose=True,
        allow_delegation=False,
    )
