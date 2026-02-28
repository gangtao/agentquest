import json
import yaml
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from agentquest.models import WorldState, PlayerConfig
from agentquest.crew.generation_crew import GenerationCrew
from agentquest.crew.gameplay_crew import GameplayCrew

app = FastAPI(title="AgentQuest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded paths for the single-tenant local server
OUTPUT_DIR = Path("output")
SESSION_DIR = OUTPUT_DIR / "session"
WORLD_STATE_PATH = OUTPUT_DIR / "world_state.json"
GAME_STATE_PATH = SESSION_DIR / "game_state.json"
TRANSCRIPT_PATH = SESSION_DIR / "transcript.md"

# In-memory holder for the active GameplayCrew
active_gameplay_crew: Optional[GameplayCrew] = None

class GenerateRequest(BaseModel):
    seed: str

class PlayRequest(BaseModel):
    players_yaml: Optional[str] = None
    resume: bool = True

@app.get("/api/status")
def get_status():
    """Returns the current status of the server."""
    world_exists = WORLD_STATE_PATH.exists()
    game_exists = GAME_STATE_PATH.exists()
    return {
        "world_generated": world_exists,
        "game_in_progress": game_exists,
        "crew_active": active_gameplay_crew is not None
    }

@app.post("/api/generate")
def generate_world(req: GenerateRequest):
    """Generates a new world based on the seed. This is a blocking call and may take a few minutes."""
    try:
        crew = GenerationCrew(world_seed=req.seed, output_dir=OUTPUT_DIR)
        world_state = crew.run()
        return {"message": "World generated successfully", "world_state": world_state.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/play/start")
def start_play(req: PlayRequest):
    """Initializes the gameplay crew with a world and player configs."""
    global active_gameplay_crew
    
    if not WORLD_STATE_PATH.exists():
        raise HTTPException(status_code=400, detail="World state not found. Generate a world first.")
        
    try:
        with open(WORLD_STATE_PATH, 'r') as f:
            world_data = json.load(f)
            world_state = WorldState(**world_data)
            
        if req.players_yaml:
            players_data = yaml.safe_load(req.players_yaml)
        else:
            with open("examples/players.yaml", "r") as f:
                players_data = yaml.safe_load(f)
                
        if not players_data or 'players' not in players_data:
            raise HTTPException(status_code=400, detail="Invalid players YAML format.")
            
        player_configs = [PlayerConfig(**p) for p in players_data.get('players', [])]
        
        active_gameplay_crew = GameplayCrew(
            world_state=world_state, 
            players=player_configs, 
            output_dir=SESSION_DIR, 
            resume=req.resume
        )
        
        return {"message": "Game session started", "game_state": active_gameplay_crew.game_state.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/play/step")
def play_step():
    """Runs a single round of the game."""
    global active_gameplay_crew
    
    if not active_gameplay_crew:
        raise HTTPException(status_code=400, detail="Gameplay crew not initialized. Call /api/play/start first.")
        
    try:
        continues = active_gameplay_crew.run_round()
        
        # Read the latest transcript addition (just the last block)
        # For a more robust app, we'd stream this, but for now we read the file
        transcript_content = ""
        if TRANSCRIPT_PATH.exists():
            with open(TRANSCRIPT_PATH, "r") as f:
                content = f.read().split("## Round")
                if len(content) > 1:
                    transcript_content = "## Round" + content[-1]
                else:
                    transcript_content = content[0]
                    
        return {
            "game_continues": continues,
            "game_state": active_gameplay_crew.game_state.model_dump(),
            "latest_transcript": transcript_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/state")
def get_state():
    """Returns the current world state and game state if they exist."""
    world_state = None
    game_state = None
    transcript = None
    
    if WORLD_STATE_PATH.exists():
        with open(WORLD_STATE_PATH, 'r') as f:
            world_state = json.load(f)
            
    if GAME_STATE_PATH.exists():
        with open(GAME_STATE_PATH, 'r') as f:
            game_state = json.load(f)
            
    if TRANSCRIPT_PATH.exists():
        with open(TRANSCRIPT_PATH, 'r') as f:
            transcript = f.read()
            
    if active_gameplay_crew is not None and not game_state:
        game_state = active_gameplay_crew.game_state.model_dump()
        
    return {
        "world_state": world_state,
        "game_state": game_state,
        "transcript": transcript
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
