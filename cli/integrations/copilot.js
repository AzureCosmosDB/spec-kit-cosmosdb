'use strict';
const fs = require('fs');
const path = require('path');
const { toFrontmatter, ensureDir } = require('../lib/transform');

exports.install = async function (cwd, prompts, flags) {
  const agentsDir = path.join(cwd, '.github', 'agents');
  const promptsDir = path.join(cwd, '.github', 'prompts');
  ensureDir(agentsDir);
  ensureDir(promptsDir);

  for (const p of prompts) {
    const fm = toFrontmatter({ description: p.description });
    fs.writeFileSync(path.join(agentsDir, `${p.name}.agent.md`), fm + '\n' + p.content);
    fs.writeFileSync(path.join(promptsDir, `${p.name}.prompt.md`), fm + '\n' + p.content);
  }

  // Update .vscode/settings.json
  const vsDir = path.join(cwd, '.vscode');
  ensureDir(vsDir);
  const settingsFile = path.join(vsDir, 'settings.json');
  let settings = {};
  if (fs.existsSync(settingsFile)) {
    try { settings = JSON.parse(fs.readFileSync(settingsFile, 'utf8')); } catch {}
  }
  settings['github.copilot.chat.promptFiles'] = true;
  fs.writeFileSync(settingsFile, JSON.stringify(settings, null, 2) + '\n');

  // Agent Kit installation
  if (flags && flags.withAgentKit) {
    const rulesContent = fs.readFileSync(path.join(__dirname, '..', 'agent-kit-rules.md'), 'utf8');

    // Append to .github/copilot-instructions.md
    const instructionsFile = path.join(cwd, '.github', 'copilot-instructions.md');
    ensureDir(path.dirname(instructionsFile));
    const header = '\n\n## Cosmos DB Agent Kit\n\n';
    if (fs.existsSync(instructionsFile)) {
      const existing = fs.readFileSync(instructionsFile, 'utf8');
      if (!existing.includes('Cosmos DB Agent Kit')) {
        fs.appendFileSync(instructionsFile, header + rulesContent);
      }
    } else {
      fs.writeFileSync(instructionsFile, header.trimStart() + rulesContent);
    }

    // Install as .github/instructions/cosmos-agent-kit.instructions.md
    const instrDir = path.join(cwd, '.github', 'instructions');
    ensureDir(instrDir);
    const fm = '---\napplyTo: "**/*"\n---\n\n';
    fs.writeFileSync(path.join(instrDir, 'cosmos-agent-kit.instructions.md'), fm + rulesContent);
  }
};
