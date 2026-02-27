# CLAUDE.md

## Repository Overview

This is a **GitHub Skills course template repository** — an educational course that teaches learners how to use GitHub Copilot within VS Code and Codespaces. It is **not** a production application or code library.

- **Course title:** "Code with GitHub Copilot"
- **Purpose:** Hands-on training for GitHub Copilot via a step-by-step automated learning workflow
- **License:** MIT

---

## Repository Structure

```
/
├── README.md                          # Active course instructions (auto-updated by workflows)
├── LICENSE                            # MIT License
├── .gitignore                         # Standard ignores (binaries, logs, OS files)
├── CLAUDE.md                          # This file
└── .github/
    ├── steps/
    │   ├── -step.txt                  # Current step tracker (single integer: 0–4 or "X")
    │   ├── 0-welcome.md               # Placeholder (step 0 start)
    │   ├── 1-copilot-extension.md     # Devcontainer setup instructions
    │   ├── 2-skills-javascript.md     # skills.js creation instructions
    │   ├── 3-copilot-hub.md           # member.js + Copilot hub instructions
    │   ├── 4-copilot-comment.md       # comments.js + comment-driven generation
    │   └── X-finish.md                # Course completion screen
    └── workflows/
        ├── 0-welcome.yml              # Triggers on first push to main → step 1
        ├── 1-copilot-extension.yml    # Triggers on .devcontainer/devcontainer.json push
        ├── 2-skills-javascript.yml    # Triggers on skills.js push
        ├── 3-copilot-hub.yml          # Triggers on member.js push
        └── 4-copilot-comment.yml      # Triggers on comments.js push
```

**No source code, package.json, build system, or test framework exists.** The repository contains only course content and GitHub Actions automation.

---

## Course Flow (Step-by-Step)

The course progresses automatically through steps 0 → 1 → 2 → 3 → 4 → X (finish). The current step is stored as a plain integer in `.github/steps/-step.txt`.

| Step | Action Required | Trigger File | Validation |
|------|----------------|--------------|------------|
| 0 | Use template / push to main | any push to `main` | None |
| 1 | Create `.devcontainer/devcontainer.json` with Copilot extension | `.devcontainer/devcontainer.json` | Contains `"GitHub.copilot"` |
| 2 | Create `skills.js` with a Copilot-suggested function | `skills.js` | Contains `function calculateNumbers` |
| 3 | Create `member.js` using Copilot hub suggestions | `member.js` | Contains `skillsMember` |
| 4 | Create `comments.js` from a comment prompt | `comments.js` | Contains `Create web server` |
| X | Course complete | — | — |

---

## GitHub Actions Automation

### Workflow Pattern

Every workflow follows the same structure:

1. **`get_current_step` job** — reads `.github/steps/-step.txt` and exposes it as a job output
2. **Main job** — runs only when:
   - The repository is **not** the template repo (`!github.event.repository.is_template`)
   - The current step matches the expected value
3. **File validation** — uses `skills/action-check-file@v1` to confirm required content is present
4. **Step advancement** — uses `skills/action-update-step@v2` to rewrite `README.md` and increment the step counter

### Actions Used

| Action | Purpose |
|--------|---------|
| `actions/checkout@v4` | Check out repository for file inspection |
| `skills/action-check-file@v1` | Assert a file exists and contains a required string (regex) |
| `skills/action-update-step@v2` | Rewrite README.md content and update `-step.txt` |

### Required Permissions

All workflows require `contents: write` (to update `README.md` and `-step.txt`).

---

## Learner-Created Files

Learners create these files at the **repository root** during the course:

| File | Required Content | Step |
|------|-----------------|------|
| `.devcontainer/devcontainer.json` | `"GitHub.copilot"` in extensions list | 1 |
| `skills.js` | `function calculateNumbers` | 2 |
| `member.js` | `skillsMember` | 3 |
| `comments.js` | `// Create web server` comment | 4 |

---

## Key Conventions for AI Assistants

### What This Repo Is and Isn't

- **Is:** An educational GitHub Skills course template with Markdown lesson content and GitHub Actions automation
- **Is not:** A deployable application, npm package, or testable codebase
- There are **no tests to run**, **no build steps**, and **no linting configuration**

### Step Counter

The file `.github/steps/-step.txt` controls which workflow job runs. It contains a single value (`0`, `1`, `2`, `3`, `4`, or `X`). Modifying this file directly will break the course flow — only change it through the `skills/action-update-step@v2` action.

### README.md Is Auto-Generated

`README.md` is rewritten by `skills/action-update-step@v2` at each step transition. It pulls content from the corresponding `.github/steps/<N>-*.md` file. **Do not manually edit README.md** to add course step content — edit the step files instead.

### Step Files

Each `.github/steps/*.md` file corresponds to one step of the course. They use standard Markdown with GitHub-flavored HTML comment annotations (`<!-- <<< Author notes: ... >>> -->`). Preserve these comment markers when editing step files.

### Workflow Conditions

All workflow jobs guard themselves with:
```yaml
if: ${{ !github.event.repository.is_template && needs.get_current_step.outputs.current_step == N }}
```
This prevents workflows from running on the template repository itself and ensures sequential course progression.

### Branch Strategy

- Learners work on the **`main`** branch — all workflow triggers target `main`
- Development/AI work should use feature branches (e.g., `claude/...`) and not push directly to `main` unless intentionally advancing a course step

---

## Development Workflows

### Adding or Modifying a Course Step

1. Edit the relevant `.github/steps/<N>-*.md` file with new instructions
2. If the validation criteria change, update the corresponding `.github/workflows/<N>-*.yml` workflow's `search:` parameter
3. Verify the workflow's trigger path (`paths:`) matches the file the learner is expected to create

### Adding a New Step

1. Create `.github/steps/<N>-description.md` with lesson content
2. Create `.github/workflows/<N>-description.yml` following the existing workflow pattern
3. Update the preceding workflow's `to_step:` value to point to the new step number
4. Update the new workflow's `from_step:` and `to_step:` values appropriately

### Resetting the Course (for Testing)

To reset to step 0:
```bash
echo "0" > .github/steps/-step.txt
git add .github/steps/-step.txt
git commit -m "Reset course to step 0"
git push origin main
```

---

## Git History

```
Initial commit
Update to step 1 in STEP and README.md
```

The repository was set up from the GitHub Skills template and has been advanced to Step 1.

---

## External Resources

- [GitHub Copilot docs](https://docs.github.com/en/copilot)
- [GitHub Skills](https://github.com/skills)
- [GitHub Skills quickstart (for course authors)](https://skills.github.com/quickstart)
- [GitHub Skills discussions (Code with Copilot)](https://github.com/orgs/skills/discussions/categories/code-with-copilot)
- [Codespaces prerequisite course](https://github.com/skills/code-with-codespaces)
