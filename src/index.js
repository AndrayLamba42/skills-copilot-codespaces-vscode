/**
 * src/index.js — Entry point
 *
 * Loads all plugins from /plugins at startup and runs them with a shared
 * context object. Adding new behaviour requires only a new plugin file.
 */

const path = require('path');
const { loadPlugins } = require('../plugins/loader');

function main() {
  const pluginsDir = path.join(__dirname, '..', 'plugins');
  const plugins = loadPlugins(pluginsDir);

  // Shared mutable context passed to every plugin
  const context = {
    userName: process.env.USER || 'Learner',
    messages: [],
  };

  for (const plugin of plugins) {
    plugin.run(context);
  }

  console.log('\n--- Results ---');
  for (const msg of context.messages) {
    console.log(' *', msg);
  }
}

main();
