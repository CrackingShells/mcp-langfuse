# New Langfuse MCP Server - Perspective and Design

**Report Date**: 2025-12-03
**Report Version**: v0
**Purpose**: Justify and outline design for a new Langfuse MCP server focused on advanced trace exploration

---

## Executive Summary

**Why Another MCP Server?**

Existing Langfuse MCP servers are either basic API wrappers or focused on prompt management. None provide **intelligent trace exploration** with tool call extraction, temporal reconstruction, and contextual analysis. The Langfuse REST API provides all necessary primitives, but requires a **processing layer** to transform raw data into actionable insights.

**Target Use Case**: Scraping tool calls with prompt context from agent execution traces, with temporal ordering reconstruction from fragmented observation data.

**MVP Scope**: Tool call extraction with context association, leveraging session grouping and temporal reconstruction.

---

## 1. Problem Statement

### 1.1 Current Limitations

**Existing servers provide**:
- Raw API responses without processing
- Basic filtering (parameter pass-through)
- No temporal reconstruction
- No tool call identification
- No context association

**What's needed**:
- Intelligent extraction of tool calls from observation streams
- Temporal ordering reconstruction when data lacks explicit sequencing
- Context association (tool calls ↔ prompts)
- Keyword search across trace content
- Graph generation for execution visualization

### 1.2 Specific Challenge: Temporal Ordering

**Problem**: Langfuse observations may lack explicit sequencing within a session. Data is a "sea of individual observations" grouped only by `sessionId` or `traceId`.

**Solution Requirements**:
1. Reconstruct execution order from timestamps (`startTime`, `endTime`)
2. Use parent-child relationships (`parentObservationId`) for hierarchy
3. Handle missing/null timestamps with contextual inference
4. Sort observations across multiple traces within a session
5. Maintain causal relationships (prompt → tool → response)

---

## 2. Why a New Server is Justified

### 2.1 Gap Analysis

| Requirement | Existing Servers | New Server |
|-------------|------------------|------------|
| **Tool call extraction** | ❌ None | ✅ Type-based + pattern matching |
| **Temporal reconstruction** | ❌ None | ✅ Timestamp + hierarchy analysis |
| **Context association** | ❌ None | ✅ Parent-child + proximity |
| **Keyword search** | ❌ None | ✅ Content search across fields |
| **Graph generation** | ❌ None | ✅ Execution flow visualization |
| **Data processing** | ❌ Minimal | ✅ Intelligent transformation |

### 2.2 Value Proposition

**For AI Agents**:
- Understand tool usage patterns in agent executions
- Extract training data (prompt → tool → result sequences)
- Debug agent behavior with temporal context
- Analyze tool effectiveness and failure modes

**For Developers**:
- Visualize agent execution flows
- Identify bottlenecks and optimization opportunities
- Search for specific tool usage patterns
- Generate reports on tool call statistics

**For Research**:
- Study agent reasoning patterns
- Analyze tool selection strategies
- Build datasets for fine-tuning
- Evaluate agent performance metrics

---

## 3. Design Principles

### 3.1 Intelligence Over Wrapping

**Principle**: Add value through data processing, not just API access.

**Implementation**:
- Parse and interpret observation structures
- Reconstruct relationships and sequences
- Generate insights and summaries
- Transform raw data into actionable information

### 3.2 Context-Aware Extraction

**Principle**: Tool calls are meaningless without context.

**Implementation**:
- Always associate tool calls with triggering prompts
- Include surrounding observations for narrative
- Capture input/output for complete picture
- Maintain temporal relationships

### 3.3 Flexible Granularity

**Principle**: Support both high-level overview and deep-dive analysis.

**Implementation**:
- Summary mode: Tool call counts, types, success rates
- Detailed mode: Full tool call data with context
- Drill-down: From session → trace → observation → tool call

### 3.4 Performance Optimization

**Principle**: Minimize API calls, maximize caching.

**Implementation**:
- Use field selection to reduce payload
- Cache processed results
- Batch operations when possible
- Leverage server-side filtering

---

## 4. MVP Scope: Tool Call Scraper

### 4.1 Core Functionality

**Goal**: Extract tool calls with prompt context from agent execution traces.

**Deliverables**:
1. Identify tool calls (SPAN observations)
2. Extract tool name, arguments, results
3. Associate with triggering prompt (parent GENERATION)
4. Reconstruct temporal ordering within session
5. Return structured data for analysis

