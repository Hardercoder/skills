---
name: "un-skill-authoring"
description: "Meta skill: author a new high-quality sdlc-flow skill following repo conventions (un- prefix, name equals folder, double-quoted description, shared templates, validate with package_skill.py). Use when adding or refining a skill in this plugin. Part of sdlc-flow discipline layer."
agent_created: true
---

# un-skill-authoring

How to add or fix a skill inside this plugin so it stays consistent and portable.

## When to use
- Adding a new skill to `sdlc-flow`, or fixing an existing one.
- Inspired by the Superpowers `writing-skills` meta skill, adapted to this repo.

## Workflow
1. Create the folder: `sdlc-flow/skills/un-<name>/SKILL.md`.
2. Frontmatter (exact):
   - `name: "un-<name>"` — must match the folder name exactly.
   - `description:` a **plain double-quoted single line**, no angle brackets `<` `>`.
   - add `agent_created: true` (WorkBuddy-only field; other tools ignore it).
3. Body sections: `## When to use`, `## Workflow`, `## Output`, `## Cross-references`.
4. If the skill produces an artifact, add a template under `shared/` and reference
   it as `../../shared/<template>.md` (skill is two levels under `skills/<name>/`).
5. Symlink for local use:
   `ln -s "$(pwd)/skills/un-<name>" ~/.workbuddy/skills/un-<name>`.
6. Validate:
   `python3 <skill-creator>/scripts/package_skill.py skills/un-<name> /tmp/zips`
   Fix any "Validation failed".

## Rules
- Keep the `un-` prefix to avoid collisions across tools/plugins.
- Never hardcode absolute machine paths — use relative refs so the whole package
  distributes cleanly.
- Distribute the whole `sdlc-flow/` folder, not a single skill (templates break otherwise).

## Cross-references
- See `plugin.md` for the full layout, routing, and the contract bridge.
