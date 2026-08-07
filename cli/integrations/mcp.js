'use strict';
const fs = require('fs');
const path = require('path');
const { ensureDir } = require('../lib/transform');

exports.install = async function (cwd, prompts, flags) {
  // Create MCP server script
  const mcpDir = path.join(cwd, '.mcp');
  ensureDir(mcpDir);

  const tools = prompts.map(p => ({
    name: p.name.replace(/\./g, '_'),
    description: p.description,
    content: p.content
  }));

  const serverScript = `#!/usr/bin/env node
'use strict';
// Lightweight MCP server exposing Cosmos intent prompts as tools
const http = require('http');

const tools = ${JSON.stringify(tools, null, 2)};

const server = http.createServer((req, res) => {
  if (req.method === 'POST') {
    let body = '';
    req.on('data', d => body += d);
    req.on('end', () => {
      const msg = JSON.parse(body);
      if (msg.method === 'tools/list') {
        res.end(JSON.stringify({
          result: { tools: tools.map(t => ({ name: t.name, description: t.description, inputSchema: { type: 'object', properties: { input: { type: 'string' } } } })) }
        }));
      } else if (msg.method === 'tools/call') {
        const tool = tools.find(t => t.name === msg.params?.name);
        res.end(JSON.stringify({ result: { content: [{ type: 'text', text: tool ? tool.content : 'Unknown tool' }] } }));
      } else {
        res.end(JSON.stringify({ result: {} }));
      }
    });
  } else {
    res.end('Cosmos Intent MCP Server');
  }
});

server.listen(0, () => console.log(\`MCP server on port \${server.address().port}\`));
`;

  fs.writeFileSync(path.join(mcpDir, 'cosmos-server.js'), serverScript);
  fs.chmodSync(path.join(mcpDir, 'cosmos-server.js'), 0o755);

  // Write MCP config to .vscode and .cursor
  const mcpConfig = {
    servers: {
      'cosmos-intent': {
        command: 'node',
        args: ['.mcp/cosmos-server.js']
      }
    }
  };

  for (const dir of ['.vscode', '.cursor']) {
    ensureDir(path.join(cwd, dir));
    const configFile = path.join(cwd, dir, 'mcp.json');
    let existing = {};
    if (fs.existsSync(configFile)) {
      try { existing = JSON.parse(fs.readFileSync(configFile, 'utf8')); } catch {}
    }
    existing.servers = { ...existing.servers, ...mcpConfig.servers };
    fs.writeFileSync(configFile, JSON.stringify(existing, null, 2) + '\n');
  }
};
