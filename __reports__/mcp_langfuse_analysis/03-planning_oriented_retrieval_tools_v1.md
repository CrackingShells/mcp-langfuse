# Planning-Oriented Retrieval Tools for Langfuse MCP Server

**Report Date**: 2025-12-03
**Report Version**: v1
**Purpose**: Define focused MCP tools for extracting and analyzing LLM planning behavior from Langfuse traces

---

## Changes from v0

### Major Additions
1. **Tool call detection flexibility**: Support both SPAN observations and metadata-based tool calls (LiteLLM pattern)
2. **ID retrieval tools**: New tools for finding session/trace IDs via timestamps and keywords
3. **LLM-assisted analysis**: Use LLM sampling for plan detection and causal relationship inference
4. **Performance optimization**: Explicit asyncio patterns with rate limiting and caching guidance
5. **Format-agnostic exports**: Abstract export formats for future extensibility

### Refinements
- Clarified parent-child vs causal terminology
- Added RPM configuration as tool parameter
- Expanded pseudo-code with concurrency patterns
- Removed specific format implementations (PDDL/GraphML) in favor of abstraction
- Added preconditions/effects extraction for action definitions

### Structural Changes
- New section on tool call detection strategies (SPAN vs metadata)
- New section on ID retrieval patterns
- Enhanced performance considerations with asyncio + rate limiting
- Simplified export format discussion

---

## Executive Summary

This report defines **11 focused MCP tools** for **planning-oriented retrieval** from Langfuse traces. The tools enable extraction, reconstruction, and analysis of LLM decision-making processes for integration with planning domain systems.

**Core Focus**:
- Extract tool calls from both SPAN observations and LLM output metadata
- Reconstruct execution timelines with dependency tracking
- Use LLM sampling for plan detection and causal analysis
- Support high-performance async I/O with rate limiting
- Provide format-agnostic exports for planning systems

**Key Design Principles**:
- Flexible tool call detection (SPAN + metadata patterns)
- Human-friendly ID retrieval (timestamps, keywords)
- LLM-assisted semantic analysis where programmatic parsing fails
- Async I/O with explicit rate limiting and caching
- Format abstraction for future extensibility

---

## 1. Context and Requirements

### 1.1 System Integration Context

The MCP server integrates into a stack that:
1. **Extracts tool usage plans** from LLM interactions
2. **Stores plans** in well-defined formats
3. **Records individual actions** in a planning domain
4. **Enables planning algorithms** to find plans independently of LLM stochasticity

### 1.2 Tool Call Detection Strategies

**Challenge**: Different Langfuse instrumentation patterns store tool calls differently.

**Pattern 1: SPAN Observations** (Standard Langfuse instrumentation)
```python
# Tool calls are separate SPAN observations
{
  "type": "SPAN",
  "name": "search_database",
  "input": {"query": "user data"},
  "output": {"results": [...]},
  "parentObservationId": "generation_123"
}
```

**Pattern 2: Metadata in GENERATION** (LiteLLM pattern)
```python
# Tool calls embedded in LLM generation metadata
{
  "type": "GENERATION",
  "output": "I'll search the database...",
  "metadata": {
    "tool_calls": [
      {
        "name": "search_database",
        "arguments": {"query": "user data"},
        "result": {"results": [...]}
      }
    ]
  }
}
```

**Solution**: Tools must support both patterns via detection strategy parameter.

### 1.3 ID Retrieval Challenge

**Problem**: Session/trace IDs are not human-friendly and difficult to retrieve manually.

**Solution**: Provide tools for ID discovery via:
- **Temporal queries**: Find sessions/traces by timestamp ranges
- **Keyword search**: Find sessions/traces by content
- **User-based queries**: Find sessions by user ID
- **Tag-based queries**: Find sessions by tags/metadata

### 1.4 Graph Representation for Planning

**Current State**: ArangoDB MCP server handles graph storage.

**Design Decision**: Focus on retrieving graph-structured data with format abstraction.

**Format Abstraction Pattern**:
```python
# Abstract export interface
class PlanningDomainExporter:
    def export(self, data, format_spec: str) -> str:
        """
        format_spec: Grammar/schema provided via MCP resources
        Returns: Formatted output validated against grammar
        """
        pass
```

**Supported Patterns**:
- Adjacency list (JSON) - Default, simple
- Grammar-based generation (PDDL, custom) - LLM-assisted with validation
- Graph formats (DOT, GraphML) - For visualization/analysis

---

## 2. Core Tool Definitions

### 2.1 ID Retrieval Tools

#### Tool 2.1.1: `find_sessions_by_timerange`

**Purpose**: Find session IDs within a time range for human-friendly access.

**MCP Tool Signature**:
```python
{
  "name": "find_sessions_by_timerange",
  "description": "Find Langfuse session IDs within a time range",
  "inputSchema": {
    "type": "object",
    "properties": {
      "from_timestamp": {"type": "string", "format": "date-time"},
      "to_timestamp": {"type": "string", "format": "date-time"},
      "user_id": {"type": "string", "description": "Optional: filter by user"},
      "environment": {"type": "string", "description": "Optional: filter by environment"},
      "limit": {"type": "integer", "default": 50},
      "rpm_limit": {"type": "integer", "default": 60, "description": "Requests per minute limit"}
    },
    "required": ["from_timestamp", "to_timestamp"]
  }
}
```


**Processing Strategy**:
```python
async def find_sessions_by_timerange(from_ts, to_ts, user_id=None, rpm_limit=60):
    # Rate limiter: rpm_limit requests per minute
    rate_limiter = AsyncRateLimiter(rpm_limit)
    
    async with rate_limiter:
        sessions = await api.get_sessions(
            fromTimestamp=from_ts,
            toTimestamp=to_ts,
            limit=100
        )
    
    # Filter by user_id if provided
    if user_id:
        sessions = [s for s in sessions if s.userId == user_id]
    
    return {
        "sessions": [
            {
                "session_id": s.id,
                "created_at": s.createdAt,
                "user_id": s.userId,
                "trace_count": len(s.traces)
            }
            for s in sessions
        ]
    }
```

