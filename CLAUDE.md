# CLAUDE.md — AI Assistant Guide

This file provides context for AI assistants (Claude, Copilot, etc.) working
inside this repository. It describes the project purpose, structure, workflows,
and conventions to follow.

---

## Project Overview

**skills-copilot-codespaces-vscode** is a **GitHub Skills educational course**
that teaches developers how to use GitHub Copilot inside GitHub Codespaces and
VS Code. The repository is intentionally minimal: it contains no application
source code, no dependencies, and no build tooling. All content is
documentation and GitHub Actions automation.

Learners fork this repository, open it in a Codespace, and complete 4 guided
steps. Each step is verified automatically by a GitHub Actions workflow that
detects committed files and advances the course progress.

---

## Repository Structure

```
.
├── .github/
│   ├── steps/                    # Per-step instructional markdown
│   │   ├── 0-welcome.md
│   │   ├── 1-copilot-extension.md
│   │   ├── 2-skills-javascript.md
│   │   ├── 3-copilot-hub.md
│   │   ├── 4-copilot-comment.md
│   │   └── X-finish.md
│   ├── workflows/                # GitHub Actions — one per step
│   │   ├── 0-welcome.yml
│   │   ├── 1-copilot-extension.yml
│   │   ├── 2-skills-javascript.yml
│   │   ├── 3-copilot-hub.yml
│   │   └── 4-copilot-comment.yml
│   └── steps/-step.txt           # Single source of truth: current step number
├── CLAUDE.md                     # This file
├── LICENSE                       # MIT
└── README.md                     # Auto-updated course landing page
```

**Learner-created files** (do not exist in the template; created during the
course):

| File | Created in Step | Content Expected |
|------|-----------------|------------------|
| `.devcontainer/devcontainer.json` | Step 1 | Must include `"GitHub.copilot"` |
| `skills.js` | Step 2 | Must define `function calculateNumbers` |
| `member.js` | Step 3 | Must define `function skillsMember` |
| `comments.js` | Step 4 | Must contain `// Create web server` |

---

## How the Course Progression Works

1. `.github/steps/-step.txt` holds the current step number (`0`–`4` or `X`).
2. Each workflow reads this file in a `get_current_step` job and only executes
   if the current step matches its own step number.
3. The workflow uses `skills/action-check-file@v1` to verify the expected file
   and content exist in the learner's commit.
4. On success, `skills/action-update-step@v2` increments the step counter and
   rewrites the README with the next set of instructions.

**State machine:**

```
0 (welcome) → 1 → 2 → 3 → 4 → X (finished)
```

Workflows never run against the template repository itself
(`!github.event.repository.is_template`).

---

## GitHub Actions Conventions

- Runner: `ubuntu-latest`
- Checkout: `actions/checkout@v4` with `fetch-depth: 0`
- Permissions: `contents: write` for every workflow
- Job chaining via `needs:` and output parameters (`steps.<id>.outputs.<key>`)
- Conditional execution pattern:

```yaml
if: steps.get_step.outputs.current_step == '1'
```

- Authentication: `${{ secrets.GITHUB_TOKEN }}` passed explicitly to actions

---

## Naming Conventions

| Artifact | Pattern | Example |
|----------|---------|---------|
| Workflow files | `{N}-{kebab-name}.yml` | `2-skills-javascript.yml` |
| Step docs | `{N}-{kebab-name}.md` | `2-skills-javascript.md` |
| Learner JS files | `{topic}.js` | `skills.js`, `member.js` |
| JS functions | camelCase | `calculateNumbers()`, `skillsMember()` |

---

## Development Workflows

### Adding or modifying a step

1. Update (or create) the step doc in `.github/steps/{N}-{name}.md`.
2. Update (or create) the workflow in `.github/workflows/{N}-{name}.yml`.
3. Ensure the workflow reads `-step.txt` and conditions on the correct step
   number.
4. Update the `X-finish.md` and `0-welcome.md` if the total step count changes.
5. Verify that the previous step's workflow advances to the new step number.

### Modifying the README

The README is rewritten automatically by `skills/action-update-step@v2` during
step transitions. Manual edits to dynamic sections will be overwritten. Edit
the source content inside the relevant `.github/steps/*.md` file instead.

### Testing workflows locally

Use [act](https://github.com/nektos/act) to run GitHub Actions locally:

```bash
act push -W .github/workflows/2-skills-javascript.yml
```

---

## Key Constraints for AI Assistants

- **Do not introduce a build system, package.json, or dependencies** unless
  explicitly asked. The educational value depends on simplicity.
- **Do not modify `-step.txt` directly.** Step advancement is handled
  exclusively by the `skills/action-update-step@v2` action.
- **Do not modify the README body directly.** Use the step markdown files.
- **Learner files (`skills.js`, `member.js`, `comments.js`, `.devcontainer/`)
  are intentionally absent** from the template. Do not pre-create them.
- Workflow YAML must keep `!github.event.repository.is_template` guards intact
  so the template itself never self-advances.

---

## Adaptive Code Structure (Design Intent)

This repository is designed to be **metadata-driven and self-advancing**:

- A single plain-text counter (`-step.txt`) drives all branching logic.
- Adding a new learning step requires only a new markdown file + a new workflow
  file — no changes to any other file.
- The README surface presented to the learner is regenerated automatically from
  step docs; the course "adapts" its UI to the learner's current position.

When extending this repository, preserve this pattern: **new information
(a new step, a new check) should be expressible by adding a file, not by
modifying existing logic.**

---

## Resources

- [GitHub Skills](https://skills.github.com/)
- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
- [skills/action-update-step](https://github.com/skills/action-update-step)
- [skills/action-check-file](https://github.com/skills/action-check-file)
