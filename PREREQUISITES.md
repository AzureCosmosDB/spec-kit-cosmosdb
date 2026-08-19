# PREREQUISITES.md — full setup walkthrough (personal / initial-use aid)

> **Not linked from the README.** This is a throwaway copy-paste walkthrough for
> initial self-testing. The **canonical, always-current** instructions live in the
> [Spec Kit docs](https://github.com/github/spec-kit) — if anything here drifts,
> trust Spec Kit's docs, not this file.
>
> - Spec Kit installation guide: <https://github.com/github/spec-kit/blob/main/docs/installation.md>
> - Spec Kit Get Started: <https://github.com/github/spec-kit#-get-started>

## 1. Install `uv`

Spec Kit's CLI is installed via [uv](https://docs.astral.sh/uv/). Install it:
see <https://docs.astral.sh/uv/getting-started/installation/>.

## 2. Install the Specify CLI

From PyPI (simplest):

```bash
uv tool install specify-cli
```

Or pin a specific Spec Kit release (keep the leading `v`):

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

Verify:

```bash
specify --help
```

## 3. Initialize a project for your AI coding agent

Pick the integration for your agent (Copilot shown; Spec Kit supports others):

```bash
specify init my-project --integration copilot
cd my-project
```

## 4. Install the Azure Cosmos DB extension

**Public (once v0.1.0 is released):**

```bash
specify extension add cosmosdb --from https://github.com/AzureCosmosDB/spec-kit-cosmosdb/archive/refs/tags/v0.1.0.zip
```

**Private self-test — local zip (no auth):**

```bash
# from a clone of the repo
git archive --format=zip --prefix=spec-kit-cosmosdb/ -o /tmp/cosmosdb-v0.1.0.zip HEAD
specify extension add cosmosdb --from /tmp/cosmosdb-v0.1.0.zip
```

**Private self-test — pre-release RC (authenticated):**

```bash
gh release download v0.1.0-rc1 -R AzureCosmosDB/spec-kit-cosmosdb -A zip -D /tmp
specify extension add cosmosdb --from /tmp/spec-kit-cosmosdb-*.zip
```

## 5. Verify

- `/speckit.cosmosdb.*` commands appear (expect **53**).
- Two hooks registered: `before_implement → advise`, `after_implement → review`.
- See the smoke-test steps for the guided flow, a scaffold, and hook firing.

---

_Delete or ignore this file for the public release — user-facing setup is the
README's Prerequisites section, which points at Spec Kit's canonical docs._