**REST API Leverage**:
- `GET /api/public/sessions?fromTimestamp={ts}&toTimestamp={ts}`
- Pagination for large result sets
- Filter parameters for user_id, environment

**Output Structure**:
```json
{
  "time_range": {"from": "ISO8601", "to": "ISO8601"},
  "total_sessions": "number",
  "sessions": [
    {
      "session_id": "string",
      "created_at": "ISO8601",
      "user_id": "string",
      "trace_count": "number",
      "environment": "string"
    }
  ]
}
```

#### Tool 2.1.2: `find_traces_by_keyword`

**Purpose**: Find trace IDs by searching content (user queries, LLM outputs, tool names).

**MCP Tool Signature**:
```python
{
  "name": "find_traces_by_keyword",
  "description": "Find trace IDs by searching observation content",
  "inputSchema": {
    "type": "object",
    "properties": {
      "keyword": {"type": "string"},
      "search_in": {
        "type": "array",
        "items": {"type": "string", "enum": ["input", "output", "name", "metadata"]},
        "default": ["input", "output", "name"]
      },
      "from_timestamp": {"type": "string", "format": "date-time"},
      "to_timestamp": {"type": "string", "format": "date-time"},
      "limit": {"type": "integer", "default": 50},
      "rpm_limit": {"type": "integer", "default": 60}
    },
    "required": ["keyword"]
  }
}
```

**Processing Strategy**:
```python
async def find_traces_by_keyword(keyword, search_in, from_ts=None, to_ts=None, rpm_limit=60):
    rate_limiter = AsyncRateLimiter(rpm_limit)
    
    # Fetch observations with filters
    async with rate_limiter:
        observations = await api.get_observations(
            fromStartTime=from_ts,
            toStartTime=to_ts,
            limit=100
        )
    
    # Client-side keyword search (API doesn't support full-text search)
    matching_traces = set()
    for obs in observations:
        if keyword_matches(obs, keyword, search_in):
            matching_traces.add(obs.traceId)
    
    # Fetch trace details for matches
    traces = []
    async with rate_limiter:
        for trace_id in matching_traces:
            trace = await api.get_trace(trace_id)
            traces.append(trace)
    
    return {"traces": traces}
```

**Output Structure**:
```json
{
  "keyword": "string",
  "total_matches": "number",
  "traces": [
    {
      "trace_id": "string",
      "session_id": "string",
      "timestamp": "ISO8601",
      "name": "string",
      "match_context": "string"
    }
  ]
}
```

---

### 2.2 Tool Call Extraction Tools

#### Tool 2.2.1: `extract_tool_calls_from_session`

**Purpose**: Extract all tool calls from a session with full context, supporting both SPAN and metadata patterns.

**MCP Tool Signature**:
```python
{
  "name": "extract_tool_calls_from_session",
  "description": "Extract all tool calls from a Langfuse session",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {"type": "string"},
      "detection_strategy": {
        "type": "string",
        "enum": ["auto", "span_only", "metadata_only"],
        "default": "auto",
        "description": "How to detect tool calls"
      },
      "include_context": {"type": "boolean", "default": true},
      "include_results": {"type": "boolean", "default": true},
      "filter_by_status": {"type": "string", "enum": ["all", "success", "failure"], "default": "all"},
      "rpm_limit": {"type": "integer", "default": 60}
    },
    "required": ["session_id"]
  }
}
```


**Processing Strategy with Async + Rate Limiting**:
```python
async def extract_tool_calls_from_session(session_id, detection_strategy="auto", rpm_limit=60):
    rate_limiter = AsyncRateLimiter(rpm_limit)
    cache = LRUCache(maxsize=1000)
    
    # Step 1: Fetch all traces for session (lightweight)
    async with rate_limiter:
        traces = await api.get_traces(sessionId=session_id, fields="core")
    
    # Step 2: Batch fetch observations with concurrency control
    semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests
    
    async def fetch_observations_with_limit(trace_id):
        async with semaphore, rate_limiter:
            # Check cache first
            if cached := cache.get(trace_id):
                return cached
            
            obs = await api.get_observations(traceId=trace_id)
            cache.set(trace_id, obs)
            return obs
    
    # Parallel fetch all observations
    all_observations = await asyncio.gather(*[
        fetch_observations_with_limit(t.id) for t in traces
    ])
    
    # Step 3: Extract tool calls based on strategy
    tool_calls = []
    for observations in all_observations:
        if detection_strategy in ["auto", "span_only"]:
            tool_calls.extend(extract_from_spans(observations))
        
        if detection_strategy in ["auto", "metadata_only"]:
            tool_calls.extend(extract_from_metadata(observations))
    
    return {"tool_calls": tool_calls}

def extract_from_spans(observations):
    """Extract tool calls from SPAN observations"""
    tool_calls = []
    obs_map = {o.id: o for o in observations}
    
    for obs in observations:
        if obs.type != "SPAN":
            continue
        
        # Find parent GENERATION for context
        parent = obs_map.get(obs.parentObservationId)
        
        tool_calls.append({
            "id": obs.id,
            "tool_name": obs.name,
            "arguments": parse_input(obs.input),
            "result": parse_output(obs.output),
            "timestamp": obs.startTime,
            "duration_seconds": (obs.endTime - obs.startTime).total_seconds(),
            "context": parent.output if parent and parent.type == "GENERATION" else None
        })
    
    return tool_calls

def extract_from_metadata(observations):
    """Extract tool calls from GENERATION metadata (LiteLLM pattern)"""
    tool_calls = []
    
    for obs in observations:
        if obs.type != "GENERATION":
            continue
        
        # Check for tool_calls in metadata
        if tool_calls_meta := obs.metadata.get("tool_calls"):
            for tc in tool_calls_meta:
                tool_calls.append({
                    "id": f"{obs.id}_tool_{tc['name']}",
                    "tool_name": tc["name"],
                    "arguments": tc.get("arguments", {}),
                    "result": tc.get("result", {}),
                    "timestamp": obs.startTime,
                    "context": obs.output
                })
    
    return tool_calls
```

