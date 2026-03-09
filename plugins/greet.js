/**
 * plugins/greet.js — Example plugin
 *
 * Demonstrates the plugin contract. The host passes a `context` object;
 * plugins read from and write to it freely.
 */

module.exports = {
  name: 'greet',

  run(context) {
    const name = context.userName || 'World';
    context.messages = context.messages || [];
    context.messages.push(`Hello, ${name}! (from greet plugin)`);
  },
};
