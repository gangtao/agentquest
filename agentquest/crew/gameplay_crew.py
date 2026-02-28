from pathlib import Path
from crewai import Crew, Task, Process
from agentquest.agents import get_dm_agent, get_player_agent
from agentquest.models import WorldState, PlayerConfig, GameState, CharacterState

class GameplayCrew:
    """
    Looping crew that runs the live game session.
    DM agent orchestrates each round; Player agents respond independently.
    Maintains and persists game_state.json across rounds.
    """
    def __init__(self, world_state: WorldState, players: list[PlayerConfig], output_dir: Path):
        self.world_state = world_state
        self.players_config = players
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.game_state_path = self.output_dir / "game_state.json"
        self.transcript_path = self.output_dir / "transcript.md"
        
        self.dm_agent = get_dm_agent()
        self.player_agents = [get_player_agent(p) for p in self.players_config]
        
        self.game_state = self._init_game_state()
        self._save_game_state()
        
    def _init_game_state(self) -> GameState:
        characters = [
            CharacterState(
                name=p.name,
                hp=10,
                max_hp=10,
                inventory=["Basic Weapon", "Rations"],
                status_effects=[]
            ) for p in self.players_config
        ]
        
        # Start at the first location in the world
        start_location = self.world_state.locations[0].name if self.world_state.locations else "Unknown"
        
        return GameState(
            round_number=1,
            current_location=start_location,
            characters=characters,
            npc_attitudes={},
            quest_progress={},
            session_history=[]
        )
        
    def _save_game_state(self):
        with open(self.game_state_path, "w") as f:
            f.write(self.game_state.model_dump_json(indent=2))
            
    def _append_transcript(self, text: str):
        with open(self.transcript_path, "a") as f:
            f.write(text + "\\n\\n")

    def run_round(self) -> bool:
        """Run a single round. Returns True if game continues, False if game over."""
        print(f"\\n=== Round {self.game_state.round_number} ===")
        
        # Task 1: DM describes the scene
        describe_task = Task(
            description=f"Describe the current situation at {self.game_state.current_location}. Round: {self.game_state.round_number}. Provide clear hooks for the players.",
            expected_output="A vivid description of the environment and any immediate events or characters present.",
            agent=self.dm_agent
        )
        
        # Parallel Tasks: Players decide their actions
        player_tasks = []
        for i, pa in enumerate(self.player_agents):
            pt = Task(
                description=f"Listen to the DM's scene description and the current situation. Decide your next action. Character: {self.players_config[i].name}.",
                expected_output=f"A short description of {self.players_config[i].name}'s action and any dialogue.",
                agent=pa,
                context=[describe_task]
            )
            player_tasks.append(pt)
            
        # Task 3: DM resolves the round
        resolve_task = Task(
            description="Review all player actions. Use your dice roller to determine outcomes if they attempt something difficult. Formulate a final narrative summary of the round and specify any state changes (HP, inventory, location).",
            expected_output="A narrative resolution of the players' actions, followed by a summary of state changes. At the very end of your output, you MUST include the exact phrase 'STATUS: GAME_OVER' if the game has ended (e.g. all players are dead), or 'STATUS: CONTINUE' if the game should proceed.",
            agent=self.dm_agent,
            context=player_tasks
        )
        
        crew = Crew(
            agents=[self.dm_agent] + self.player_agents,
            tasks=[describe_task] + player_tasks + [resolve_task],
            process=Process.sequential, # In a future version we could run players in parallel, but sequential ensures the DM sees all
            verbose=True
        )
        
        result = crew.kickoff()
        
        resolution_text = str(result)
        
        # Update our simple state representation
        self.game_state.session_history.append(resolution_text)
        self.game_state.round_number += 1
        self._save_game_state()
        self._append_transcript(f"## Round {self.game_state.round_number - 1}\\n\\n" + resolution_text)
        
        # Check for the explicit game over marker
        if "STATUS: GAME_OVER" in resolution_text.upper():
            return False
            
        return True