**REST API Leverage**:
- `GET /api/public/traces?sessionId={id}&fields=core` - Lightweight trace list
- `GET /api/public/observations?traceId={id}` - Batch fetch with asyncio.gather
- Rate limiting via semaphore + custom rate limiter
- Caching to avoid redundant API calls

**Output Structure**:
```json
{
  "session_id": "string",
  "total_tool_calls": "number",
  "traces_analyzed": "number",
  "detection_strategy_used": "auto|span_only|metadata_only",
  "tool_calls": [
    {
      "id": "string",
      "trace_id": "string",
      "timestamp": "ISO8601",
      "tool_name": "string",
      "arguments": {},
      "result": {},
      "status": "success|failure",
      "duration_seconds": "number",
      "context": {
        "preceding_llm_output": "string",
        "llm_observation_id": "string"
      }
    }
  ]
}
```

#### Tool 2.2.2: `extract_tool_calls_from_trace`

**Purpose**: Extract tool calls from a single trace (finer granularity).

**MCP Tool Signature**: Similar to `extract_tool_calls_from_session` but with `trace_id` parameter.

**Processing Strategy**: Same as session-level but scoped to single trace (simpler, no batch fetching needed).

---

### 2.3 Temporal Reconstruction Tools

#### Tool 2.3.1: `reconstruct_execution_timeline`

**Purpose**: Reconstruct temporal execution order with parallelism detection.

**MCP Tool Signature**:
```python
{
  "name": "reconstruct_execution_timeline",
  "description": "Reconstruct temporal execution timeline from observations",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {"type": "string"},
      "trace_id": {"type": "string"},
      "include_llm_reasoning": {"type": "boolean", "default": true},
      "include_parallel_detection": {"type": "boolean", "default": true},
      "output_format": {
        "type": "string",
        "enum": ["timeline", "graph"],
        "default": "timeline"
      },
      "rpm_limit": {"type": "integer", "default": 60}
    },
    "oneOf": [
      {"required": ["session_id"]},
      {"required": ["trace_id"]}
    ]
  }
}
```


**Processing Strategy**:
```python
async def reconstruct_timeline(scope_id, scope_type, rpm_limit=60):
    rate_limiter = AsyncRateLimiter(rpm_limit)
    
    # Fetch all observations
    async with rate_limiter:
        if scope_type == "session":
            traces = await api.get_traces(sessionId=scope_id)
            observations = []
            for trace in traces:
                obs = await api.get_observations(traceId=trace.id)
                observations.extend(obs)
        else:
            observations = await api.get_observations(traceId=scope_id)
    
    # Sort by timestamp
    sorted_obs = sorted(observations, key=lambda o: o.startTime)
    
    # Build parent-child map
    children_map = defaultdict(list)
    for obs in observations:
        if obs.parentObservationId:
            children_map[obs.parentObservationId].append(obs)
    
    # Detect parallel executions
    parallel_groups = detect_parallel_executions(sorted_obs)
    
    # Build timeline
    timeline = []
    for i, obs in enumerate(sorted_obs):
        timeline.append({
            "sequence_number": i + 1,
            "observation_id": obs.id,
            "type": obs.type,
            "name": obs.name,
            "start_time": obs.startTime,
            "end_time": obs.endTime,
            "duration_seconds": (obs.endTime - obs.startTime).total_seconds(),
            "parent_id": obs.parentObservationId,
            "depth": calculate_depth(obs, children_map),
            "parallel_group_id": find_parallel_group(obs, parallel_groups)
        })
    
    return {"timeline": timeline, "parallel_groups": parallel_groups}

def detect_parallel_executions(observations):
    """Detect observations that executed in parallel"""
    parallel_groups = []
    
    for i, obs1 in enumerate(observations):
        parallel = [obs1]
        for obs2 in observations[i+1:]:
            # Check time overlap
            if (obs1.startTime < obs2.endTime and 
                obs2.startTime < obs1.endTime):
                # Ensure not parent-child
                if not is_ancestor(obs1, obs2):
                    parallel.append(obs2)
        
        if len(parallel) > 1:
            parallel_groups.append({
                "group_id": f"parallel_{i}",
                "observations": [o.id for o in parallel],
                "time_range": {
                    "start": min(o.startTime for o in parallel),
                    "end": max(o.endTime for o in parallel)
                }
            })
    
    return parallel_groups
```

**Output Structure (Timeline Format)**:
```json
{
  "scope": {"type": "session|trace", "id": "string"},
  "total_duration_seconds": "number",
  "timeline": [
    {
      "sequence_number": "number",
      "observation_id": "string",
      "type": "SPAN|GENERATION|EVENT",
      "name": "string",
      "start_time": "ISO8601",
      "end_time": "ISO8601",
      "duration_seconds": "number",
      "parent_id": "string|null",
      "depth": "number",
      "parallel_group_id": "string|null"
    }
  ],
  "parallel_executions": [
    {
      "group_id": "string",
      "observations": ["observation_id"],
      "time_range": {"start": "ISO8601", "end": "ISO8601"}
    }
  ]
}
```

**Output Structure (Graph Format)**:
```json
{
  "nodes": [
    {
      "id": "observation_id",
      "type": "SPAN|GENERATION|EVENT",
      "label": "string",
      "start_time": "ISO8601",
      "duration": "number"
    }
  ],
  "edges": [
    {
      "from": "observation_id",
      "to": "observation_id",
      "type": "parent_child|temporal_sequence|parallel"
    }
  ]
}
```

---

### 2.4 Search and Statistics Tools

#### Tool 2.4.1: `search_tool_calls_by_keyword`

**Purpose**: Search tool calls by content for pattern discovery.

**MCP Tool Signature**:
```python
{
  "name": "search_tool_calls_by_keyword",
  "description": "Search tool calls by keyword in arguments, results, or context",
  "inputSchema": {
    "type": "object",
    "properties": {
      "keyword": {"type": "string"},
      "search_in": {
        "type": "array",
        "items": {"type": "string", "enum": ["arguments", "results", "context", "tool_name"]},
        "default": ["arguments", "results", "context"]
      },
      "session_id": {"type": "string"},
      "from_timestamp": {"type": "string", "format": "date-time"},
      "to_timestamp": {"type": "string", "format": "date-time"},
      "limit": {"type": "integer", "default": 100},
      "rpm_limit": {"type": "integer", "default": 60}
    },
    "required": ["keyword"]
  }
}
```

