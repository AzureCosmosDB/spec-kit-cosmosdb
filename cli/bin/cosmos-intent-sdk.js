#!/usr/bin/env node
'use strict';

const path = require('path');
const pkg = require('../package.json');

const args = process.argv.slice(2);
const command = args[0];

function showHelp() {
  console.log(`
cosmos-intent-sdk v${pkg.version}

Usage:
  cosmos-intent-sdk <command> [options]

Commands:
  init      Install prompt templates into the current project
  update    Re-install/update prompts (overwrites existing)
  list      List available integrations and prompts

Options:
  --help, -h       Show help
  --version, -v    Show version

Init Options:
  --integration <name>   Install specific integration (repeatable)
  --all                  Install all integrations
  --with-agent-kit       Include agent kit instructions for ongoing protection

Integrations:
  copilot    GitHub Copilot (VS Code)
  cursor     Cursor
  claude     Claude Code
  gemini     Gemini
  windsurf   Windsurf/Codeium
  mcp        MCP server (universal)

Examples:
  npx cosmos-intent-sdk init
  npx cosmos-intent-sdk init --all
  npx cosmos-intent-sdk init --integration copilot --integration claude
  npx cosmos-intent-sdk update --all
`);
}

function showVersion() {
  console.log(pkg.version);
}

function parseFlags(args) {
  const flags = { integrations: [], all: false, withAgentKit: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--all') flags.all = true;
    else if (args[i] === '--with-agent-kit') flags.withAgentKit = true;
    else if (args[i] === '--integration' && args[i + 1]) {
      flags.integrations.push(args[i + 1]);
      i++;
    }
  }
  return flags;
}

const INTEGRATIONS = ['copilot', 'cursor', 'claude', 'gemini', 'windsurf', 'mcp'];

async function promptUser() {
  const readline = require('readline');
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const ask = (q) => new Promise(r => rl.question(q, r));
  console.log('Available integrations:');
  INTEGRATIONS.forEach((n, i) => console.log(`  ${i + 1}. ${n}`));
  const answer = await ask('\nWhich integrations? (comma-separated numbers, or "all"): ');
  rl.close();
  if (answer.trim().toLowerCase() === 'all') return INTEGRATIONS;
  return answer.split(',').map(s => INTEGRATIONS[parseInt(s.trim()) - 1]).filter(Boolean);
}

async function runInit(flags) {
  let selected = flags.integrations;
  if (flags.all) selected = INTEGRATIONS;
  else if (selected.length === 0) {
    if (process.stdin.isTTY) {
      selected = await promptUser();
    } else {
      console.error('No integrations specified. Use --all or --integration <name>');
      process.exit(1);
    }
  }

  const cwd = process.cwd();
  const { loadPrompts } = require('../lib/transform');
  const prompts = loadPrompts();

  console.log(`\nInstalling ${selected.length} integration(s) with ${prompts.length} prompts...\n`);

  for (const name of selected) {
    try {
      const integration = require(`../integrations/${name}`);
      await integration.install(cwd, prompts, flags);
      console.log(`  ✓ ${name}`);
    } catch (e) {
      console.error(`  ✗ ${name}: ${e.message}`);
    }
  }

  console.log('\nDone! See each integration\'s docs for usage instructions.');
}

async function runList() {
  const { loadPrompts } = require('../lib/transform');
  const prompts = loadPrompts();
  console.log('\nAvailable integrations:', INTEGRATIONS.join(', '));
  console.log(`\nAvailable prompts (${prompts.length}):`);
  prompts.forEach(p => console.log(`  ${p.name} — ${p.description}`));
}

(async () => {
  if (args.includes('--help') || args.includes('-h') || args.length === 0) return showHelp();
  if (args.includes('--version') || args.includes('-v')) return showVersion();

  const flags = parseFlags(args.slice(1));

  switch (command) {
    case 'init':
    case 'update':
      await runInit(flags);
      break;
    case 'list':
      await runList();
      break;
    default:
      console.error(`Unknown command: ${command}`);
      showHelp();
      process.exit(1);
  }
})();
