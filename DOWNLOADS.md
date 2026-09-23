# Download tracking

The installation command uses an uploaded GitHub release asset. GitHub exposes a cumulative `download_count` for each asset through its public REST API. No changes to Spec Kit core or extension-side telemetry are required.

## Read the counts

With the GitHub CLI installed, show the v0.2.0 package count:

```bash
gh api repos/AzureCosmosDB/spec-kit-cosmosdb/releases/tags/v0.2.0 --jq '.assets[] | select(.name == "cosmosdb-v0.2.0.zip") | {name, download_count, created_at, browser_download_url}'
```

Show package counts across all releases:

```bash
gh api --paginate repos/AzureCosmosDB/spec-kit-cosmosdb/releases --jq '.[] | .tag_name as $tag | .assets[] | select(.name | startswith("cosmosdb-v") and endswith(".zip")) | {version: $tag, asset_id: .id, downloads: .download_count, created_at}'
```

For weekly or monthly reporting, save timestamped snapshots of asset IDs and counts. Subtract consecutive counts for the same asset ID to estimate downloads between snapshots. A replacement asset has a new ID and a new counter; do not treat it as a continuation of the old counter.

See GitHub's [release assets API documentation](https://docs.github.com/en/rest/releases/assets).

## What the numbers mean

- Counts represent asset downloads, not unique people, successful installs, or active users. Retries, CI, and maintainer validation downloads can contribute.
- Counting starts when the asset is uploaded. Historical downloads of GitHub-generated source archives cannot be recovered through this API.
- Source ZIP URLs (`/archive/refs/tags/...`), clones, forks, and local installs bypass this counter. GitHub's automatically generated "Source code" downloads are not the uploaded package.
- There is no channel attribution: README, catalog, and blog downloads share the same counter when they use the same asset URL.
- The Spec Kit community catalog's `downloads` field is not automatically synchronized by this workflow. Do not use it as the package download count.

## Publishing packages

The **Publish extension download** workflow runs when a release is published. It packages the release tag with `git archive`, checks that the manifest version matches the tag and all declared command files exist, then uploads `cosmosdb-<tag>.zip`. The archive contains the tracked source at that tag under a single top-level directory, matching the source-archive installation layout. It deliberately does not execute code from the tag.

The workflow uses GitHub Actions' built-in token with `contents: write`; no custom secret is needed. To package an existing release after the workflow is merged into the default branch:

```bash
gh workflow run release-assets.yml --repo AzureCosmosDB/spec-kit-cosmosdb --ref main -f tag=v0.2.0
```

Check that the workflow completed and the asset exists before advertising its URL. Rerunning skips an existing asset so its counter is preserved. Do not delete/re-upload assets or use `gh release upload --clobber`; publish a new version for changed contents.

For each release, update the README version and install URL to:

```text
https://github.com/AzureCosmosDB/spec-kit-cosmosdb/releases/download/<tag>/cosmosdb-<tag>.zip
```

Also update installation links in blog posts and other maintained documentation. Request an update to the Spec Kit community catalog's `download_url` through its [extension submission process](https://github.com/github/spec-kit/issues/new?template=extension_submission.yml). This is a catalog metadata change, not a Spec Kit core code change. Older archive links continue to work but remain outside the asset counter.