**Processing Strategy**: Similar to `extract_tool_calls_from_session` but with keyword filtering.

#### Tool 2.4.2: `get_tool_call_statistics`

**Purpose**: Aggregate statistics on tool usage patterns.

**MCP Tool Signature**:
```python
{
  "name": "get_tool_call_statistics",
  "description": "Get aggregated statistics on tool usage patterns",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {"type": "string"},
      "from_timestamp": {"type": "string", "format": "date-time"},
      "to_timestamp": {"type": "string", "format": "date-time"},
      "group_by": {
        "type": "string",
        "enum": ["tool", "session", "trace", "time_bucket"],
        "default": "tool"
      },
      "time_bucket": {"type": "string", "enum": ["hour", "day", "week"], "default": "day"},
      "rpm_limit": {"type": "integer", "default": 60}
    }
  }
}
```


**Processing Strategy with Metrics API**:
```python
async def get_tool_call_statistics(from_ts, to_ts, group_by="tool", rpm_limit=60):
    rate_limiter = AsyncRateLimiter(rpm_limit)
    
    # Use Metrics API for aggregation
    metrics_query = {
        "select": [
            {"column": "name", "agg": None},
            {"column": "latency", "agg": "avg"},
            {"column": "totalCost", "agg": "sum"},
            {"column": "id", "agg": "count"}
        ],
        "filters": [
            {"column": "type", "operator": "=", "value": "SPAN", "type": "string"}
        ],
        "groupBy": [{"column": "name", "type": "string"}],
        "fromTimestamp": from_ts,
        "toTimestamp": to_ts
    }
    
    async with rate_limiter:
        result = await api.post_metrics(query=metrics_query)
    
    # Process results
    statistics = []
    for row in result.data:
        statistics.append({
            "tool_name": row["name"],
            "call_count": row["count"],
            "avg_duration_seconds": row["avg_latency"],
            "total_cost_usd": row["sum_totalCost"]
        })
    
    return {"statistics_by_tool": statistics}
```

**Output Structure**:
```json
{
  "time_range": {"from": "ISO8601", "to": "ISO8601"},
  "total_tool_calls": "number",
  "statistics_by_tool": [
    {
      "tool_name": "string",
      "call_count": "number",
      "success_rate": "number",
      "avg_duration_seconds": "number",
      "p50_duration": "number",
      "p95_duration": "number",
      "total_cost_usd": "number"
    }
  ]
}
```

---

### 2.5 LLM-Assisted Plan Extraction Tools

#### Tool 2.5.1: `extract_llm_plans`

**Purpose**: Extract LLM-decided action plans using LLM sampling for semantic analysis.

**MCP Tool Signature**:
```python
{
  "name": "extract_llm_plans",
  "description": "Extract LLM planning decisions using LLM-assisted analysis",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {"type": "string"},
      "trace_id": {"type": "string"},
      "use_llm_sampling": {"type": "boolean", "default": true},
      "include_execution_matching": {"type": "boolean", "default": true},
      "include_deviation_analysis": {"type": "boolean", "default": true},
      "rpm_limit": {"type": "integer", "default": 60}
    },
    "oneOf": [
      {"required": ["session_id"]},
      {"required": ["trace_id"]}
    ]
  }
}
```

**Processing Strategy with LLM Sampling**:
```python
async def extract_llm_plans(scope_id, scope_type, use_llm_sampling=True, rpm_limit=60):
    rate_limiter = AsyncRateLimiter(rpm_limit)
    
    # Step 1: Fetch observations
    async with rate_limiter:
        observations = await fetch_observations_for_scope(scope_id, scope_type)
    
    # Step 2: Identify potential planning observations (GENERATION type)
    generation_obs = [o for o in observations if o.type == "GENERATION"]
    
    plans = []
    
    if use_llm_sampling:
        # Use LLM to analyze each generation for planning content
        for obs in generation_obs:
            plan_analysis = await analyze_with_llm(
                observation=obs,
                prompt="""
                Analyze this LLM output and determine:
                1. Does it contain a plan or action sequence? (yes/no)
                2. If yes, extract the planned actions with:
                   - Action name/tool
                   - Arguments
                   - Rationale
                
                Output JSON format:
                {
                  "is_plan": boolean,
                  "planned_actions": [
                    {"action": "string", "tool": "string", "arguments": {}, "rationale": "string"}
                  ]
                }
                """,
                context={"preceding_observations": get_context(obs, observations)}
            )
            
            if plan_analysis["is_plan"]:
                plans.append({
                    "observation_id": obs.id,
                    "timestamp": obs.startTime,
                    "planned_actions": plan_analysis["planned_actions"],
                    "detection_method": "llm_sampling"
                })
    else:
        # Fallback: Simple heuristics (less reliable)
        for obs in generation_obs:
            if contains_action_keywords(obs.output):
                plans.append(extract_plan_heuristic(obs))
    
    # Step 3: Match plans to executions
    if include_execution_matching:
        for plan in plans:
            plan["execution_matching"] = await match_plan_to_executions(
                plan, observations, rate_limiter
            )
    
    return {"plans": plans}

async def analyze_with_llm(observation, prompt, context):
    """Use LLM sampling to analyze observation content"""
    # Construct analysis prompt with observation content
    full_prompt = f"{prompt}\n\nObservation Output:\n{observation.output}"
    
    if context:
        full_prompt += f"\n\nContext:\n{json.dumps(context)}"
    
    # Call LLM (via MCP or direct API)
    response = await llm_client.generate(
        prompt=full_prompt,
        temperature=0.1,  # Low temperature for consistent analysis
        response_format="json"
    )
    
    return json.loads(response)
```

