import os
from unittest.mock import patch, MagicMock
from agentquest.crew.gameplay_crew import GameplayCrew
from agentquest.models import WorldState, PlayerConfig

@patch.dict(os.environ, {"OPENAI_API_KEY": "dummy"})
def test_gameplay_crew_success(tmp_path):
    # Setup dummy WorldState
    world_dict = {
        "seed": "fantasy",
        "setting": "fantasy",
        "lore": "old",
        "factions": [],
        "locations": [{"name": "Start", "description": "start desc", "connected_to": [], "npcs_present": []}],
        "npcs": [],
        "main_quest": {"title": "Main", "description": "main desc", "objectives": [], "twists": [], "is_main_quest": True},
        "side_quests": [],
        "consistency_approved": True
    }
    world_state = WorldState(**world_dict)
    
    # Setup dummy Players
    players = [
        PlayerConfig(name="Alice", character_class="Mage", personality="Smart", goal="Learn", alignment="Neutral")
    ]
    
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = "The round was resolved. The party rests out."
    
    with patch("agentquest.crew.gameplay_crew.Crew", return_value=mock_crew_instance):
        crew = GameplayCrew(world_state=world_state, players=players, output_dir=tmp_path)
        
        continues = crew.run_round()
        assert continues is True
        
        assert crew.game_state.round_number == 2
        assert len(crew.game_state.session_history) == 1
        
        # Verify files were saved
        assert (tmp_path / "game_state.json").exists()
        assert (tmp_path / "transcript.md").exists()
