/**
 * plugins/loader.js
 *
 * Adaptive plugin loader — scans this directory at runtime and registers
 * every file that exports the standard plugin interface:
 *
 *   module.exports = {
 *     name: 'my-plugin',   // unique identifier
 *     run(context) { ... } // called by the host with shared context
 *   };
 *
 * To add new behaviour, drop a new .js file in this directory.
 * No other file needs to be touched.
 */

const fs = require('fs');
const path = require('path');

const SELF = path.basename(__filename); // 'loader.js' — skip self

function loadPlugins(dir = __dirname) {
  const plugins = [];

  const files = fs.readdirSync(dir).filter(
    (f) => f.endsWith('.js') && f !== SELF
  );

  for (const file of files) {
    const fullPath = path.join(dir, file);
    try {
      const plugin = require(fullPath);

      if (typeof plugin.name !== 'string' || typeof plugin.run !== 'function') {
        console.warn(`[loader] Skipping ${file}: missing name or run export`);
        continue;
      }

      plugins.push(plugin);
      console.log(`[loader] Registered plugin: ${plugin.name} (${file})`);
    } catch (err) {
      console.error(`[loader] Failed to load ${file}:`, err.message);
    }
  }

  return plugins;
}

module.exports = { loadPlugins };
