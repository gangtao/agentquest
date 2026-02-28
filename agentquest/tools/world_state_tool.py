from crewai.tools import BaseTool
import json

class WorldStateTool(BaseTool):
    name: str = "query_world_state"
    description: str = "Query sections of the world state. Useful for getting information about locations, NPCs, quests, or lore. Valid sections are: 'lore', 'factions', 'locations', 'npcs', 'main_quest', 'side_quests'."
    world_state_path: str = "output/world_state.json"

    def _run(self, section: str) -> str:
        try:
            with open(self.world_state_path, 'r') as f:
                state_data = json.load(f)
        except Exception as e:
            return f"Error reading world state from {self.world_state_path}: {e}"

        section = section.strip().lower()
        if section not in state_data:
            return f"Error: '{section}' is not a valid section. Valid sections are: {list(state_data.keys())}"

        section_data = state_data[section]
        if isinstance(section_data, (dict, list)):
            return json.dumps(section_data, indent=2)
        return str(section_data)
