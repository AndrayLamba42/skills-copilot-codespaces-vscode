# Directory Structures, Helpers & Utils

## When to Create Separate Directories

Create dedicated directories when:
- A concern has **3 or more related files**
- Logic is **reused across multiple modules**
- Data transformations are **complex enough to warrant isolation**

## Directory Purposes

### `src/helpers/`
Pure, stateless functions that perform a single transformation.
- No side effects, no I/O, no external dependencies
- Each helper file focuses on one domain (e.g., `string-helpers.js`, `date-helpers.js`)
- Every function must be independently testable

```javascript
// src/helpers/string-helpers.js
/**
 * Capitalize the first letter of a string.
 * @param {string} str
 * @returns {string}
 */
const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1);

module.exports = { capitalize };
```

### `src/utils/`
Cross-cutting utilities that may have side effects or depend on environment.
- Logging, configuration, environment detection
- File I/O wrappers, HTTP client setup
- Retry logic, rate limiting helpers

```javascript
// src/utils/logger.js
const logger = {
  info: (msg, ctx = {}) => console.log(JSON.stringify({ level: 'info', msg, ...ctx })),
  error: (msg, ctx = {}) => console.error(JSON.stringify({ level: 'error', msg, ...ctx })),
};

module.exports = logger;
```

### `src/structures/`
Data structures, type definitions, and schema objects.
- Class definitions for domain entities
- Validation schemas (e.g., JSON Schema, Joi/Zod objects)
- Enums and constant maps

```javascript
// src/structures/member.js
class Member {
  constructor(name, role) {
    this.name = name;
    this.role = role;
    this.joinedAt = new Date();
  }

  isAdmin() {
    return this.role === 'admin';
  }
}

module.exports = Member;
```

### `src/services/`
Business logic that orchestrates helpers, utils, and structures.
- Each service encapsulates one domain workflow
- Services may call helpers and utils but not other services directly
- Keep services thin — delegate computation to helpers

## Data-Heavy Task Guidelines

For tasks involving large datasets or complex transformations:

1. **Isolate data loading** — Put loaders in `src/utils/` with clear input/output contracts
2. **Separate transformation logic** — Put transformers in `src/helpers/` as pure functions
3. **Define schemas** — Put data shapes in `src/structures/` before writing logic
4. **Write fixtures first** — Create representative test data in `tests/fixtures/` before implementing
5. **Stream when possible** — Use Node.js streams for files larger than available memory
