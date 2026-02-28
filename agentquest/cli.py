import typer
from rich.console import Console
from pathlib import Path
from agentquest.crew.generation_crew import GenerationCrew

app = typer.Typer(help="AgentQuest - Autonomous multi-agent RPG orchestration")
console = Console()

@app.command()
def generate(
    seed: str = typer.Option(..., "--seed", "-s", help="The world seed text prompt"),
    output: str = typer.Option("output", "--output", "-o", help="Directory to save the generated world state"),
):
    """Generate a new game world from a seed prompt."""
    console.print(f"[bold green]Generating world with seed:[/bold green] {seed}")
    crew = GenerationCrew(world_seed=seed, output_dir=Path(output))
    try:
        world_state = crew.run()
        console.print(f"[bold green]World state successfully saved to {Path(output) / 'world_state.json'}![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to generate world:[/bold red] {e}")

import json
import yaml
from agentquest.crew.gameplay_crew import GameplayCrew
from agentquest.models import WorldState, PlayerConfig

@app.command()
def play(
    world: str = typer.Option("output/world_state.json", "--world", "-w", help="Path to the generated world state JSON"),
    players: str = typer.Option("examples/players.yaml", "--players", "-p", help="Path to the players config YAML file"),
    output: str = typer.Option("output/session", "--output", "-o", help="Directory to save session artifacts (game_state, transcript)"),
    rounds: int = typer.Option(3, "--rounds", "-r", help="Number of rounds to play"),
):
    """Play a game session using an existing world and player config."""
    console.print("[bold blue]Starting game session...[/bold blue]")
    console.print(f"Loading world from {world}")
    console.print(f"Loading players from {players}")
    
    try:
        with open(world, 'r') as f:
            world_data = json.load(f)
            world_state = WorldState(**world_data)
            
        with open(players, 'r') as f:
            players_data = yaml.safe_load(f)
            player_configs = [PlayerConfig(**p) for p in players_data.get('players', [])]
            
        crew = GameplayCrew(world_state=world_state, players=player_configs, output_dir=Path(output))
        
        for i in range(rounds):
            if not crew.run_round():
                console.print(f"[bold yellow]Game Over after round {i+1}![/bold yellow]")
                break
                
        console.print(f"[bold green]Session complete! Transcript saved to {Path(output) / 'transcript.md'}[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error running session:[/bold red] {e}")

if __name__ == "__main__":
    app()