**Output Structure**:
```json
{
  "scope": {"type": "session|trace", "id": "string"},
  "plans_detected": "number",
  "plans": [
    {
      "plan_id": "string",
      "observation_id": "string",
      "timestamp": "ISO8601",
      "detection_method": "llm_sampling|heuristic",
      "planned_actions": [
        {
          "sequence": "number",
          "action_type": "tool_call|api_request|computation",
          "tool_name": "string",
          "arguments": {},
          "rationale": "string"
        }
      ],
      "execution_matching": {
        "matched_actions": [
          {
            "planned_sequence": "number",
            "executed_observation_id": "string",
            "execution_sequence": "number",
            "time_to_execution_seconds": "number",
            "status": "success|failure"
          }
        ],
        "unmatched_planned": [],
        "unplanned_executions": []
      }
    }
  ]
}
```

---

### 2.6 Action Dependency Extraction Tools

#### Tool 2.6.1: `extract_action_dependencies`

**Purpose**: Extract dependency relationships between actions for planning domain modeling.

**MCP Tool Signature**:
```python
{
  "name": "extract_action_dependencies",
  "description": "Extract action dependencies and preconditions from execution traces",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {"type": "string"},
      "trace_id": {"type": "string"},
      "dependency_types": {
        "type": "array",
        "items": {"type": "string", "enum": ["temporal", "data_flow", "parent_child", "causal"]},
        "default": ["temporal", "data_flow", "parent_child"]
      },
      "use_llm_for_causal": {"type": "boolean", "default": true},
      "output_format": {"type": "string", "enum": ["graph", "json"], "default": "graph"},
      "rpm_limit": {"type": "integer", "default": 60}
    },
    "oneOf": [
      {"required": ["session_id"]},
      {"required": ["trace_id"]}
    ]
  }
}
```


**Processing Strategy with LLM-Assisted Causal Analysis**:
```python
async def extract_dependencies(scope_id, scope_type, dependency_types, use_llm_for_causal=True, rpm_limit=60):
    rate_limiter = AsyncRateLimiter(rpm_limit)
    
    # Fetch observations
    async with rate_limiter:
        observations = await fetch_observations_for_scope(scope_id, scope_type)
    
    dependencies = []
    
    # 1. Temporal dependencies (programmatic)
    if "temporal" in dependency_types:
        dependencies.extend(extract_temporal_deps(observations))
    
    # 2. Data flow dependencies (programmatic)
    if "data_flow" in dependency_types:
        dependencies.extend(extract_data_flow_deps(observations))
    
    # 3. Parent-child dependencies (from API structure)
    if "parent_child" in dependency_types:
        dependencies.extend(extract_parent_child_deps(observations))
    
    # 4. Causal dependencies (LLM-assisted)
    if "causal" in dependency_types and use_llm_for_causal:
        dependencies.extend(await extract_causal_deps_llm(observations, rate_limiter))
    
    # Extract preconditions and effects
    actions = await extract_action_definitions(observations, dependencies, rate_limiter)
    
    return {
        "nodes": actions,
        "edges": dependencies
    }

def extract_temporal_deps(observations):
    """Extract temporal ordering dependencies"""
    deps = []
    sorted_obs = sorted(observations, key=lambda o: o.startTime)
    
    for i, obs_a in enumerate(sorted_obs):
        for obs_b in sorted_obs[i+1:]:
            if obs_a.endTime <= obs_b.startTime:
                deps.append({
                    "from": obs_a.id,
                    "to": obs_b.id,
                    "type": "temporal",
                    "strength": 1.0
                })
                break  # Only immediate successor
    
    return deps

def extract_data_flow_deps(observations):
    """Detect data flow: output of A used as input to B"""
    deps = []
    
    for obs_a in observations:
        output_data = extract_output_values(obs_a.output)
        
        for obs_b in observations:
            if obs_b.startTime > obs_a.endTime:
                input_data = extract_input_values(obs_b.input)
                
                # Check if output values appear in input
                if data_overlap(output_data, input_data):
                    deps.append({
                        "from": obs_a.id,
                        "to": obs_b.id,
                        "type": "data_flow",
                        "strength": calculate_overlap_strength(output_data, input_data)
                    })
    
    return deps

def extract_parent_child_deps(observations):
    """Extract parent-child relationships from API structure"""
    deps = []
    
    for obs in observations:
        if obs.parentObservationId:
            deps.append({
                "from": obs.parentObservationId,
                "to": obs.id,
                "type": "parent_child",
                "strength": 1.0
            })
    
    return deps

async def extract_causal_deps_llm(observations, rate_limiter):
    """Use LLM to infer causal relationships"""
    deps = []
    
    # Analyze pairs of observations for causality
    for i, obs_a in enumerate(observations):
        for obs_b in observations[i+1:]:
            # Only analyze temporally ordered pairs
            if obs_a.endTime > obs_b.startTime:
                continue
            
            # Use LLM to determine causality
            async with rate_limiter:
                causal_analysis = await analyze_with_llm(
                    observation=None,
                    prompt=f"""
                    Analyze if Action A caused or triggered Action B:
                    
                    Action A: {obs_a.name}
                    - Input: {obs_a.input}
                    - Output: {obs_a.output}
                    - Time: {obs_a.startTime}
                    
                    Action B: {obs_b.name}
                    - Input: {obs_b.input}
                    - Output: {obs_b.output}
                    - Time: {obs_b.startTime}
                    
                    Determine:
                    1. Is there a causal relationship? (yes/no)
                    2. Confidence level (0.0-1.0)
                    3. Explanation
                    
                    Output JSON:
                    {{"is_causal": boolean, "confidence": float, "explanation": "string"}}
                    """,
                    context={}
                )
            
            if causal_analysis["is_causal"] and causal_analysis["confidence"] > 0.7:
                deps.append({
                    "from": obs_a.id,
                    "to": obs_b.id,
                    "type": "causal",
                    "strength": causal_analysis["confidence"],
                    "explanation": causal_analysis["explanation"]
                })
    
    return deps

async def extract_action_definitions(observations, dependencies, rate_limiter):
    """Extract action definitions with preconditions and effects"""
    actions = []
    
    for obs in observations:
        if obs.type != "SPAN":
            continue
        
        # Use LLM to infer preconditions and effects
        async with rate_limiter:
            action_def = await analyze_with_llm(
                observation=obs,
                prompt=f"""
                Analyze this action and extract:
                1. Preconditions (what must be true before execution)
                2. Effects (what changes after execution)
                
                Action: {obs.name}
                Input: {obs.input}
                Output: {obs.output}
                
                Output JSON:
                {{
                  "preconditions": ["condition1", "condition2"],
                  "effects": ["effect1", "effect2"]
                }}
                """,
                context={"dependencies": get_related_deps(obs.id, dependencies)}
            )
        
        actions.append({
            "id": obs.id,
            "action": obs.name,
            "type": obs.type,
            "preconditions": action_def["preconditions"],
            "effects": action_def["effects"],
            "duration": (obs.endTime - obs.startTime).total_seconds()
        })
    
    return actions
```

