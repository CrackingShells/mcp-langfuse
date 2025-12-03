# Langfuse REST API Capabilities - Analysis Report

**Report Date**: 2025-12-03
**Report Version**: v0
**Purpose**: Analyze Langfuse REST API to identify capabilities for building advanced trace exploration tools

---

## Executive Summary

The Langfuse REST API provides comprehensive endpoints for trace data retrieval, with powerful filtering and querying capabilities that are **underutilized by existing MCP servers**. Key findings:

- **Rich observation data** includes parent-child relationships, timestamps, and metadata
- **Advanced filtering** supports complex queries with JSON filter syntax
- **Metrics API** enables aggregation and analytics
- **Session grouping** provides natural boundaries for temporal reconstruction
- **Observation types** (SPAN, GENERATION, EVENT) enable tool call identification

**Critical Insight**: The API provides all necessary primitives to build sophisticated trace analysis tools - existing servers simply don't leverage them.

---

## 1. Core Data Retrieval Endpoints

### 1.1 Traces API

**Endpoint**: `GET /api/public/traces`

**Query Parameters**:
- **Pagination**: `page`, `limit`
- **Filtering**: `userId`, `name`, `sessionId`, `tags`, `version`, `release`, `environment`
- **Time range**: `fromTimestamp`, `toTimestamp`
- **Ordering**: `orderBy` (format: `field.asc|desc`)
  - Available fields: `id`, `timestamp`, `name`, `userId`, `release`, `version`, `public`, `bookmarked`, `sessionId`
- **Field selection**: `fields` parameter for controlling response size
  - Groups: `core` (always included), `io`, `scores`, `observations`, `metrics`
  - Example: `fields=core,scores,metrics` (excludes observations and I/O)
- **Advanced filtering**: `filter` parameter (JSON string with complex conditions)

**Response Structure** (`TraceWithFullDetails`):
```json
{
  "id": "string",
  "timestamp": "datetime",
  "name": "string",
  "userId": "string",
  "sessionId": "string",
  "release": "string",
  "version": "string",
  "metadata": {},
  "tags": [],
  "input": {},
  "output": {},
  "htmlPath": "string",
  "latency": "number (seconds)",
  "totalCost": "number (USD)",
  "observations": [ObservationsView],
  "scores": [ScoreV1]
}
```

**Key Capabilities**:
- Retrieve traces with full observation trees
- Filter by session for grouping related traces
- Time-based ordering for temporal analysis
- Cost and latency metrics included

### 1.2 Observations API

**Endpoint**: `GET /api/public/observations`

**Query Parameters**:
- **Pagination**: `page`, `limit`
- **Filtering**: `name`, `userId`, `type`, `traceId`, `parentObservationId`, `level`, `environment`, `version`
- **Time range**: `fromStartTime`, `toStartTime`
- **Advanced filtering**: `filter` parameter (JSON string)

**Observation Types**:
- `SPAN` - Execution spans (typically tool calls, function executions)
- `GENERATION` - LLM generations (model calls)
- `EVENT` - Discrete events (logging, checkpoints)

**Response Structure** (`Observation`):
```json
{
  "id": "string",
  "traceId": "string",
  "type": "SPAN|GENERATION|EVENT",
  "name": "string",
  "startTime": "datetime",
  "endTime": "datetime",
  "completionStartTime": "datetime",
  "model": "string",
  "modelParameters": {},
  "input": {},
  "output": {},
  "metadata": {},
  "usage": {},
  "usageDetails": {},
  "costDetails": {},
  "level": "DEBUG|DEFAULT|WARNING|ERROR",
  "statusMessage": "string",
  "parentObservationId": "string",
  "promptId": "string",
  "version": "string",
  "environment": "string"
}
```

