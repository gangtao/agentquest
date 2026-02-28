from agentquest.models import Location, PlayerConfig

def test_location_model():
    loc = Location(
        name="Town",
        description="A quiet village.",
        connected_to=["Forest"],
        npcs_present=["Mayor"]
    )
    assert loc.name == "Town"

def test_player_config():
    player = PlayerConfig(
        name="Bob",
        character_class="Fighter",
        personality="Brave",
        goal="Loot",
        alignment="Chaotic Good",
        backstory="A wandering sellsword."
    )
    assert player.name == "Bob"