**Output Structure (Graph Format)**:
```json
{
  "nodes": [
    {
      "id": "observation_id",
      "action": "string",
      "type": "SPAN|GENERATION",
      "preconditions": ["condition"],
      "effects": ["effect"],
      "duration": "number"
    }
  ],
  "edges": [
    {
      "from": "observation_id",
      "to": "observation_id",
      "type": "temporal|data_flow|parent_child|causal",
      "strength": "number (0-1)",
      "explanation": "string (for causal)"
    }
  ]
}
```

---

### 2.7 Planning Domain Export Tools

#### Tool 2.7.1: `export_planning_domain`

**Purpose**: Export extracted plans and actions in planning domain format with grammar-based generation.

**MCP Tool Signature**:
```python
{
  "name": "export_planning_domain",
  "description": "Export plans and actions in planning domain format",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_ids": {"type": "array", "items": {"type": "string"}},
      "from_timestamp": {"type": "string", "format": "date-time"},
      "to_timestamp": {"type": "string", "format": "date-time"},
      "format_grammar": {
        "type": "string",
        "description": "Grammar specification for output format (provided via MCP resources)"
      },
      "use_llm_generation": {"type": "boolean", "default": true},
      "validate_output": {"type": "boolean", "default": true},
      "include_metadata": {"type": "boolean", "default": true},
      "rpm_limit": {"type": "integer", "default": 60}
    }
  }
}
```


**Processing Stra
tegy with Grammar-Based Generation**:
```python
async def export_planning_domain(session_ids, format_grammar, use_llm_generation=True, rpm_limit=60):
    rate_limiter = AsyncRateLimiter(rpm_limit)
    
    # Step 1: Extract all plans and actions from sessions
    all_plans = []
    all_actions = []
    
    for session_id in session_ids:
        async with rate_limiter:
            plans = await extract_llm_plans(session_id, "session")
            actions = await extract_action_dependencies(session_id, "session")
        
        all_plans.extend(plans["plans"])
        all_actions.extend(actions["nodes"])
    
    # Step 2: Build unified action library
    action_library = deduplicate_actions(all_actions)
    
    # Step 3: Generate output using grammar
    if use_llm_generation:
        # Use LLM to generate format-compliant output
        async with rate_limiter:
            formatted_output = await generate_with_grammar(
                data={
                    "actions": action_library,
                    "plans": all_plans
                },
                grammar=format_grammar,
                llm_client=llm_client
            )
    else:
        # Fallback: JSON format
        formatted_output = json.dumps({
            "domain": {"actions": action_library},
            "problems": all_plans
        })
    
    # Step 4: Validate output against grammar
    if validate_output:
        validation_result = validate_against_grammar(formatted_output, format_grammar)
        if not validation_result.valid:
            raise ValueError(f"Output validation failed: {validation_result.errors}")
    
    return {
        "format": format_grammar,
        "output": formatted_output,
        "metadata": {
            "total_sessions": len(session_ids),
            "total_actions": len(action_library),
            "total_plans": len(all_plans)
        }
    }

async def generate_with_grammar(data, grammar, llm_client):
    """Use LLM to generate format-compliant output"""
    prompt = f"""
    Generate a planning domain specification following this grammar:
    
    {grammar}
    
    Using this extracted data:
    {json.dumps(data, indent=2)}
    
    Generate valid output that conforms to the grammar.
    """
    
    response = await llm_client.generate(
        prompt=prompt,
        temperature=0.1,
        max_tokens=4000
    )
    
    return response
```

**Output Structure**:
```json
{
  "format": "string (grammar name)",
  "output": "string (formatted according to grammar)",
  "metadata": {
    "extraction_timestamp": "ISO8601",
    "source_sessions": ["session_id"],
    "total_plans": "number",
    "total_actions": "number",
    "validation_status": "valid|invalid"
  }
}
```

**Example Grammar (PDDL)**:
```
(define (domain extracted_domain)
  (:requirements :strips :typing)
  (:types action)
  (:predicates
    (completed ?a - action)
    (precedes ?a1 ?a2 - action))
  (:action {action_name}
    :parameters (?tool - action)
    :precondition (and {preconditions})
    :effect (and {effects})))
```

---

### 2.8 Pattern Analysis Tools

#### Tool 2.8.1: `analyze_plan_success_patterns`

**Purpose**: Identify patterns in successful vs failed plan executions.

**MCP Tool Signature**:
```python
{
  "name": "analyze_plan_success_patterns",
  "description": "Analyze patterns in successful vs failed plan executions",
  "inputSchema": {
    "type": "object",
    "properties": {
      "from_timestamp": {"type": "string", "format": "date-time"},
      "to_timestamp": {"type": "string", "format": "date-time"},
      "min_plan_occurrences": {"type": "integer", "default": 3},
      "include_failure_analysis": {"type": "boolean", "default": true},
      "use_llm_clustering": {"type": "boolean", "default": true},
      "rpm_limit": {"type": "integer", "default": 60}
    },
    "required": ["from_timestamp", "to_timestamp"]
  }
}
```

