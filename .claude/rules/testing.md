# Testing Rules & Verification

## Test Structure

```
tests/
├── unit/                # Fast, isolated tests (mirrors src/ structure)
│   ├── helpers/
│   ├── utils/
│   ├── structures/
│   └── services/
├── integration/         # Tests that involve multiple modules or I/O
└── fixtures/            # Static test data, mocks, and sample files
```

## Test File Naming

- Unit tests: `<module-name>.test.js` (e.g., `string-helpers.test.js`)
- Integration tests: `<feature>.integration.test.js`
- Fixtures: Descriptive names matching the data they represent (e.g., `sample-members.json`)

## Writing Tests

### Unit Tests
Every helper, util, and structure must have a corresponding test file.

```javascript
// tests/unit/helpers/string-helpers.test.js
const { capitalize } = require('../../../src/helpers/string-helpers');

describe('capitalize', () => {
  it('capitalizes the first letter of a lowercase string', () => {
    expect(capitalize('hello')).toBe('Hello');
  });

  it('returns an empty string unchanged', () => {
    expect(capitalize('')).toBe('');
  });

  it('handles already-capitalized strings', () => {
    expect(capitalize('Hello')).toBe('Hello');
  });
});
```

### Test Patterns
- **Arrange-Act-Assert** (AAA) for every test case
- One assertion per test when possible
- Use descriptive `it('should ...')` or `it('returns ... when ...')` names
- Group related tests with `describe` blocks

### What to Test
- Happy path (expected inputs produce expected outputs)
- Edge cases (empty strings, zero, null, boundary values)
- Error conditions (invalid inputs, missing data)
- For data-heavy code: test with realistic fixtures, not trivial examples

## Fixtures

- Store in `tests/fixtures/` as JSON, CSV, or JS modules
- Keep fixtures minimal but representative
- Name fixtures to describe their content: `valid-members.json`, `malformed-input.json`
- Never commit sensitive data — use anonymized/synthetic data only

## Verification Commands

```bash
# Run all tests
npm test

# Run tests in watch mode (during development)
npm test -- --watch

# Run a specific test file
npx jest tests/unit/helpers/string-helpers.test.js

# Run tests with coverage
npm test -- --coverage

# Lint before committing
npm run lint
```

## Verification Checklist

Before committing any new code:
1. All existing tests pass (`npm test`)
2. New code has corresponding test files
3. No linting errors (`npm run lint`, if configured)
4. Test coverage does not decrease
5. Fixtures are up to date if data schemas changed

## Tutorial-Specific Validation

This project uses GitHub Actions workflows to verify tutorial steps.
Each step checks for:
- Existence of a specific file (e.g., `skills.js`)
- Presence of expected content within that file
- Files are validated on push to `main` via `skills/action-check-file@v1`
