# Code Style Rules

## JavaScript / Node.js

### Naming
- `camelCase` for variables, functions, and method names
- `PascalCase` for classes, constructors, and type aliases
- `UPPER_SNAKE_CASE` for constants and environment variables
- Prefix boolean variables with `is`, `has`, `should`, or `can`

### Functions
- Keep functions under 30 lines; extract when they exceed that
- Use arrow functions for callbacks and inline operations
- Use named function declarations for top-level exported functions
- Always add JSDoc with `@param` and `@returns` for public APIs

```javascript
/**
 * Calculate the total price including tax.
 * @param {number} price - Base price
 * @param {number} taxRate - Tax rate as a decimal (e.g., 0.08)
 * @returns {number} Total price with tax applied
 */
function calculateTotal(price, taxRate) {
  return price * (1 + taxRate);
}
```

### Formatting
- 2-space indentation
- Semicolons required
- Single quotes for strings (except when the string contains a single quote)
- Trailing commas in multi-line arrays and objects
- Max line length: 100 characters

### Imports
- Group imports: built-in modules, external packages, internal modules
- Sort alphabetically within each group
- Prefer named exports over default exports

### Error Handling
- Always catch specific error types when possible
- Log errors with context (function name, input parameters)
- Never swallow errors silently — at minimum, log them

## YAML

- 2-space indentation (no tabs)
- Quote strings containing `:`, `{`, `}`, `[`, `]`, `,`, `&`, `*`, `#`, `?`, `|`, `-`, `<`, `>`, `=`, `!`, `%`, `@`, or backticks
- Use block scalars (`|` or `>`) for multi-line strings

## Markdown

- ATX-style headers with a blank line before and after
- One sentence per line (improves diff readability)
- Fenced code blocks with language identifiers
- Reference links for URLs used more than once