### 4.2 MVP Tools (5 Tools)

#### Tool 1: `extract_tool_calls_from_session`

**Purpose**: Extract all tool calls from a session with context.

**Parameters**:
- `session_id` (required): Session identifier
- `include_context` (optional, default=true): Include prompt context
- `time_ordered` (optional, default=true): Sort by execution time
- `filter_tool_names` (optional): List of tool names to include

**Returns**:
```json
{
  "session_id": "string",
  "session_created_at": "datetime",
  "total_tool_calls": "number",
  "tool_calls": [
    {
      "tool_call_id": "string",
      "tool_name": "string",
      "tool_type": "string",
      "timestamp": "datetime",
      "duration_seconds": "number",
      "arguments": {},
      "result": {},
      "status": "success|error",
      "context": {
        "prompt": "string",
        "prompt_observation_id": "string",
        "trace_id": "string",
        "user_id": "string"
      }
    }
  ]
}
```

**Processing Logic**:
1. Fetch all traces for session (ordered by timestamp)
2. For each trace, fetch observations filtered by `type=SPAN`
3. For each SPAN, identify parent GENERATION (prompt)
4. Extract tool name from observation name/metadata
5. Parse arguments from input, results from output
6. Sort by startTime for temporal ordering
7. Return structured data

#### Tool 2: `extract_tool_calls_from_trace`

**Purpose**: Extract tool calls from a single trace.

**Parameters**:
- `trace_id` (required): Trace identifier
- `include_context` (optional, default=true): Include prompt context
- `build_execution_tree` (optional, default=false): Return hierarchical structure

**Returns**:
```json
{
  "trace_id": "string",
  "trace_name": "string",
  "trace_timestamp": "datetime",
  "total_tool_calls": "number",
  "tool_calls": [...],
  "execution_tree": {
    "root": {
      "observation_id": "string",
      "type": "GENERATION",
      "children": [
        {
          "observation_id": "string",
          "type": "SPAN",
          "tool_name": "string",
          "children": [...]
        }
      ]
    }
  }
}
```

**Processing Logic**:
1. Fetch trace with full observations
2. Filter observations by `type=SPAN`
3. Build parent-child tree using `parentObservationId`
4. Extract tool call data from SPANs
5. Associate with parent GENERATION for context
6. Optionally return tree structure

#### Tool 3: `search_tool_calls_by_keyword`

**Purpose**: Search for tool calls containing specific keywords in input/output.

**Parameters**:
- `keyword` (required): Search term
- `search_fields` (optional, default=["input", "output", "metadata"]): Fields to search
- `session_id` (optional): Limit to specific session
- `from_timestamp` (optional): Start of time range
- `to_timestamp` (optional): End of time range
- `limit` (optional, default=50): Max results

**Returns**:
```json
{
  "keyword": "string",
  "total_matches": "number",
  "matches": [
    {
      "tool_call_id": "string",
      "tool_name": "string",
      "matched_field": "input|output|metadata",
      "matched_content": "string (excerpt)",
      "timestamp": "datetime",
      "trace_id": "string",
      "session_id": "string",
      "context": {...}
    }
  ]
}
```

**Processing Logic**:
1. Fetch observations filtered by `type=SPAN` and time range
2. For each observation, search specified fields for keyword
3. Extract matching content with context window
4. Associate with parent for prompt context
5. Sort by relevance or timestamp
6. Return matches with excerpts

#### Tool 4: `get_tool_call_statistics`

**Purpose**: Generate statistics on tool usage patterns.

**Parameters**:
- `session_id` (optional): Specific session
- `from_timestamp` (optional): Start of time range
- `to_timestamp` (optional): End of time range
- `group_by` (optional, default="tool_name"): Grouping dimension

**Returns**:
```json
{
  "time_range": {
    "from": "datetime",
    "to": "datetime"
  },
  "total_tool_calls": "number",
  "unique_tools": "number",
  "statistics": [
    {
      "tool_name": "string",
      "call_count": "number",
      "success_rate": "number (0-1)",
      "avg_duration_seconds": "number",
      "total_cost_usd": "number",
      "error_count": "number"
    }
  ]
}
```

**Processing Logic**:
1. Use Metrics API to aggregate tool call data
2. Filter observations by `type=SPAN`
3. Group by tool name (from observation name)
4. Calculate: count, success rate, avg duration, cost
5. Return sorted by call count