**Key Capabilities**:
- **Parent-child relationships**: `parentObservationId` enables tree reconstruction
- **Temporal data**: `startTime`, `endTime`, `completionStartTime` for ordering
- **Type discrimination**: Filter by `type` to isolate tool calls (SPANs)
- **Hierarchical structure**: Build execution trees from parent references
- **Rich metadata**: Input/output capture for context extraction

### 1.3 Sessions API

**Endpoint**: `GET /api/public/sessions`

**Query Parameters**:
- **Pagination**: `page`, `limit`
- **Time range**: `fromTimestamp`, `toTimestamp`
- **Environment**: `environment` filter

**Endpoint**: `GET /api/public/sessions/{sessionId}`

**Response Structure** (`SessionWithTraces`):
```json
{
  "id": "string",
  "createdAt": "datetime",
  "projectId": "string",
  "environment": "string",
  "traces": [Trace]
}
```

**Key Capabilities**:
- **Natural grouping**: Sessions group related traces
- **Temporal boundaries**: Session provides context window
- **Warning**: Single session endpoint returns non-paginated traces (use `GET /api/public/traces?sessionId=<id>` for large sessions)

---

## 2. Advanced Filtering Capabilities

### 2.1 JSON Filter Syntax

Both traces and observations support complex filtering via JSON `filter` parameter:

**Filter Structure**:
```json
[
  {
    "type": "string|number|datetime|stringOptions|categoryOptions|arrayOptions|stringObject|numberObject|boolean|null",
    "column": "field_name",
    "operator": "=|>|<|>=|<=|contains|starts with|ends with|any of|none of|all of|is null|is not null",
    "value": "any",
    "key": "string (for nested fields like metadata)"
  }
]
```

**Operators by Type**:
- **datetime**: `>`, `<`, `>=`, `<=`
- **string**: `=`, `contains`, `does not contain`, `starts with`, `ends with`
- **stringOptions**: `any of`, `none of`
- **arrayOptions**: `any of`, `none of`, `all of`
- **number**: `=`, `>`, `<`, `>=`, `<=`
- **boolean**: `=`, `<>`
- **null**: `is null`, `is not null`

**Available Columns (Observations)**:
- Core: `id`, `type`, `name`, `traceId`, `startTime`, `endTime`
- Metadata: `metadata.*` (using `key` parameter)
- Model: `model`, `modelParameters.*`
- Hierarchy: `parentObservationId`
- Status: `level`, `statusMessage`

**Example Use Cases**:
```json
// Find all tool calls (SPANs) with "search" in name
[
  {"type": "string", "column": "type", "operator": "=", "value": "SPAN"},
  {"type": "string", "column": "name", "operator": "contains", "value": "search"}
]

// Find observations with specific metadata
[
  {"type": "stringObject", "column": "metadata", "operator": "=", "value": "tool_call", "key": "type"}
]

// Find slow operations (>5 seconds)
[
  {"type": "number", "column": "latency", "operator": ">", "value": 5}
]
```

### 2.2 Field Selection

**Traces `fields` parameter** enables response size optimization:
- `core` - Always included (id, timestamp, name, userId, sessionId, etc.)
- `io` - Input, output, metadata
- `scores` - Score data
- `observations` - Full observation tree
- `metrics` - totalCost, latency

**Strategy**: Use `fields=core` for listing, then fetch full details for specific traces.

---

## 3. Metrics and Analytics API

**Endpoint**: `GET /api/public/metrics`

**Query Structure** (JSON string):
```json
{
  "view": "traces|observations|scores-numeric|scores-categorical",
  "dimensions": [
    {"field": "name|userId|sessionId|..."}
  ],
  "metrics": [
    {
      "measure": "count|latency|value|cost",
      "aggregation": "count|sum|avg|p95|histogram"
    }
  ],
  "filters": [...],
  "timeDimension": {
    "granularity": "minute|hour|day|week|month|auto"
  },
  "fromTimestamp": "ISO datetime",
  "toTimestamp": "ISO datetime",
  "orderBy": [
    {"field": "...", "direction": "asc|desc"}
  ],
  "config": {
    "bins": 10,
    "row_limit": 1000
  }
}
```

