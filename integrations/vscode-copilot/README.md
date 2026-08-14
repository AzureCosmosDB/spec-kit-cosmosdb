# VS Code Copilot Integration

## Overview

Use speckit-cosmosdb prompt templates as VS Code Copilot Chat participants or via `.github/copilot-instructions.md`.

## Option 1: Copilot Instructions (Zero Code)

Add a `.github/copilot-instructions.md` to your repository:

```markdown
## Cosmos DB Design

When asked to design Cosmos DB containers, data models, or queries, follow these rules:

- Always specify a partition key with high cardinality
- Prefer denormalization over joins for read-heavy workloads
- Embed child entities when they're always accessed with the parent
- Use change feed for materialized views, not cross-container queries
- Default to Session consistency unless requirements demand otherwise
- Recommend composite indexes for multi-field ORDER BY

Reference the speckit-cosmosdb prompt structure:
1. Describe the entity and access patterns
2. Output: partition key, schema, indexes, SDK code sample, RU estimate
```

## Option 2: Chat Participant Extension

Build a VS Code extension that registers a `@cosmos` chat participant:

```typescript
// extension.ts
import * as vscode from 'vscode';
import { loadTemplate, renderPrompt } from 'speckit-cosmosdb';

export function activate(context: vscode.ExtensionContext) {
  const participant = vscode.chat.createChatParticipant('cosmos', async (request, context, stream, token) => {
    const template = loadTemplate('design-container');
    const rendered = renderPrompt(template, {
      entity: request.prompt,
      access_patterns: extractPatterns(request.prompt),
    });

    // Stream the rendered prompt as context to Copilot
    stream.markdown('Designing Cosmos DB container...\n\n');

    const response = await request.model.sendRequest([
      vscode.LanguageModelChatMessage.User(rendered)
    ], {}, token);

    for await (const chunk of response.text) {
      stream.markdown(chunk);
    }
  });

  participant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'cosmos-icon.png');
  context.subscriptions.push(participant);
}
```

### Slash Commands

Register specific templates as slash commands:

```typescript
participant.commandProvider = {
  provideCommands: () => [
    { name: 'design', description: 'Design a container schema' },
    { name: 'query', description: 'Generate an optimized query' },
    { name: 'migrate', description: 'Plan a migration strategy' },
    { name: 'index', description: 'Recommend indexing policy' },
  ]
};
```

Usage in Copilot Chat:
```
@cosmos /design An e-commerce order system with customer lookup and date range queries
@cosmos /query Find all orders for customer X in the last 30 days
@cosmos /index Optimize for queries filtering on status + createdAt
```

## Option 3: Prompt Files (`.prompt.md`)

VS Code Copilot supports `.prompt.md` files in `.github/prompts/`:

```markdown
---
mode: agent
tools: []
---

# Design Cosmos DB Container

Given the following entity description and access patterns, design an optimal
Cosmos DB container following best practices.

## Rules
- Partition key must have high cardinality and appear in most query filters
- Embed related data accessed together; reference data accessed independently
- Include composite indexes for multi-field sorts
- Estimate RU cost for primary operations

## Entity
${input:entity_description}

## Access Patterns
${input:access_patterns}
```

Then invoke via: `@workspace /prompt Design Cosmos DB Container`
