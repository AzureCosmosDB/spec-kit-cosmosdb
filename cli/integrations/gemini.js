'use strict';
const fs = require('fs');
const path = require('path');
const { ensureDir } = require('../lib/transform');

exports.install = async function (cwd, prompts, flags) {
  const promptsDir = path.join(cwd, '.gemini', 'prompts');
  ensureDir(promptsDir);

  for (const p of prompts) {
    const name = p.name.replace(/^cosmos\./, 'cosmos-');
    fs.writeFileSync(path.join(promptsDir, `${name}.md`), p.content);
  }

  // Update GEMINI.md
  const geminiFile = path.join(cwd, 'GEMINI.md');
  const section = '\n\n## Cosmos Intent Prompts\n\nCosmos DB prompt templates are available in `.gemini/prompts/cosmos-*.md`.\n';
  if (fs.existsSync(geminiFile)) {
    const existing = fs.readFileSync(geminiFile, 'utf8');
    if (!existing.includes('Cosmos Intent')) {
      fs.appendFileSync(geminiFile, section);
    }
  } else {
    fs.writeFileSync(geminiFile, '# GEMINI.md\n' + section);
  }

  // Agent Kit installation
  if (flags && flags.withAgentKit) {
    const rulesContent = fs.readFileSync(path.join(__dirname, '..', 'agent-kit-rules.md'), 'utf8');
    const header = '\n\n## Cosmos DB Agent Kit\n\n';
    if (fs.existsSync(geminiFile)) {
      const existing = fs.readFileSync(geminiFile, 'utf8');
      if (!existing.includes('Cosmos DB Agent Kit')) {
        fs.appendFileSync(geminiFile, header + rulesContent);
      }
    } else {
      fs.writeFileSync(geminiFile, '# GEMINI.md\n' + header.trimStart() + rulesContent);
    }
  }
};
