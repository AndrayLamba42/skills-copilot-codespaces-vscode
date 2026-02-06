# GitHub Actions Workflow Rules

## Workflow Structure

Each workflow in `.github/workflows/` follows this pattern for the tutorial:

```yaml
name: Step N, Descriptive Title
on:
  push:
    branches:
      - main
permissions:
  contents: write
jobs:
  job_name:
    name: Descriptive Job Name
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # validation steps...
      # step advancement...
```

## Conventions

### Naming
- Workflow files: `<step-number>-<short-description>.yml`
- Job names: Clear, human-readable descriptions
- Step names: Action-oriented (e.g., "Verify devcontainer config exists")

### Step Validation Pattern
The tutorial uses `skills/action-check-file@v1` to verify learner work:
- `file`: Path to the file to check
- `search`: String to search for inside the file
- `directory`: Working directory for the check

### Step Advancement Pattern
After validation passes, advance the tutorial step:
```yaml
- name: Advance to next step
  uses: skills/action-update-step@v2
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    from: <current-step>
    to: <next-step>
```

## Adding New Workflows

1. Follow the existing naming convention
2. Always include `permissions: contents: write` if modifying repo content
3. Pin action versions (use `@v4` not `@latest`)
4. Add descriptive names to every step
5. Test workflows in a branch before merging to main

## Security

- Never expose secrets in logs
- Use `${{ secrets.GITHUB_TOKEN }}` for repo operations
- Limit permissions to the minimum required scope
