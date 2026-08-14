#!/usr/bin/env python3
"""
Determinism testing harness for cosmos-intent-sdk prompt templates.

Runs a prompt N times with identical inputs, extracts structural features
from each output, and computes a consistency score.
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from string import Template
from typing import Any

try:
    import openai
except ImportError:
    print("Install openai: pip install openai", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None  # Fall back to JSON templates


def load_template(path: str) -> dict:
    """Load a prompt template (YAML or JSON)."""
    text = Path(path).read_text()
    if path.endswith((".yaml", ".yml")):
        if yaml is None:
            raise RuntimeError("PyYAML required for .yaml templates: pip install pyyaml")
        return yaml.safe_load(text)
    return json.loads(text)


def render_prompt(template: dict, variables: dict) -> str:
    """Render the prompt template with provided variables."""
    prompt_text = template.get("prompt", template.get("system", ""))
    # Simple $variable substitution
    return Template(prompt_text).safe_substitute(variables)


def call_llm(prompt: str, model: str, api_base: str | None = None, api_key: str | None = None) -> str:
    """Call an OpenAI-compatible endpoint."""
    client_kwargs = {}
    if api_base:
        client_kwargs["base_url"] = api_base
    if api_key:
        client_kwargs["api_key"] = api_key
    else:
        client_kwargs["api_key"] = os.environ.get("OPENAI_API_KEY", os.environ.get("GITHUB_TOKEN", ""))

    client = openai.OpenAI(**client_kwargs)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content or ""


def extract_features(output: str) -> dict[str, Any]:
    """Extract structural features from LLM output."""
    features = {}

    # Partition keys: look for /fieldName patterns or "partition key" mentions
    pk_patterns = re.findall(r'/([a-zA-Z_]\w*)', output)
    pk_mentions = re.findall(r'partition\s*key[:\s]*[`"]?(/?\w+)[`"]?', output, re.IGNORECASE)
    features["partition_keys"] = list(set(pk_patterns[:5] + [p.lstrip("/") for p in pk_mentions]))

    # Field names from JSON-like structures or backtick-quoted identifiers
    json_blocks = re.findall(r'\{[^{}]{10,}\}', output, re.DOTALL)
    field_names = set()
    for block in json_blocks:
        field_names.update(re.findall(r'"(\w+)"\s*:', block))
    # Also grab backtick-quoted field names
    field_names.update(re.findall(r'`(\w+)`', output))
    features["field_names"] = sorted(field_names)

    # Architectural patterns
    pattern_keywords = [
        "change feed", "materialized view", "event sourcing", "CQRS",
        "denormalization", "embedding", "referencing", "transactional batch",
        "bulk operations", "point read", "cross-partition", "fan-out",
    ]
    features["patterns"] = [kw for kw in pattern_keywords if kw.lower() in output.lower()]

    # SDK patterns
    sdk_keywords = [
        "CosmosClient", "CreateItemAsync", "UpsertItemAsync", "ReadItemAsync",
        "GetItemQueryIterator", "TransactionalBatch", "BulkOperations",
        "ChangeFeedProcessor", "Container.Scripts",
    ]
    features["sdk_patterns"] = [kw for kw in sdk_keywords if kw in output]

    # Consistency level
    consistency_levels = ["Strong", "BoundedStaleness", "Session", "ConsistentPrefix", "Eventual"]
    features["consistency_level"] = [cl for cl in consistency_levels if cl.lower() in output.lower()]

    # Index types
    index_keywords = ["composite index", "spatial index", "range index", "hash index", "vector index"]
    features["index_types"] = [kw for kw in index_keywords if kw.lower() in output.lower()]

    return features


def compute_consistency(all_features: list[dict]) -> dict:
    """Compute per-feature and overall consistency scores."""
    if len(all_features) < 2:
        return {"overall": 1.0, "per_feature": {}, "note": "Need >=2 iterations"}

    n = len(all_features)
    feature_keys = set()
    for f in all_features:
        feature_keys.update(f.keys())

    per_feature = {}
    for key in sorted(feature_keys):
        values = [tuple(sorted(f.get(key, []))) for f in all_features]
        # Consistency = fraction of pairs that agree
        if not any(values):
            continue
        most_common_value, most_common_count = Counter(values).most_common(1)[0]
        per_feature[key] = {
            "consistency": round(most_common_count / n, 3),
            "most_common": list(most_common_value),
            "variants": len(set(values)),
        }

    scores = [v["consistency"] for v in per_feature.values()]
    overall = round(sum(scores) / len(scores), 3) if scores else 0.0

    return {"overall": overall, "per_feature": per_feature}


def main():
    parser = argparse.ArgumentParser(description="Run determinism tests on prompt templates")
    parser.add_argument("--template", "-t", required=True, help="Path to prompt template")
    parser.add_argument("--variables", "-v", default="{}", help="JSON string of input variables")
    parser.add_argument("--iterations", "-n", type=int, default=5, help="Number of iterations")
    parser.add_argument("--model", "-m", default="gpt-4o", help="Model name")
    parser.add_argument("--api-base", help="OpenAI-compatible API base URL")
    parser.add_argument("--api-key", help="API key (or set OPENAI_API_KEY / GITHUB_TOKEN)")
    parser.add_argument("--output", "-o", help="Output report path (default: stdout)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between calls (seconds)")
    args = parser.parse_args()

    variables = json.loads(args.variables)
    template = load_template(args.template)
    prompt = render_prompt(template, variables)

    print(f"Running {args.iterations} iterations with model={args.model}", file=sys.stderr)
    print(f"Prompt length: {len(prompt)} chars", file=sys.stderr)

    outputs = []
    all_features = []

    for i in range(args.iterations):
        print(f"  Iteration {i+1}/{args.iterations}...", file=sys.stderr)
        try:
            output = call_llm(prompt, args.model, args.api_base, args.api_key)
            outputs.append(output)
            features = extract_features(output)
            all_features.append(features)
        except Exception as e:
            print(f"  ERROR on iteration {i+1}: {e}", file=sys.stderr)
            outputs.append("")
            all_features.append({})
        if i < args.iterations - 1:
            time.sleep(args.delay)

    consistency = compute_consistency(all_features)

    report = {
        "template": args.template,
        "model": args.model,
        "iterations": args.iterations,
        "variables": variables,
        "consistency": consistency,
        "features_per_run": all_features,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    report_json = json.dumps(report, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(report_json)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report_json)

    # Exit code based on score
    if consistency["overall"] >= 0.9:
        print(f"✓ Score: {consistency['overall']} (PASS)", file=sys.stderr)
    elif consistency["overall"] >= 0.7:
        print(f"⚠ Score: {consistency['overall']} (WARN)", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"✗ Score: {consistency['overall']} (FAIL)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
