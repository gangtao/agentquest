# AgentQuest

An autonomous multi-agent RPG orchestration framework based on CrewAI.

## Overview
AgentQuest allows you to generate complete, playable RPG worlds from a single text prompt using a crew of AI agents. You can then configure a party of AI-driven player characters and let them play through the generated world autonomously, with another AI acting as the Dungeon Master.

## Installation
Requires Python >= 3.10 and `uv`.

```bash
uv sync
```

Set up your API keys:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Usage

### 1. Generate a World
Supply a "seed" prompt, and the Generation Crew (World Builder, Character Creator, Quest Designer, Consistency Checker) will build `output/world_state.json`.

```bash
uv run agentquest generate --seed "A dark fantasy world where magic is outlawed."
```

### 2. Play the Game
Using the generated world and a `players.yaml` config file, the Gameplay Crew (Dungeon Master, Players) will run a session autonomously.

```bash
uv run agentquest play --world output/world_state.json --players examples/players.yaml --rounds 3
```

Check `output/session/transcript.md` to read the story!

## Architecture
AgentQuest separates world generation (a one-shot sequential Crew) from gameplay (a looping round-based Crew with hierarchical state updates). All state passing is done via strict Pydantic schemas serialized to JSON.