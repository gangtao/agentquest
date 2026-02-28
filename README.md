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

### Configuration
By default, AgentQuest uses OpenAI's default model (e.g. `gpt-4o`).
You can change the provider or model by setting the `MODEL` environment variable in your `.env` file. We use LiteLLM via CrewAI, so you can specify Anthropic, Google Gemini, or local models:

```bash
# Example for Anthropic
MODEL=anthropic/claude-3-5-sonnet-20240620
ANTHROPIC_API_KEY=your-key

# Example for OpenAI
MODEL=openai/gpt-4-turbo
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

**Campaign Persistence:**
By default, running the `play` command again will automatically resume from the `output/session/game_state.json` file if it exists, allowing you to play long, continuous campaigns across multiple sessions. 

If you want to start a completely new game using the same world generation, use the `--no-resume` flag:
```bash
uv run agentquest play --world output/world_state.json --players examples/players.yaml --rounds 3 --no-resume
```

**Context Summarization:**
AgentQuest automatically summarizes old session history once the game exceeds 10 rounds to prevent overloading the LLM context window, ensuring long campaigns run smoothly and cheaply.

## Architecture
AgentQuest separates world generation (a one-shot sequential Crew) from gameplay (a looping round-based Crew with hierarchical state updates). All state passing is done via strict Pydantic schemas serialized to JSON.