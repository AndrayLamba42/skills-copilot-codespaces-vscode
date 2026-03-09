/**
 * plugins/timestamp.js — Example plugin
 *
 * Appends the current ISO timestamp to the shared context.
 * Drop this file in /plugins to enable it; delete it to disable.
 */

module.exports = {
  name: 'timestamp',

  run(context) {
    context.messages = context.messages || [];
    context.messages.push(`Current time: ${new Date().toISOString()}`);
  },
};