**Key Capabilities**:
- **Aggregation**: Count, sum, average, percentiles, histograms
- **Grouping**: By any dimension (name, userId, sessionId, etc.)
- **Time series**: Group by time with configurable granularity
- **Multi-metric**: Calculate multiple metrics in single query
- **Histogram support**: Distribution analysis with configurable bins

**Use Cases for Tool Call Analysis**:
- Count tool calls by type/name
- Average latency per tool
- Tool usage over time
- Cost analysis per tool
- Error rate by tool type

---

## 4. Data Structures for Temporal Reconstruction

### 4.1 Observation Hierarchy

**Parent-Child Relationships**:
- Each observation has optional `parentObservationId`
- Root observations have `parentObservationId: null`
- Tree structure: Trace → Root Observations → Child Observations → ...

**Temporal Markers**:
- `startTime` - When observation began
- `endTime` - When observation completed
- `completionStartTime` - When completion phase started (for streaming)

**Reconstruction Strategy**:
1. Fetch all observations for a trace/session
2. Build tree using `parentObservationId` references
3. Sort siblings by `startTime` for temporal ordering
4. Handle missing timestamps with parent context

### 4.2 Session-Based Grouping

**Session as Context Window**:
- Session groups related traces
- Traces within session share temporal context
- Session `createdAt` provides baseline timestamp

**Multi-Trace Ordering**:
1. Fetch all traces for session (ordered by timestamp)
2. For each trace, fetch observations
3. Merge observation streams using timestamps
4. Maintain trace boundaries for context

---

## 5. Tool Call Identification Patterns

### 5.1 Observation Type Filtering

**SPAN observations** typically represent:
- Function/tool calls
- External API calls
- Database queries
- Custom instrumented code blocks

**Identification Strategy**:
```
Filter: type = "SPAN"
Additional: name contains tool/function keywords
Check: input/output structure for tool call patterns
```

### 5.2 Metadata Inspection

**Common metadata patterns**:
```json
{
  "metadata": {
    "type": "tool_call",
    "tool_name": "search_web",
    "tool_id": "call_abc123"
  }
}
```

**Name patterns**:
- `tool_*` prefix
- `function_*` prefix
- Specific tool names (e.g., `search_web`, `calculator`, `file_read`)

### 5.3 Input/Output Structure

**Tool call input pattern**:
```json
{
  "input": {
    "tool": "search_web",
    "arguments": {
      "query": "...",
      "max_results": 10
    }
  }
}
```

**Tool call output pattern**:
```json
{
  "output": {
    "result": [...],
    "status": "success"
  }
}
```

---

## 6. Context Association Strategies

### 6.1 Prompt-to-Tool Linking

**Pattern 1: Parent-Child Relationship**
- GENERATION (LLM call) → SPAN (tool call)
- Parent observation contains prompt
- Child observation is tool execution

**Pattern 2: Temporal Proximity**
- Find GENERATION observations before SPAN
- Within same trace
- Time gap < threshold (e.g., 1 second)

**Pattern 3: Metadata References**
- Tool call metadata references prompt ID
- Use `promptId` field in observation

### 6.2 Multi-Hop Context

**Scenario**: User query → LLM → Tool → LLM → Response

**Reconstruction**:
1. Identify root observation (user input)
2. Traverse children to find GENERATION
3. Find SPAN children of GENERATION (tools)
4. Find subsequent GENERATION (response synthesis)
5. Build narrative: Query → Reasoning → Tool Use → Synthesis

---

## 7. API Capabilities Summary

### What the API Provides

✅ **Complete observation data** with parent-child relationships
✅ **Temporal markers** for ordering reconstruction
✅ **Type discrimination** for tool call identification
✅ **Rich metadata** for context extraction
✅ **Advanced filtering** for complex queries
✅ **Aggregation capabilities** via Metrics API
✅ **Session grouping** for natural boundaries
✅ **Field selection** for performance optimization