#### Tool 5: `reconstruct_execution_timeline`

**Purpose**: Build time-ordered execution timeline for a session.

**Parameters**:
- `session_id` (required): Session identifier
- `include_generations` (optional, default=true): Include LLM calls
- `include_tool_calls` (optional, default=true): Include tool calls
- `include_events` (optional, default=false): Include EVENT observations

**Returns**:
```json
{
  "session_id": "string",
  "timeline": [
    {
      "timestamp": "datetime",
      "type": "GENERATION|SPAN|EVENT",
      "observation_id": "string",
      "name": "string",
      "duration_seconds": "number",
      "summary": "string",
      "parent_id": "string",
      "children_count": "number"
    }
  ],
  "total_duration_seconds": "number",
  "observation_count": "number"
}
```

**Processing Logic**:
1. Fetch all traces for session
2. Fetch all observations for traces
3. Filter by requested types (GENERATION, SPAN, EVENT)
4. Sort by `startTime` (handle nulls with parent context)
5. Build timeline with parent-child indicators
6. Calculate total duration and counts

---

## 5. Technical Architecture

### 5.1 Data Flow

```
MCP Client (AI Agent)
    ↓
MCP Tool Call
    ↓
Tool Handler (Python)
    ↓
Langfuse REST API (filtered queries)
    ↓
Data Processor (tree building, extraction, ordering)
    ↓
Result Formatter (structured JSON)
    ↓
MCP Response
```

### 5.2 Core Components

**1. API Client Layer**
- Langfuse SDK wrapper
- Request optimization (field selection, batching)
- Error handling and retry logic
- Response caching

**2. Data Processing Layer**
- Tree builder (parent-child relationships)
- Temporal sorter (timestamp-based ordering)
- Tool call extractor (type + pattern matching)
- Context associator (prompt linking)

**3. Search Engine**
- Keyword matcher (regex/fuzzy)
- Field selector (input/output/metadata)
- Result ranker (relevance scoring)

**4. Analytics Engine**
- Aggregation calculator (counts, averages, percentiles)
- Statistics generator (success rates, costs)
- Metrics API wrapper

**5. MCP Interface Layer**
- Tool registration and routing
- Parameter validation
- Response formatting
- Error translation

### 5.3 Key Algorithms

**Algorithm 1: Temporal Reconstruction**
```python
def reconstruct_timeline(observations):
    # Build parent-child map
    tree = build_tree(observations)

    # Sort by startTime (handle nulls)
    sorted_obs = []
    for obs in observations:
        if obs.startTime:
            sorted_obs.append(obs)
        else:
            # Infer from parent or siblings
            inferred_time = infer_timestamp(obs, tree)
            obs.startTime = inferred_time
            sorted_obs.append(obs)

    sorted_obs.sort(key=lambda x: x.startTime)
    return sorted_obs
```

**Algorithm 2: Tool Call Extraction**
```python
def extract_tool_calls(observations):
    tool_calls = []

    for obs in observations:
        # Filter by type
        if obs.type != "SPAN":
            continue

        # Pattern match on name
        if not is_tool_call(obs.name, obs.metadata):
            continue

        # Extract tool data
        tool_call = {
            "id": obs.id,
            "name": extract_tool_name(obs),
            "arguments": parse_arguments(obs.input),
            "result": parse_result(obs.output),
            "timestamp": obs.startTime,
            "duration": calculate_duration(obs)
        }

        # Find parent prompt
        parent = find_parent_generation(obs, observations)
        if parent:
            tool_call["context"] = extract_prompt_context(parent)

        tool_calls.append(tool_call)

    return tool_calls
```

**Algorithm 3: Context Association**
```python
def associate_context(tool_call_obs, all_observations):
    # Strategy 1: Direct parent
    parent = find_by_id(tool_call_obs.parentObservationId, all_observations)
    if parent and parent.type == "GENERATION":
        return extract_context(parent)

    # Strategy 2: Temporal proximity
    nearby = find_observations_before(
        tool_call_obs.startTime,
        window_seconds=5,
        all_observations
    )
    for obs in nearby:
        if obs.type == "GENERATION":
            return extract_context(obs)

    # Strategy 3: Same trace root
    trace_root = find_trace_root(tool_call_obs.traceId, all_observations)
    return extract_context(trace_root)
```

