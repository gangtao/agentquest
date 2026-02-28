# AgentQuest Design Document

## Current Context
- **AgentQuest** is a new open-source project built on top of [CrewAI](https://crewai.com/), the multi-agent orchestration framework.
- The project has no existing codebase — this document defines the initial architecture from scratch.
- The core idea: users provide a world seed and a player config, then an autonomous crew of AI agents generates a game world and plays through it — with no human in the game loop.
- Key insight: separating *world generation* (a one-time CrewAI crew) from *gameplay* (a looping crew of DM + Player agents) is what makes the architecture clean and replayable.

---

## Requirements

### Functional Requirements

**Part 1 — World Generation**
- Accept a free-text `world_seed` string from the user as the only required input
- Run a multi-agent generation crew that produces a fully structured `world_state.json`
- World state must include: setting/lore, map locations, factions, NPCs, main quest arc, side quests, and narrative twists
- A consistency checker agent must validate cross-agent outputs and flag contradictions before finalizing
- Generation should loop (up to N iterations) until the consistency checker approves the world state

**Part 2 — Player Config**
- Users define players via a simple `players.yaml` file — no coding required
- Each player entry must support: `name`, `class`, `personality`, `goal`, `alignment`, and optional `backstory`
- Config validation should provide clear error messages for missing or invalid fields
- At least 1 player required; support up to 6 players

**Part 3 — Gameplay Loop**
- A DM agent orchestrates each round: describes the scene, collects player actions, resolves outcomes, narrates results
- Each player agent independently decides their action based on their personality, goals, and memory of past events
- Player agents should NOT share their intended actions before submitting (to maximize emergent conflict/cooperation)
- DM agent maintains a live `game_state.json` tracking: HP, inventory, quest progress, NPC attitudes, session history
- Game loop runs until: the main quest is resolved, all players die, or the user manually stops it
- All dialogue and narration streamed to terminal (or UI) in real time

**General**
- CLI entrypoint: `agentquest run --seed "..." --players players.yaml`
- World state and game transcripts saved to an `output/` directory
- Allow replaying an existing world with a new player config: `agentquest play --world output/world_state.json --players players.yaml`

### Non-Functional Requirements

- **Performance**: World generation should complete within 3–5 minutes for a standard LLM provider. Each game round should resolve within 30 seconds.
- **Scalability**: Support 1–6 player agents without architectural changes. World complexity should be configurable (short one-shot vs. full campaign).
- **Observability**: All agent actions, LLM calls, and tool uses logged to structured JSON log files. Real-time console output for gameplay narrative.
- **Extensibility**: Agent prompts, tools, and game rules defined in plain Python/YAML — easy for contributors to customize.
- **Portability**: Works with OpenAI, Anthropic, and any LiteLLM-compatible model provider. Model configured via environment variable.
- **Security**: API keys loaded from `.env` only, never hardcoded. No network calls beyond LLM provider APIs.

---

## Design Decisions

### 1. Two Separate CrewAI Crews
Will implement two distinct CrewAI `Crew` objects (one for generation, one for gameplay) because:
- Generation is a one-shot, finite pipeline — sequential tasks with a clear end state
- Gameplay is an infinite loop with stateful context — fundamentally different orchestration pattern
- Keeping them separate allows users to regenerate the world without replaying, and replay without regenerating
- Trade-off: slightly more boilerplate, but dramatically cleaner separation of concerns

### 2. Structured World State via JSON
Will use a schema-validated `world_state.json` as the shared artifact between Part 1 and Part 3 because:
- Agents need to reliably parse each other's outputs — free-form prose breaks downstream agents
- JSON enables the consistency checker to do structured diffing across agent outputs
- Persisting to disk allows the replay feature and makes debugging easy
- Alternatives considered: Markdown document (too unstructured), SQLite (overkill for v1)

### 3. Player Agents Do Not See Each Other's Actions Before Submitting
Will implement a "sealed bid" action model per round because:
- This creates genuine emergent conflict and surprise — a core design goal
- Mirrors how real tabletop players don't fully coordinate every move
- Makes the spectator experience more dynamic and unpredictable
- Alternatives considered: shared deliberation phase (more cooperative but less interesting)

### 4. DM Agent as Hierarchical Manager
Will use CrewAI's hierarchical process mode with the DM agent as manager because:
- DM naturally orchestrates the flow of each round
- DM must have final authority on resolving conflicting player actions
- CrewAI's manager pattern handles delegation and result collection cleanly
- Trade-off: slightly less parallelism, but narrative coherence requires a single arbiter

### 5. YAML for Player Config
Will use YAML instead of JSON or CLI flags because:
- More human-readable and writable without tooling
- Supports multi-line strings for backstories naturally
- Standard for configuration in the Python/DevOps ecosystem
- Pydantic used for validation to give clear error messages

---

## Technical Design

### 1. Core Components

```python
# crew/generation_crew.py
class GenerationCrew:
    """
    One-shot crew that generates the full game world from a seed prompt.
    Runs agents sequentially: WorldBuilder → CharacterCreator → 
    QuestDesigner → ConsistencyChecker (loops until approved).
    Outputs world_state.json.
    """
    def __init__(self, world_seed: str, output_dir: Path): ...
    def run(self) -> WorldState: ...


# crew/gameplay_crew.py
class GameplayCrew:
    """
    Looping crew that runs the live game session.
    DM agent orchestrates each round; Player agents respond independently.
    Maintains and persists game_state.json across rounds.
    """
    def __init__(self, world_state: WorldState, players: list[PlayerConfig]): ...
    def run(self) -> GameTranscript: ...


# gm/dm_agent.py
class DMAgent:
    """
    Hierarchical manager agent. Describes scenes, collects player actions,
    resolves outcomes with dice rolls, narrates results, updates game state.
    """
    def describe_scene(self, game_state: GameState) -> str: ...
    def resolve_round(self, actions: list[PlayerAction]) -> RoundResult: ...
    def update_state(self, result: RoundResult) -> GameState: ...


# players/player_agent.py
class PlayerAgent:
    """
    Individual player agent. System prompt encodes personality, class, goals.
    Decides actions independently based on scene description and personal memory.
    """
    def __init__(self, config: PlayerConfig): ...
    def decide_action(self, scene: str, game_state: GameState) -> PlayerAction: ...
```

### 2. Data Models

```python
from pydantic import BaseModel
from typing import Optional

# models/world_state.py
class Location(BaseModel):
    name: str
    description: str
    connected_to: list[str]
    npcs_present: list[str]

class NPC(BaseModel):
    name: str
    role: str
    personality: str
    attitude_toward_party: str  # friendly / neutral / hostile
    backstory: str

class Quest(BaseModel):
    title: str
    description: str
    objectives: list[str]
    twists: list[str]
    is_main_quest: bool

class WorldState(BaseModel):
    seed: str
    setting: str
    lore: str
    factions: list[str]
    locations: list[Location]
    npcs: list[NPC]
    main_quest: Quest
    side_quests: list[Quest]
    consistency_approved: bool


# models/player_config.py
class PlayerConfig(BaseModel):
    name: str
    character_class: str
    personality: str
    goal: str
    alignment: str
    backstory: Optional[str] = None


# models/game_state.py
class CharacterState(BaseModel):
    name: str
    hp: int
    max_hp: int
    inventory: list[str]
    status_effects: list[str]

class GameState(BaseModel):
    round_number: int
    current_location: str
    characters: list[CharacterState]
    npc_attitudes: dict[str, str]
    quest_progress: dict[str, bool]
    session_history: list[str]  # last N round summaries for context


# models/gameplay.py
class PlayerAction(BaseModel):
    player_name: str
    action: str
    target: Optional[str] = None

class RoundResult(BaseModel):
    narration: str
    state_changes: dict  # diffs applied to GameState
    game_over: bool
    game_over_reason: Optional[str] = None
```

### 3. Integration Points

**LLM Provider**
- All agents use LiteLLM under the hood via CrewAI — model configured via `MODEL` env var (e.g. `openai/gpt-4o`, `anthropic/claude-sonnet-4-6`)
- API key loaded from `.env` via `python-dotenv`

**Agent Tools**
- `DiceRollerTool` — DM agent uses this for randomized outcome resolution (d20, d6, etc.)
- `WorldStateTool` — read-only tool giving agents access to relevant world state sections
- `CharacterSheetTool` — player agents query their own current stats and inventory

**Data Flow**

```
CLI
 └─► GenerationCrew
       ├─ WorldBuilderAgent      ──┐
       ├─ CharacterCreatorAgent  ──┤──► world_state.json
       ├─ QuestDesignerAgent     ──┤
       └─ ConsistencyCheckerAgent─┘
            ↓ (approved)
 └─► GameplayCrew (reads world_state.json)
       ├─ DMAgent (manager)
       │    ├─ PlayerAgent[0..N]  (parallel action collection)
       │    └─ Resolves + narrates
       └─► game_state.json (updated each round)
            └─► output/transcript.md (append each round)
```

### 4. File Structure

```
agentquest/
├── agentquest/
│   ├── __init__.py
│   ├── cli.py                    # CLI entrypoint (typer)
│   ├── crew/
│   │   ├── generation_crew.py    # Part 1 crew definition
│   │   └── gameplay_crew.py      # Part 3 crew + game loop
│   ├── agents/
│   │   ├── world_builder.py
│   │   ├── character_creator.py
│   │   ├── quest_designer.py
│   │   ├── consistency_checker.py
│   │   ├── dm_agent.py
│   │   └── player_agent.py
│   ├── models/
│   │   ├── world_state.py
│   │   ├── player_config.py
│   │   └── game_state.py
│   ├── tools/
│   │   ├── dice_roller.py
│   │   ├── world_state_tool.py
│   │   └── character_sheet_tool.py
│   └── prompts/
│       ├── world_builder.md
│       ├── character_creator.md
│       ├── quest_designer.md
│       ├── consistency_checker.md
│       ├── dm_agent.md
│       └── player_agent.md       # templated with player config
├── examples/
│   ├── players.yaml              # example player config
│   └── seeds.md                  # example world seed prompts
├── output/                       # gitignored, runtime artifacts
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Implementation Plan

### Phase 1: Foundation 
- Set up repo, pyproject.toml, CLI skeleton with Typer
- Implement all Pydantic data models with validation
- Implement `DiceRollerTool`, `WorldStateTool`, `CharacterSheetTool`
- Write and test prompt templates for all 6 agents in `prompts/`

### Phase 2: Generation Crew 
- Implement `WorldBuilderAgent`, `CharacterCreatorAgent`, `QuestDesignerAgent`
- Implement `ConsistencyCheckerAgent` with loop-until-approved logic
- Implement `GenerationCrew` wiring all four together
- Test end-to-end: `agentquest generate --seed "..."` produces valid `world_state.json`
- Validate JSON output against Pydantic schema

### Phase 3: Gameplay Crew 
- Implement `DMAgent` with scene description, action resolution, state update
- Implement `PlayerAgent` with personality-encoded system prompts
- Implement `GameplayCrew` with the round loop
- Wire up game state persistence and transcript output
- Test: `agentquest play` runs a full session to completion

### Phase 4: Polish & Open Source Launch 
- README with architecture diagram, quickstart, example output
- `examples/` with 3 world seeds and sample player configs
- GitHub Actions CI (lint, type check, unit tests)
- Record a demo GIF for the README
- Publish to PyPI: `pip install agentquest`

---

## Testing Strategy

### Unit Tests
- `test_models.py` — validate Pydantic models accept valid input and reject invalid
- `test_tools.py` — dice roller produces values in expected ranges; world state tool returns correct sections
- `test_prompts.py` — prompt templates render correctly with various player configs
- Mock all LLM calls using `unittest.mock` or `pytest-mock`

### Integration Tests
- `test_generation_crew.py` — mock LLM responses, assert `world_state.json` is produced and schema-valid
- `test_gameplay_crew.py` — mock LLM responses for DM + 2 players, assert game loop runs 3 rounds and updates state correctly
- `test_consistency_checker.py` — inject a contradictory world state, assert checker flags it and triggers a revision

### Manual / Exploratory Tests
- Run full end-to-end with real LLM for at least 3 different world seeds before each release
- Test with 1 player, 3 players, and 6 players to validate scaling

---

## Observability

### Logging
- Structured JSON logs written to `output/logs/session_{timestamp}.jsonl`
- Each log line contains: `timestamp`, `agent`, `event_type`, `content`, `round_number`
- Event types: `llm_call`, `tool_use`, `action_decided`, `round_resolved`, `state_updated`, `error`
- Console output is human-readable narrative only (not raw logs)

### Metrics (future)
- Total LLM tokens consumed per session (generation + gameplay)
- Average round resolution time
- Consistency checker iteration count per generation

---

## Future Considerations

### Potential Enhancements
- **Web UI**: Replace terminal output with a Next.js/Streamlit frontend showing live agent "speech bubbles" and a visual map
- **Image Generation**: Auto-generate location art and character portraits via DALL-E or Stable Diffusion at world generation time
- **Human-in-the-Loop Mode**: Allow the user to take over one player slot and type their own actions each round
- **Campaign Persistence**: Save and resume sessions across multiple runs
- **Multiple World Genres**: Sci-fi, horror, western — genre templates that adjust all agent prompts
- **Voice Output**: TTS narration for DM agent using ElevenLabs or OpenAI TTS

### Known Limitations
- Long sessions will hit LLM context limits — session history needs summarization after ~20 rounds (not in v1)
- Agent creativity is bounded by the underlying model — GPT-4o / Claude Sonnet recommended for best results
- No true parallelism in v1 — player agents queried sequentially despite being logically independent
- Consistency checker may loop excessively on complex world seeds — needs a max-iterations cap

---

## Dependencies

```toml
[project]
dependencies = [
    "crewai>=0.80.0",
    "pydantic>=2.0",
    "typer>=0.12",
    "python-dotenv>=1.0",
    "rich>=13.0",        # pretty terminal output
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-mock>=3.0",
    "ruff>=0.4",         # linting
    "mypy>=1.0",         # type checking
]
```

---

## Security Considerations
- API keys loaded exclusively from `.env` file; `.env` in `.gitignore` by default
- `.env.example` provided with placeholder values only
- No user data sent to any service beyond the configured LLM provider
- World state and game transcripts stored locally only
- No authentication needed for v1 (local CLI tool)

---

## Rollout Strategy
1. **Development**: Build and test locally against OpenAI GPT-4o
2. **Alpha**: Share GitHub repo with a small group of CrewAI / D&D community members for feedback
3. **Beta**: Submit to CrewAI's community showcase; post on Hacker News / Reddit r/DnD and r/LocalLLaMA
4. **v1.0 Release**: Publish to PyPI, post demo video, write dev blog post on Medium / Dev.to
5. **Post-Launch**: Monitor GitHub issues, iterate on most-requested features

---

## References
- [CrewAI Documentation](https://docs.crewai.com)
- [CrewAI Hierarchical Process](https://docs.crewai.com/concepts/processes#hierarchical-process)
- [Pydantic v2 Documentation](https://docs.pydantic.dev)
- [Typer CLI Framework](https://typer.tiangolo.com)
- [LiteLLM (multi-provider LLM interface)](https://litellm.ai)