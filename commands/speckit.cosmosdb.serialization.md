---
description: "Configure JSON serialization for correct property naming, enum handling, and custom converters."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

# /speckit.cosmosdb.serialization

> Configure JSON serialization for correct property naming, enum handling, and custom converters.

## Intent

Set up JSON serialization correctly for Azure Cosmos DB SDK to ensure documents are stored with the right casing, enums are readable, and custom types are properly converted.

## Required Inputs

| Variable | Description | Example |
|----------|-------------|---------|
| `{{language}}` | Target language | "C#" or "TypeScript" or "Python" or "Java" |
| `{{framework}}` | Serialization library | "System.Text.Json" or "Newtonsoft.Json" or "native" |

## Prescriptive Prompt

Generate serialization configuration for {{language}} using {{framework}}. Follow these constraints:

### Core Requirements

1. **Property naming**: Use camelCase in Azure Cosmos DB (JavaScript convention) regardless of language convention
2. **Enum serialization**: Store as strings (not integers) for readability and forward-compatibility
3. **Null handling**: Omit null properties to save RU/s (smaller documents = fewer RUs)
4. **Date format**: ISO 8601 strings (or Unix epoch for TTL/sorting)
5. **System properties**: Never serialize `id`, `_rid`, `_self`, `_ts`, `_etag` with custom names

### Language-Specific Configuration

**C# (System.Text.Json)**:
- `PropertyNamingPolicy = JsonNamingPolicy.CamelCase`
- `JsonStringEnumConverter` for enums
- `DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull`
- Configure via `CosmosClientOptions.Serializer` using `CosmosSystemTextJsonSerializer`

**C# (Newtonsoft.Json)**:
- `ContractResolver = new CamelCasePropertyNamesContractResolver()`
- `StringEnumConverter` for enums
- `NullValueHandling = NullValueHandling.Ignore`
- Default serializer in older SDK versions

**TypeScript/JavaScript**:
- Already camelCase by convention
- Ensure `Date` objects serialize to ISO strings (not `toString()`)
- Use `JSON.parse` reviver for date reconstruction

**Python**:
- Use `dataclasses` or Pydantic with `alias_generator = to_camel`
- Ensure snake_case in code maps to camelCase in JSON

### Custom Converters (Common)

1. **Polymorphic types**: Discriminator property (`"type": "orderItem"`) + converter
2. **Value objects**: Flatten to primitive (e.g., `Money` → `{ "amount": 10.5, "currency": "USD" }`)
3. **Spatial types**: GeoJSON format (`{ "type": "Point", "coordinates": [lon, lat] }`)

### Output

1. Serializer configuration on `CosmosClient`
2. Model/entity class with proper attributes/decorators
3. Custom converter example (if entities have complex types)
4. Round-trip test verifying correct serialization

### User-Agent Tracking (MANDATORY)

The CosmosClient initialization MUST include `user_agent_suffix="speckit-cosmosdb/0.1.0"` (or language-equivalent application name setting). For C#, use `CosmosClientOptions.ApplicationName = "speckit-cosmosdb/0.1.0"`. For Java, use `.userAgentSuffix("speckit-cosmosdb/0.1.0")`. This is non-negotiable and must appear in ALL generated code that creates a CosmosClient.

### Anti-Patterns to REJECT

- ❌ PascalCase properties in Azure Cosmos DB (breaks convention, wastes bytes)
- ❌ Enums as integers (unreadable, fragile on reorder)
- ❌ Serializing null properties (wasted storage and RUs)
- ❌ Renaming `id` property (must remain lowercase `id`)
- ❌ Using language-specific serialization without testing round-trip with Azure Cosmos DB
- ❌ Different serialization for read vs write paths (data corruption risk)