---

## 6. Differentiation from Existing Servers

### 6.1 vs. avivsinai/langfuse-mcp

| Feature | avivsinai | New Server |
|---------|-----------|------------|
| **Data retrieval** | ✅ Raw API calls | ✅ Optimized queries |
| **Tool call extraction** | ❌ None | ✅ Intelligent parsing |
| **Temporal ordering** | ❌ Returns raw | ✅ Reconstructs timeline |
| **Context association** | ❌ None | ✅ Prompt linking |
| **Search** | ❌ Basic filters | ✅ Keyword search |
| **Analytics** | ❌ None | ✅ Statistics & metrics |
| **Processing** | ❌ Pass-through | ✅ Transformation |

### 6.2 vs. Prompt Management Servers

**Completely different domains**:
- Prompt servers: CRUD operations on prompts
- New server: Trace analysis and tool call extraction

**No overlap** - complementary use cases.

---

## 7. Implementation Roadmap

### Phase 1: MVP (Weeks 1-2)
- ✅ Tool 1: `extract_tool_calls_from_session`
- ✅ Tool 2: `extract_tool_calls_from_trace`
- ✅ Basic temporal reconstruction
- ✅ Tool call identification (type-based)
- ✅ Context association (parent-based)

### Phase 2: Search & Analytics (Weeks 3-4)
- ✅ Tool 3: `search_tool_calls_by_keyword`
- ✅ Tool 4: `get_tool_call_statistics`
- ✅ Advanced pattern matching
- ✅ Metrics API integration

### Phase 3: Visualization (Weeks 5-6)
- ✅ Tool 5: `reconstruct_execution_timeline`
- ✅ Graph generation (execution trees)
- ✅ Timeline visualization data
- ✅ Export formats (JSON, CSV, Mermaid)

### Phase 4: Advanced Features (Future)
- Semantic search (embedding-based)
- Anomaly detection (unusual patterns)
- Performance profiling (bottleneck identification)
- Comparative analysis (session vs session)

---

## 8. Success Criteria

### 8.1 Functional Requirements

✅ Extract tool calls from sessions with >95% accuracy
✅ Reconstruct temporal ordering for sessions with fragmented data
✅ Associate tool calls with prompts in >90% of cases
✅ Search tool calls by keyword with <2s response time
✅ Generate statistics for 1000+ tool calls in <5s

### 8.2 Quality Requirements

✅ Handle missing timestamps gracefully
✅ Support sessions with 100+ traces
✅ Cache results for repeated queries
✅ Provide clear error messages
✅ Document all tools with examples

### 8.3 Performance Requirements

✅ API calls optimized (field selection, batching)
✅ Response time <5s for typical queries
✅ Memory efficient (streaming for large datasets)
✅ Cache hit rate >70% for repeated queries

---

## 9. Conclusion

**A new Langfuse MCP server is justified and necessary** because:

1. **Existing servers are insufficient**: They provide raw API access without intelligent processing
2. **The API provides primitives**: All necessary data is available, but requires transformation
3. **The use case is distinct**: Tool call extraction with context is not addressed by any existing server
4. **Value is in processing**: Intelligence layer transforms raw data into actionable insights

**MVP focuses on core value**: Tool call scraping with context association and temporal reconstruction.

**Technical feasibility is high**: Langfuse REST API provides all required data; implementation is primarily data processing logic.

**Differentiation is clear**: No overlap with existing servers; complementary to prompt management tools.

---

## 10. Candidate Tools Summary

### MVP Tools (5)

1. **extract_tool_calls_from_session** - Session-level tool call extraction with context
2. **extract_tool_calls_from_trace** - Trace-level extraction with optional tree structure
3. **search_tool_calls_by_keyword** - Content search across tool call data
4. **get_tool_call_statistics** - Aggregated analytics on tool usage
5. **reconstruct_execution_timeline** - Time-ordered execution sequence

### Future Tools (Deferred)

6. **compare_sessions** - Side-by-side session comparison
7. **detect_tool_call_patterns** - Pattern recognition in tool usage
8. **generate_execution_graph** - Visual graph generation (Mermaid/DOT)
9. **export_tool_call_dataset** - Export for fine-tuning/training
10. **analyze_tool_performance** - Performance profiling and bottleneck detection

---

**Status**: Ready for implementation
**Next Steps**: Create detailed tool specifications and begin MVP development
