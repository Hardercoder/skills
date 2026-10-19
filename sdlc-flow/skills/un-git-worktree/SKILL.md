---
name: "un-git-worktree"
description: "Use git worktrees to isolate parallel work on separate branches without contaminating the main working tree. Use when running multiple tasks/agents concurrently or keeping experiments isolated. Part of sdlc-flow discipline layer."
agent_created: true
---

# un-git-worktree

Isolate each piece of work in its own worktree + branch so concurrent tasks never
clobber each other or the main tree.

## When to use
- Parallel feature work, agent-driven development, or keeping a clean main tree
  while experimenting.
- Pairs naturally with `un-parallel-agents`.

## Workflow
1. `git worktree add <path> -b <branch-name>` for each isolated task.
2. Do the work inside its worktree. Never mix two tasks in one tree.
3. On completion: merge/rebase back to the base branch, then
   `git worktree remove <path>` and `git branch -d <branch-name>` if merged.

## Rules
- One task per worktree / branch.
- Always clean up worktrees you created (orphaned worktrees waste disk and confuse tools).
- Keep the base branch clean; only land finished, verified work there.

## Cross-references
- Complements `un-parallel-agents` and `un-verify-before-done`.
