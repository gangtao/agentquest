import json
import os
from unittest.mock import patch, MagicMock
from agentquest.crew.generation_crew import GenerationCrew
from agentquest.models import WorldState

@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_generation_crew_success(tmp_path):
    # Mocking the crew kickoff since we don't want to make real LLM calls
    mock_output_dict = {
        "setting": "A dark fantasy world.",
        "lore": "The old gods are dead.",
        "factions": ["The Iron Legion", "The Silver Hand"],
        "locations": [
            {
                "name": "Stormkeep",
                "description": "A ruined fortress.",
                "connected_to": ["Shadow Woods"],
                "npcs_present": ["Commander Vane"]
            }
        ],
        "npcs": [
            {
                "name": "Commander Vane",
                "role": "Leader",
                "personality": "Gruff",
                "attitude_toward_party": "neutral",
                "backstory": "Veteran of the Blood Wars."
            }
        ],
        "main_quest": {
            "title": "The Fallen Crown",
            "description": "Retrieve the lost crown.",
            "objectives": ["Find the crypt", "Defeat the guardian"],
            "twists": ["The guardian is Vane's brother"],
            "is_main_quest": True
        },
        "side_quests": [],
        "consistency_approved": True
    }
    
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value.json_dict = mock_output_dict
    
    with patch("agentquest.crew.generation_crew.Crew", return_value=mock_crew_instance):
        crew = GenerationCrew(world_seed="dark fantasy", output_dir=tmp_path)
        world_state = crew.run()
        
        assert isinstance(world_state, WorldState)
        assert world_state.consistency_approved is True
        assert world_state.locations[0].name == "Stormkeep"
        
        # Verify it was saved
        saved_file = tmp_path / "world_state.json"
        assert saved_file.exists()
        
        with open(saved_file) as f:
            data = json.load(f)
            assert data["setting"] == "A dark fantasy world."
