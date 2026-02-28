import json
from pathlib import Path
from crewai import Crew, Task, Process
from agentquest.agents import get_world_builder, get_character_creator, get_quest_designer, get_consistency_checker
from agentquest.models import WorldState
from pydantic import ValidationError

class GenerationCrew:
    """
    One-shot crew that generates the full game world from a seed prompt.
    Runs agents sequentially: WorldBuilder -> CharacterCreator -> QuestDesigner -> ConsistencyChecker (loops until approved).
    Outputs world_state.json.
    """
    def __init__(self, world_seed: str, output_dir: Path):
        self.world_seed = world_seed
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.world_state_path = self.output_dir / "world_state.json"
        
        self.world_builder = get_world_builder()
        self.character_creator = get_character_creator()
        self.quest_designer = get_quest_designer()
        self.consistency_checker = get_consistency_checker()
        
    def _create_tasks(self, seed: str) -> list[Task]:
        build_world_task = Task(
            description=f"Create a setting, lore, factions, and locations for the following seed: '{seed}'. Make locations interconnected.",
            expected_output="JSON containing 'setting', 'lore', 'factions', and 'locations'.",
            agent=self.world_builder
        )
        
        create_npcs_task = Task(
            description="Generate interesting NPCs (merchants, guards, villains, allies) that fit the setting and locations created by the World Builder. Give them distinct personalities and attitudes.",
            expected_output="JSON array of NPCs matching the required schema.",
            agent=self.character_creator,
            context=[build_world_task]
        )
        
        design_quests_task = Task(
            description="Design one main quest arc involving major factions and locations, and several side quests. Include narrative twists.",
            expected_output="JSON containing 'main_quest' and 'side_quests'.",
            agent=self.quest_designer,
            context=[build_world_task, create_npcs_task]
        )
        
        check_consistency_task = Task(
            description="Review the generated world (setting, locations, NPCs, quests). Ensure no geographic impossibilities, lore contradictions, or missing references. Output JSON with 'consistency_approved' as true, or detail what needs fixing.",
            expected_output="JSON with a single boolean 'consistency_approved' and possibly explanations if false.",
            agent=self.consistency_checker,
            context=[build_world_task, create_npcs_task, design_quests_task],
            output_json=WorldState # Enforce output mapping directly to our Pydantic schema
        )
        
        return [build_world_task, create_npcs_task, design_quests_task, check_consistency_task]

    def run(self, max_iterations: int = 3) -> WorldState:
        iteration = 0
        current_seed = self.world_seed
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\\n--- Running Generation Crew (Iteration {iteration}/{max_iterations}) ---")
            
            crew = Crew(
                agents=[self.world_builder, self.character_creator, self.quest_designer, self.consistency_checker],
                tasks=self._create_tasks(current_seed),
                process=Process.sequential,
                verbose=True
            )
            
            result_output = crew.kickoff()
            
            # The result_output should ideally map to our Pydantic model now since we set output_json on the last task.
            try:
                # Sometimes CrewAI output might need to be parsed from JSON string if not returned natively as dict
                if hasattr(result_output, 'json_dict') and result_output.json_dict:
                     result_dict = result_output.json_dict
                else:
                    # Fallback to string parsing just in case
                    import re
                    json_match = re.search(r'\\{.*\\}', str(result_output), re.DOTALL)
                    if json_match:
                        result_dict = json.loads(json_match.group(0))
                    else:
                        result_dict = json.loads(str(result_output))
            except Exception as e:
                print(f"Failed to parse crew output as JSON: {e}")
                # If we fail to parse, feed that back as a seed to fix it
                current_seed = f"Fix formatting errors. The output MUST be valid JSON matching the WorldState schema. Previous seed was: {self.world_seed}"
                continue
                
            print("Consistency check completed.")
            
            # Use Pydantic to validate
            try:
                # Need to inject the original seed if it was stripped
                if 'seed' not in result_dict:
                     result_dict['seed'] = self.world_seed
                
                world_state = WorldState(**result_dict)
                
                if world_state.consistency_approved:
                    print("World generation successful and approved!")
                    
                    # Persist to disk
                    with open(self.world_state_path, "w") as f:
                        f.write(world_state.model_dump_json(indent=2))
                        
                    return world_state
                else:
                    print("Consistency checker failed approval. Retrying...")
                    # Feed the feedback back in as part of the seed
                    current_seed = f"Original seed: {self.world_seed}\\n\\nFeedback from Consistency Checker to fix: The generated world was inconsistent. Please ensure you fix the following issues in this iteration."
            except ValidationError as e:
                print(f"Schema validation error: {e}")
                current_seed = f"Original seed: {self.world_seed}\\n\\nSchema error: Please ensure output matches the required JSON structure exactly."
                
        raise RuntimeError("Failed to generate a consistent and valid world state within max iterations.")