**Processing Strategy**:
```python
async def analyze_plan_success_patterns(from_ts, to_ts, use_llm_clustering=True, rpm_limit=60):
    rate_limiter = AsyncRateLimiter(rpm_limit)
    
    # Step 1: Find all sessions in time range
    async with rate_limiter:
        sessions = await api.get_sessions(fromTimestamp=from_ts, toTimestamp=to_ts)
    
    # Step 2: Extract plans from all sessions
    all_plans = []
    for session in sessions:
        async with rate_limiter:
            plans = await extract_llm_plans(session.id, "session")
        all_plans.extend(plans["plans"])
    
    # Step 3: Cluster similar plans
    if use_llm_clustering:
        plan_clusters = await cluster_plans_with_llm(all_plans, rate_limiter)
    else:
        plan_clusters = cluster_plans_heuristic(all_plans)
    
    # Step 4: Analyze success rates per cluster
    pattern_analysis = []
    for cluster in plan_clusters:
        success_count = sum(1 for p in cluster["plans"] if p["success"])
        failure_count = len(cluster["plans"]) - success_count
        
        pattern_analysis.append({
            "pattern_id": cluster["id"],
            "tool_sequence": cluster["tool_sequence"],
            "occurrences": len(cluster["plans"]),
            "success_rate": success_count / len(cluster["plans"]),
            "success_factors": await analyze_success_factors(cluster, rate_limiter),
            "failure_points": await analyze_failure_points(cluster, rate_limiter)
        })
    
    return {"plan_patterns": pattern_analysis}

async def cluster_plans_with_llm(plans, rate_limiter):
    """Use LLM to cluster similar plans"""
    async with rate_limiter:
        clustering_result = await analyze_with_llm(
            observation=None,
            prompt=f"""
            Cluster these plans by similarity:
            
            {json.dumps([p["planned_actions"] for p in plans], indent=2)}
            
            Group plans that have similar:
            - Tool sequences
            - Goals/objectives
            - Execution patterns
            
            Output JSON:
            {{
              "clusters": [
                {{
                  "id": "string",
                  "tool_sequence": ["tool1", "tool2"],
                  "plan_indices": [0, 3, 7]
                }}
              ]
            }}
            """,
            context={}
        )
    
    # Map clusters back to plans
    clusters = []
    for cluster in clustering_result["clusters"]:
        clusters.append({
            "id": cluster["id"],
            "tool_sequence": cluster["tool_sequence"],
            "plans": [plans[i] for i in cluster["plan_indices"]]
        })
    
    return clusters
```

**Output Structure**:
```json
{
  "time_range": {"from": "ISO8601", "to": "ISO8601"},
  "total_plans_analyzed": "number",
  "plan_patterns": [
    {
      "pattern_id": "string",
      "tool_sequence": ["tool1", "tool2", "tool3"],
      "occurrences": "number",
      "success_rate": "number",
      "avg_execution_time": "number",
      "success_factors": ["factor"],
      "failure_points": [
        {
          "step": "number",
          "tool": "string",
          "failure_rate": "number",
          "common_errors": ["error_message"]
        }
      ]
    }
  ],
  "recommendations": [
    {
      "pattern_id": "string",
      "recommendation": "string",
      "expected_improvement": "string",
      "priority": "high|medium|low"
    }
  ]
}
```

---

## 3. Common Processing Patterns

### 3.1 Async Rate Limiting

All tools must implement rate limiting to respect API limits:

```python
class AsyncRateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, rpm: int):
        self.rpm = rpm
        self.interval = 60.0 / rpm  # Seconds between requests
        self.last_request = 0
    
    async def __aenter__(self):
        now = time.time()
        time_since_last = now - self.last_request
        
        if time_since_last < self.interval:
            await asyncio.sleep(self.interval - time_since_last)
        
        self.last_request = time.time()
    
    async def __aexit__(self, *args):
        pass
```

### 3.2 LRU Caching

Implement caching to avoid redundant API calls:

```python
from functools import lru_cache

class LRUCache:
    def __init__(self, maxsize=1000):
        self.cache = {}
        self.maxsize = maxsize
        self.access_order = []
    
    def get(self, key):
        if key in self.cache:
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key, value):
        if key in self.cache:
            self.access_order.remove(key)
        elif len(self.cache) >= self.maxsize:
            # Evict least recently used
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]
        
        self.cache[key] = value
        self.access_order.append(key)
```

### 3.3 Observation Tree Building

Common pattern for reconstructing hierarchical structure:

```python
def build_observation_tree(observations: List[Observation]):
    """Build tree structure from flat observation list"""
    obs_map = {o.id: o for o in observations}
    children = defaultdict(list)
    roots = []
    
    for obs in observations:
        if obs.parentObservationId:
            children[obs.parentObservationId].append(obs)
        else:
            roots.append(obs)
    
    # Attach children to each observation
    for obs in observations:
        obs.children = children.get(obs.id, [])
    
    return roots
```

### 3.4 Batch Processing with Concurrency Control

Process multiple items with controlled concurrency:

```python
async def batch_process(items, process_fn, max_concurrent=10, rpm_limit=60):
    """Process items in batches with concurrency control"""
    semaphore = asyncio.Semaphore(max_concurrent)
    rate_limiter = AsyncRateLimiter(rpm_limit)
    
    async def process_with_limits(item):
        async with semaphore, rate_limiter:
            return await process_fn(item)
    
    results = await asyncio.gather(*[
        process_with_limits(item) for item in items
    ])
    
    return results
```

---

## 4. REST API Usage Patterns

### 4.1 Efficient Filtering

Use API filters to reduce data transfer:

```python
# Good: Filter at API level
observations = await api.get_observations(
    traceId=trace_id,
    type="SPAN",  # Only tool executions
    fromStartTime=start_time,
    toStartTime=end_time,
    fields="core,io"  # Only needed fields
)

# Bad: Fetch everything and filter client-side
all_observations = await api.get_observations(traceId=trace_id)
filtered = [o for o in all_observations if o.type == "SPAN"]
```

### 4.2 Pagination Handling

Handle large result sets with pagination:

```python
async def fetch_all_paginated(fetch_fn, **kwargs):
    """Fetch all pages of a paginated endpoint"""
    all_items = []
    page = 1
    
    while True:
        response = await fetch_fn(page=page, limit=100, **kwargs)
        all_items.extend(response.data)
        
        if len(response.data) < 100:  # Last page
            break
        
        page += 1
    
    return all_items
```

### 4.3 Metrics API for Aggregation

Use Metrics API for heavy aggregations:

