from crewai.tools import BaseTool
import json

class CharacterSheetTool(BaseTool):
    name: str = "character_sheet"
    description: str = "Query your own character's stats and inventory from the game state."
    game_state_path: str = "output/game_state.json"

    def _run(self, character_name: str) -> str:
        try:
            with open(self.game_state_path, 'r') as f:
                state_data = json.load(f)
        except Exception as e:
            return f"Error reading game state from {self.game_state_path}: {e}"

        characters = state_data.get("characters", [])
        for char in characters:
            if char.get("name", "").lower() == character_name.strip().lower():
                return json.dumps(char, indent=2)
                
        return f"Error: Character '{character_name}' not found in game state."
