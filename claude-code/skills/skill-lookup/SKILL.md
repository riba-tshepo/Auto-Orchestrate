---
name: skill-lookup
description: >
  Search, retrieve, and install Agent Skills from prompts.chat to extend Claude's capabilities.
  Use when user says "find me a skill", "search for skills", "what skills are available",
  "get skill XYZ", "install a skill", or mentions Agent Skills, prompts.chat, or reusable
  AI agent components.
triggers:
  - find me a skill
  - search for skills
  - what skills are available
  - get skill
  - install a skill
---

# Skill Lookup

Search, retrieve, and install Agent Skills from the prompts.chat MCP server. Always search before suggesting the user create their own skill.

## Tools

### `search_skills`

Search for skills by keyword.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search keywords from user's request | — |
| `limit` | Number of results (max 50) | 10 |
| `category` | Filter by category slug (e.g., `coding`, `automation`) | — |
| `tag` | Filter by tag slug | — |

Present results showing title, description, author, file list, category/tags, and link.

### `get_skill`

Retrieve a specific skill by `id`. Returns metadata and all file contents (SKILL.md, reference docs, scripts, configs).

## Installation

When the user asks to install a skill:

1. Call `get_skill` to retrieve all files
2. Create `.claude/skills/{slug}/`
3. Save each file to `.claude/skills/{slug}/{filename}`
4. Confirm installation and explain what the skill does and when it activates