```python
async def get_aggregated_metrics(from_ts, to_ts):
    """Use Metrics API for efficient aggregation"""
    metrics_query = {
        "select": [
            {"column": "name", "agg": None},
            {"column": "latency", "agg": "avg"},
            {"column": "totalCost", "agg": "sum"},
            {"column": "id", "agg": "count"}
        ],
        "filters": [
            {"column": "type", "operator": "=", "value": "SPAN", "type": "string"}
        ],
        "groupBy": [{"column": "name", "type": "string"}],
        "fromTimestamp": from_ts,
        "toTimestamp": to_ts
    }
    
    result = await api.post_metrics(query=metrics_query)
    return result.data
```

---

## 5. Tool Priority and Implementation Order

### Phase 1: Core Infrastructure (Week 1)
- Async API client with rate limiting
- LRU caching implementation
- Observation tree builder
- LLM sampling integration

### Phase 2: ID Retrieval and Basic Extraction (Week 2)
1. `find_sessions_by_timerange` - Human-friendly session discovery
2. `find_traces_by_keyword` - Content-based trace discovery
3. `extract_tool_calls_from_trace` - Single trace extraction
4. `extract_tool_calls_from_session` - Session-level extraction

### Phase 3: Timeline and Search (Week 3)
5. `reconstruct_execution_timeline` - Temporal ordering
6. `search_tool_calls_by_keyword` - Content search
7. `get_tool_call_statistics` - Usage analytics

### Phase 4: Planning Analysis (Week 4-5)
8. `extract_llm_plans` - Plan detection with LLM sampling
9. `extract_action_dependencies` - Dependency extraction with causal analysis

### Phase 5: Advanced Features (Week 6)
10. `analyze_plan_success_patterns` - Pattern analysis
11. `export_planning_domain` - Grammar-based export

---

## 6. Integration Considerations

### 6.1 LLM Sampling Integration

**Options**:
1. **MCP Sampling** - Use MCP's built-in sampling capability
2. **Direct API** - Call LLM API directly (OpenAI, Anthropic, etc.)
3. **Local Model** - Use local model for privacy/cost

**Recommendation**: Start with MCP sampling for consistency with MCP ecosystem.

### 6.2 Planning Domain Integration

**Output Compatibility**:
- **PDDL planners**: Fast Downward, FF, LAMA
- **Graph databases**: ArangoDB (via existing MCP server)
- **Custom systems**: JSON/adjacency list format

**Integration Pattern**:
```python
# Extract from Langfuse
plans = await langfuse_mcp.extract_llm_plans(session_id)

# Store in ArangoDB
await arangodb_mcp.store_graph(
    nodes=plans["nodes"],
    edges=plans["edges"]
)

# Export to PDDL
pddl_output = await langfuse_mcp.export_planning_domain(
    session_ids=[session_id],
    format_grammar="pddl"
)
```

### 6.3 Error Handling

Robust error handling for production:

```python
async def safe_api_call(api_fn, *args, max_retries=3, **kwargs):
    """API call with retry logic"""
    for attempt in range(max_retries):
        try:
            return await api_fn(*args, **kwargs)
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            await asyncio.sleep(wait_time)
        except APIError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
    
    raise Exception(f"Failed after {max_retries} attempts")
```

---

## 7. Performance Considerations

### 7.1 Expected Latencies

**Single Trace Operations** (10-100 observations):
- Tool call extraction: 0.5-2 seconds
- Timeline reconstruction: 0.3-1 second
- Plan extraction (with LLM): 2-5 seconds

**Session Operations** (10-50 traces):
- Tool call extraction: 5-20 seconds
- Timeline reconstruction: 3-10 seconds
- Plan extraction (with LLM): 20-60 seconds

**Multi-Session Operations** (10+ sessions):
- Pattern analysis: 60-300 seconds
- Domain export: 30-120 seconds

### 7.2 Optimization Strategies

**Caching**:
- Cache raw API responses (1 hour TTL)
- Cache processed structures (6 hour TTL)
- Cache LLM analysis results (24 hour TTL)

**Parallelization**:
- Fetch traces in parallel (10 concurrent)
- Process observations in parallel
- Batch LLM calls when possible

**Rate Limiting**:
- Default: 60 RPM (1 request/second)
- Configurable per tool call
- Respect API rate limits

---

## 8. Next Steps

### 8.1 Validation Requirements

Before implementation:
1. **Stakeholder review** of tool definitions and priorities
2. **API capability verification** - Test all required endpoints
3. **LLM sampling validation** - Verify MCP sampling works for analysis
4. **Performance benchmarking** - Test with real Langfuse data

### 8.2 Implementation Preparation

1. **Test data preparation** - Create sample traces with known plans
2. **API client setup** - Async HTTP client with auth
3. **Schema definitions** - Pydantic models for all structures
4. **LLM integration** - Set up MCP sampling or direct API
5. **Unit test framework** - Test individual functions

### 8.3 Documentation Needs

1. **Tool usage examples** - Real-world scenarios
2. **API integration guide** - How to call from planning systems
3. **Performance tuning guide** - Optimization strategies
4. **Troubleshooting guide** - Common issues and solutions

---

## Summary

This report defines **11 focused MCP tools** for planning-oriented retrieval from Langfuse traces:

**ID Retrieval (2 tools)**:
- Session discovery by timerange
- Trace discovery by keyword

**Core Extraction (2 tools)**:
- Tool call extraction (session and trace level)
- Support for both SPAN and metadata patterns

**Timeline and Search (3 tools)**:
- Execution timeline reconstruction
- Keyword search across tool calls
- Usage statistics and analytics

**Planning Analysis (4 tools)**:
- LLM plan extraction with semantic analysis
- Action dependency extraction with causal inference
- Plan success pattern analysis
- Grammar-based domain export

**Key Innovations**:
- **Flexible tool call detection** - SPAN + metadata patterns
- **LLM-assisted analysis** - Plan detection, causal inference, precondition/effect extraction
- **Human-friendly ID retrieval** - Timestamp and keyword-based discovery
- **Async + rate limiting** - High-performance with API respect
- **Format abstraction** - Grammar-based generation for extensibility

The tools provide comprehensive support for extracting LLM planning behavior and integrating with planning domain systems.