### What the API Does NOT Provide

❌ **Pre-built temporal ordering** - Must reconstruct from timestamps
❌ **Tool call extraction** - Must identify from type/name/metadata
❌ **Context association** - Must infer from relationships
❌ **Graph visualization** - Must generate from data
❌ **Keyword search** - Must implement client-side or use filters
❌ **Semantic search** - No embedding/vector search

---

## 8. Design Implications for New MCP Server

### 8.1 Required Processing Capabilities

1. **Tree Reconstruction**
   - Build observation trees from `parentObservationId` references
   - Handle orphaned observations (missing parents)
   - Sort siblings by `startTime`

2. **Temporal Ordering**
   - Sort observations across traces within session
   - Handle missing/null timestamps
   - Infer ordering from parent-child relationships

3. **Tool Call Extraction**
   - Filter by `type = "SPAN"`
   - Pattern match on `name` field
   - Inspect `metadata` for tool indicators
   - Parse `input`/`output` structures

4. **Context Association**
   - Link tools to triggering prompts (parent GENERATION)
   - Extract surrounding observations for context
   - Build execution narratives

5. **Keyword Search**
   - Search across `input`, `output`, `metadata` fields
   - Support regex/pattern matching
   - Aggregate results across observations

### 8.2 Optimization Strategies

1. **Pagination Management**
   - Fetch observations in batches
   - Cache results for repeated queries
   - Use `fields` parameter to reduce payload

2. **Filter Optimization**
   - Use JSON filters for server-side filtering
   - Combine multiple conditions in single query
   - Leverage indexes (type, traceId, sessionId)

3. **Metrics Pre-computation**
   - Use Metrics API for aggregations
   - Cache statistics for common queries
   - Avoid client-side aggregation when possible

### 8.3 Tool Design Patterns

**Pattern 1: Hierarchical Retrieval**
```
Session → Traces → Observations → Tool Calls
```

**Pattern 2: Filter-First**
```
Filter observations by type/name → Fetch full details → Process
```

**Pattern 3: Context Expansion**
```
Find tool call → Get parent → Get siblings → Build context
```

---

## 9. Comparison with Existing Servers

| Capability | API Provides | avivsinai Uses | **New Server Should** |
|------------|--------------|----------------|----------------------|
| **Observation filtering** | ✅ Advanced JSON | ✅ Basic params | ✅ Full JSON filters |
| **Parent-child data** | ✅ Yes | ✅ Returns raw | ✅ Build trees |
| **Temporal markers** | ✅ Yes | ✅ Returns raw | ✅ Reconstruct order |
| **Type discrimination** | ✅ Yes | ✅ Returns raw | ✅ Extract tool calls |
| **Metadata** | ✅ Rich | ✅ Returns raw | ✅ Parse patterns |
| **Metrics API** | ✅ Powerful | ❌ Not used | ✅ Leverage for analytics |
| **Field selection** | ✅ Yes | ❌ Not used | ✅ Optimize queries |

**Key Insight**: The API provides all necessary primitives. Existing servers don't process the data - they just pass it through. A new server must add intelligence.

---

## 10. Conclusion

The Langfuse REST API is **feature-rich and well-designed** for building sophisticated trace analysis tools. It provides:

- Complete data access with hierarchical relationships
- Powerful filtering and querying capabilities
- Aggregation and analytics support
- Performance optimization features

**The gap is not in the API - it's in the processing layer.** Existing MCP servers act as thin wrappers, returning raw API responses without:
- Reconstructing temporal sequences
- Extracting tool calls intelligently
- Building context associations
- Generating insights or visualizations

**A new MCP server must bridge this gap** by implementing intelligent data processing on top of the API primitives.

---

**Next Steps**: Design MCP tools that leverage API capabilities to provide advanced trace exploration and tool call analysis.
