# Planning-Oriented Retrieval Tools for Langfuse MCP Server

**Report Date**: 2025-12-03
**Report Version**: v0
**Purpose**: Define focused MCP tools for extracting and analyzing LLM planning behavior from Langfuse traces

---

## Executive Summary

This report defines a focused set of MCP tools specifically designed for **planning-oriented retrieval** from Langfuse traces. The tools enable extraction, reconstruction, and analysis of LLM decision-making processes, tool usage patterns, and execution plans for integration with planning domain systems.

**Core Focus**: Extract structured planning data from Langfuse traces to support:
- Plan extraction and storage in planning domains
- Tool usage pattern analysis
- Execution timeline reconstruction
- Planning behavior analytics

**Key Design Principles**:
- Focus on planning-relevant data extraction (not general analytics)
- Support both session-level and trace-level operations
- Enable incremental processing for large datasets
- Provide structured outputs compatible with planning systems

---

## 1. Context and Requirements

### 1.1 System Integration Context

The MCP server will integrate into a stack that:
1. **Extracts tool usage plans** from LLM interactions
2. **Stores plans** in a well-defined format
3. **Records individual actions** in a planning domain
4. **Enables planning algorithms** to find plans independently of LLM stochasticity

### 1.2 Graph Representation Considerations

**Current State**: Another MCP server (ArangoDB) handles knowledge graph storage.

**Design Decision**: This server focuses on **retrieving graph-structured data** rather than storing it.

**Graph I/O Alternatives for MCP**:

```python
# Option 1: Adjacency List (Simple, MCP-friendly)
{
  "nodes": [{"id": "n1", "type": "action", "data": {...}}],
  "edges": [{"from": "n1", "to": "n2", "type": "precedes"}]
}

# Option 2: Nested Structure (Hierarchical plans)
{
  "plan": {
    "action": "root_task",
    "children": [
      {"action": "subtask_1", "children": [...]},
      {"action": "subtask_2", "children": [...]}
    ]
  }
}

# Option 3: DOT Format (Planning tools compatible)
"digraph Plan { n1 -> n2 [label=\"precedes\"]; }"

# Option 4: JSON-LD (Semantic web compatible)
{
  "@context": {...},
  "@graph": [...]
}
```

**Recommendation**: Support multiple formats via `output_format` parameter, defaulting to adjacency list for simplicity.

### 1.3 Priority Alignment

All tools in this report are **P0** (critical priority) for the planning-oriented use case:
- `extract_tool_calls_from_session` - P0
- `extract_tool_calls_from_trace` - P0
- `search_tool_calls_by_keyword` - P0
- `get_tool_call_statistics` - P0
- `reconstruct_execution_timeline` - P0
- `extract_llm_plans` - P0

---

## 2. Core Tool Definitions

### 2.1 Tool Call Extraction Tools

#### Tool 2.1.1: `extract_tool_calls_from_session`

**Purpose**: Extract all tool calls from a session with full context for planning analysis.

**MCP Tool Signature**:
```python
{
  "name": "extract_tool_calls_from_session",
  "description": "Extract all tool calls from a Langfuse session with planning context",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {"type": "string", "description": "Langfuse session ID"},
      "include_context": {"type": "boolean", "default": true, "description": "Include preceding LLM reasoning"},
      "include_results": {"type": "boolean", "default": true, "description": "Include tool execution results"},
      "filter_by_status": {"type": "string", "enum": ["all", "success", "failure"], "default": "all"}
    },
    "required": ["session_id"]
  }
}
```

**Processing Strategy**:

```
1. Fetch all traces for session (GET /api/public/traces?sessionId={id})
2. For each trace, fetch observations (GET /api/public/observations?traceId={id})
3. Filter observations by type=SPAN (tool executions)
4. For each SPAN, find parent GENERATION (LLM reasoning)
5. Extract tool name, arguments, results, timestamps
6. Build structured tool call records with context
```

**REST API Leverage**:
- `GET /api/public/traces?sessionId={id}&fields=core` - Lightweight trace list
- `GET /api/public/observations?traceId={id}&type=SPAN` - Filter tool executions
- `GET /api/public/observations/{id}` - Get full observation details
- Parent-child relationships via `parentObservationId` field

**Output Structure**:
```json
{
  "session_id": "string",
  "total_tool_calls": "number",
  "traces_analyzed": "number",
  "tool_calls": [
    {
      "id": "observation_id",
      "trace_id": "string",
      "timestamp": "ISO8601",
      "tool_name": "string",
      "arguments": {},
      "result": {},
      "status": "success|failure",
      "duration_seconds": "number",
      "context": {
        "preceding_llm_output": "string",
        "llm_observation_id": "string",
        "user_query": "string"
      }
    }
  ]
}
```

#### Tool 2.1.2: `extract_tool_calls_from_trace`

**Purpose**: Extract tool calls from a single trace (finer granularity).

**MCP Tool Signature**:
```python
{
  "name": "extract_tool_calls_from_trace",
  "description": "Extract tool calls from a specific Langfuse trace",
  "inputSchema": {
    "type": "object",
    "properties": {
      "trace_id": {"type": "string"},
      "include_context": {"type": "boolean", "default": true},
      "include_results": {"type": "boolean", "default": true}
    },
    "required": ["trace_id"]
  }
}
```


**Processing Strategy**:
```
1. Fetch trace details (GET /api/public/traces/{traceId})
2. Fetch observations (GET /api/public/observations?traceId={id}&type=SPAN)
3. Build observation tree from parent-child relationships
4. Extract tool calls with context from parent GENERATION nodes
5. Return structured tool call data
```

**Output Structure**: Same as `extract_tool_calls_from_session` but scoped to single trace.

---

### 2.2 Search and Query Tools

#### Tool 2.2.1: `search_tool_calls_by_keyword`

**Purpose**: Search tool calls by content (arguments, results, context) for pattern discovery.

**MCP Tool Signature**:
```python
{
  "name": "search_tool_calls_by_keyword",
  "description": "Search tool calls by keyword in arguments, results, or context",
  "inputSchema": {
    "type": "object",
    "properties": {
      "keyword": {"type": "string", "description": "Search term"},
      "search_in": {
        "type": "array",
        "items": {"type": "string", "enum": ["arguments", "results", "context", "tool_name"]},
        "default": ["arguments", "results", "context"]
      },
      "session_id": {"type": "string", "description": "Optional: limit to session"},
      "from_timestamp": {"type": "string", "format": "date-time"},
      "to_timestamp": {"type": "string", "format": "date-time"},
      "limit": {"type": "integer", "default": 100}
    },
    "required": ["keyword"]
  }
}
```

**Processing Strategy**:
```
1. Query observations with filters (GET /api/public/observations)
   - type=SPAN for tool executions
   - fromStartTime/toStartTime for time range
   - sessionId if provided
2. Fetch observation details with input/output (fields=core,io)
3. Search keyword in specified fields (client-side filtering)
4. Return matching tool calls with context
```

**REST API Leverage**:
- `GET /api/public/observations?type=SPAN&fromStartTime={ts}&toStartTime={ts}`
- `filter` parameter for metadata searches
- Pagination for large result sets

**Output Structure**:
```json
{
  "keyword": "string",
  "total_matches": "number",
  "matches": [
    {
      "tool_call_id": "string",
      "trace_id": "string",
      "session_id": "string",
      "timestamp": "ISO8601",
      "tool_name": "string",
      "match_location": "arguments|results|context",
      "match_snippet": "string",
      "full_tool_call": {...}
    }
  ]
}
```

---

### 2.3 Analytics and Statistics Tools

#### Tool 2.3.1: `get_tool_call_statistics`

**Purpose**: Aggregate statistics on tool usage patterns for planning optimization.

**MCP Tool Signature**:
```python
{
  "name": "get_tool_call_statistics",
  "description": "Get aggregated statistics on tool usage patterns",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {"type": "string", "description": "Optional: scope to session"},
      "from_timestamp": {"type": "string", "format": "date-time"},
      "to_timestamp": {"type": "string", "format": "date-time"},
      "group_by": {
        "type": "string",
        "enum": ["tool", "session", "trace", "time_bucket"],
        "default": "tool"
      },
      "time_bucket": {"type": "string", "enum": ["hour", "day", "week"], "default": "day"}
    }
  }
}
```


**Processing Strategy**:
```
1. Use Metrics API for aggregated statistics
   POST /api/public/metrics with query structure
2. Query observations for detailed breakdowns
3. Calculate success rates, durations, frequencies
4. Group by specified dimension
5. Return aggregated statistics
```

**REST API Leverage**:
- `POST /api/public/metrics` - Primary aggregation endpoint
- Filter by observation type, time range, metadata
- Aggregate functions: count, sum, avg, percentiles
- Time-series grouping with granularity parameter

**Metrics API Query Example**:
```json
{
  "select": [
    {"column": "name", "agg": null},
    {"column": "latency", "agg": "avg"},
    {"column": "id", "agg": "count"}
  ],
  "filters": [
    {"column": "type", "operator": "=", "value": "SPAN", "type": "string"}
  ],
  "groupBy": [{"column": "name", "type": "string"}],
  "fromTimestamp": "2024-01-01T00:00:00Z",
  "toTimestamp": "2024-12-31T23:59:59Z"
}
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
      "total_cost_usd": "number",
      "first_seen": "ISO8601",
      "last_seen": "ISO8601"
    }
  ],
  "time_series": [
    {
      "time_bucket": "ISO8601",
      "tool_calls": "number",
      "unique_tools": "number"
    }
  ]
}
```

---

### 2.4 Temporal Reconstruction Tools

#### Tool 2.4.1: `reconstruct_execution_timeline`

**Purpose**: Reconstruct the temporal execution order of actions within a session/trace for plan analysis.

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
        "enum": ["timeline", "graph", "gantt"],
        "default": "timeline"
      }
    },
    "oneOf": [
      {"required": ["session_id"]},
      {"required": ["trace_id"]}
    ]
  }
}
```

**Processing Strategy**:
```
1. Fetch all observations for scope (session or trace)
2. Sort by startTime (primary), then by parent-child relationships
3. Detect parallel executions (overlapping time ranges)
4. Build dependency graph from parent-child links
5. Identify critical path (longest dependency chain)
6. Format output according to requested format
```

**Temporal Ordering Pseudo-code**:
```python
def reconstruct_timeline(observations):
    # Sort by timestamp
    sorted_obs = sorted(observations, key=lambda o: o.startTime)
    
    # Build parent-child map
    children_map = defaultdict(list)
    for obs in observations:
        if obs.parentObservationId:
            children_map[obs.parentObservationId].append(obs)
    
    # Detect parallel executions
    parallel_groups = []
    for i, obs1 in enumerate(sorted_obs):
        parallel = [obs1]
        for obs2 in sorted_obs[i+1:]:
            if time_overlap(obs1, obs2) and not is_ancestor(obs1, obs2):
                parallel.append(obs2)
        if len(parallel) > 1:
            parallel_groups.append(parallel)
    
    return {
        "timeline": sorted_obs,
        "parallel_groups": parallel_groups,
        "dependency_graph": children_map
    }
```


**REST API Leverage**:
- `GET /api/public/observations?traceId={id}` - All observations for trace
- `GET /api/public/traces?sessionId={id}` then fetch observations per trace
- `orderBy=startTime.asc` for temporal sorting
- `parentObservationId` field for dependency tracking

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
  ],
  "critical_path": {
    "observations": ["observation_id"],
    "total_duration_seconds": "number"
  }
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

### 2.5 Plan Extraction Tools

#### Tool 2.5.1: `extract_llm_plans`

**Purpose**: Extract LLM-decided action plans and match them to actual executions.

**MCP Tool Signature**:
```python
{
  "name": "extract_llm_plans",
  "description": "Extract LLM planning decisions and match to executions",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {"type": "string"},
      "trace_id": {"type": "string"},
      "plan_detection_strategy": {
        "type": "string",
        "enum": ["metadata_marker", "output_parsing", "tool_sequence"],
        "default": "output_parsing",
        "description": "How to identify planning observations"
      },
      "include_execution_matching": {"type": "boolean", "default": true},
      "include_deviation_analysis": {"type": "boolean", "default": true}
    },
    "oneOf": [
      {"required": ["session_id"]},
      {"required": ["trace_id"]}
    ]
  }
}
```

**Processing Strategy**:
```
1. Identify planning observations (GENERATION type)
   - Strategy 1: Look for metadata markers (e.g., metadata.is_plan=true)
   - Strategy 2: Parse LLM output for action lists/sequences
   - Strategy 3: Detect tool call sequences in output
2. Extract planned actions from LLM output
3. Fetch subsequent SPAN observations (actual executions)
4. Match planned actions to executed observations
5. Analyze deviations (order changes, skipped, added actions)
6. Calculate adherence metrics
```

**Plan Detection Pseudo-code**:
```python
def detect_plans(observations):
    plans = []
    
    for obs in observations:
        if obs.type != "GENERATION":
            continue
            
        # Strategy 1: Metadata marker
        if obs.metadata.get("is_plan"):
            plans.append(extract_plan_from_metadata(obs))
            continue
        
        # Strategy 2: Output parsing
        output = obs.output
        if contains_action_list(output):
            actions = parse_action_list(output)
            plans.append({
                "observation_id": obs.id,
                "timestamp": obs.startTime,
                "planned_actions": actions
            })
            continue
        
        # Strategy 3: Tool sequence detection
        if contains_tool_calls(output):
            tools = extract_tool_calls_from_text(output)
            plans.append({
                "observation_id": obs.id,
                "timestamp": obs.startTime,
                "planned_actions": tools
            })
    
    return plans
```


**Execution Matching Pseudo-code**:
```python
def match_executions(plan, observations):
    # Get SPAN observations after plan timestamp
    executions = [o for o in observations 
                  if o.type == "SPAN" 
                  and o.startTime > plan["timestamp"]]
    
    matches = []
    for planned_action in plan["planned_actions"]:
        # Find matching execution
        match = find_best_match(planned_action, executions)
        matches.append({
            "planned": planned_action,
            "executed": match,
            "matched": match is not None,
            "time_delta": match.startTime - plan["timestamp"] if match else None
        })
    
    # Detect unplanned executions
    unplanned = [e for e in executions 
                 if not any(m["executed"] == e for m in matches)]
    
    return {
        "matches": matches,
        "unplanned_executions": unplanned,
        "adherence_score": len([m for m in matches if m["matched"]]) / len(plan["planned_actions"])
    }
```

**REST API Leverage**:
- `GET /api/public/observations?traceId={id}&type=GENERATION` - Planning observations
- `GET /api/public/observations?traceId={id}&type=SPAN` - Execution observations
- `fields=core,io` to get input/output for parsing
- Temporal ordering for sequence matching

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
      "detection_strategy": "metadata_marker|output_parsing|tool_sequence",
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
            "status": "success|failure",
            "result": {}
          }
        ],
        "unmatched_planned": [
          {"sequence": "number", "action": "string", "reason": "skipped|failed|not_executed"}
        ],
        "unplanned_executions": [
          {"observation_id": "string", "tool_name": "string", "reason": "added|recovery|fallback"}
        ]
      },
      "deviation_analysis": {
        "order_preserved": "boolean",
        "actions_skipped": "number",
        "actions_added": "number",
        "adherence_score": "number (0-1)",
        "deviations": [
          {
            "type": "order_change|skip|addition",
            "description": "string",
            "impact": "high|medium|low"
          }
        ]
      }
    }
  ]
}
```

---

## 3. Additional Planning-Oriented Tools

### 3.1 Tool: `extract_action_dependencies`

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
        "items": {"type": "string", "enum": ["temporal", "data_flow", "causal", "parent_child"]},
        "default": ["temporal", "data_flow", "parent_child"]
      },
      "output_format": {"type": "string", "enum": ["graph", "pddl", "json"], "default": "graph"}
    },
    "oneOf": [
      {"required": ["session_id"]},
      {"required": ["trace_id"]}
    ]
  }
}
```

**Processing Strategy**:
```
1. Fetch all observations with parent-child relationships
2. Analyze temporal ordering (A before B)
3. Detect data flow (output of A used as input to B)
4. Identify causal relationships (A triggers B)
5. Build dependency graph
6. Format for planning domain (PDDL-compatible if requested)
```

**Dependency Detection Pseudo-code**:
```python
def extract_dependencies(observations):
    deps = []
    
    for i, obs_a in enumerate(observations):
        for obs_b in observations[i+1:]:
            # Temporal dependency
            if obs_a.endTime < obs_b.startTime:
                deps.append({"from": obs_a.id, "to": obs_b.id, "type": "temporal"})
            
            # Data flow dependency
            if output_used_as_input(obs_a, obs_b):
                deps.append({"from": obs_a.id, "to": obs_b.id, "type": "data_flow"})
            
            # Parent-child dependency
            if obs_b.parentObservationId == obs_a.id:
                deps.append({"from": obs_a.id, "to": obs_b.id, "type": "parent_child"})
    
    return deps
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
      "effects": ["effect"]
    }
  ],
  "edges": [
    {
      "from": "observation_id",
      "to": "observation_id",
      "dependency_type": "temporal|data_flow|causal|parent_child",
      "strength": "number (0-1)"
    }
  ]
}
```

**Output Structure (PDDL Format)**:
```lisp
(define (domain extracted_plan)
  (:requirements :strips :typing)
  (:types action)
  (:predicates
    (completed ?a - action)
    (precedes ?a1 ?a2 - action))
  (:action execute_tool_call
    :parameters (?tool - action)
    :precondition (and ...)
    :effect (completed ?tool)))
```

---

### 3.2 Tool: `analyze_plan_success_patterns`

**Purpose**: Identify patterns in successful vs failed plan executions for optimization.

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
      "include_failure_analysis": {"type": "boolean", "default": true}
    },
    "required": ["from_timestamp", "to_timestamp"]
  }
}
```

**Processing Strategy**:
```
1. Extract all plans in time range using extract_llm_plans
2. Group plans by similarity (tool sequence, structure)
3. Calculate success rates per plan pattern
4. Identify common failure points
5. Analyze context differences between success/failure
6. Generate optimization recommendations
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
      "common_contexts": ["context_description"],
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

### 3.3 Tool: `export_planning_domain`

**Purpose**: Export extracted plans and actions in planning domain format for external planning systems.

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
      "format": {
        "type": "string",
        "enum": ["pddl", "json", "graphml", "dot"],
        "default": "json"
      },
      "include_metadata": {"type": "boolean", "default": true}
    }
  }
}
```

**Processing Strategy**:
```
1. Extract all plans and executions from specified scope
2. Build unified action library (all unique actions)
3. Extract preconditions and effects from observations
4. Generate domain definition in requested format
5. Include problem instances (specific plan executions)
6. Add metadata for traceability
```

**Output Structure (JSON Format)**:
```json
{
  "domain": {
    "name": "langfuse_extracted_domain",
    "actions": [
      {
        "name": "string",
        "parameters": {},
        "preconditions": ["condition"],
        "effects": ["effect"],
        "cost": "number",
        "avg_duration": "number",
        "success_rate": "number",
        "source_observations": ["observation_id"]
      }
    ],
    "predicates": ["predicate_definition"]
  },
  "problems": [
    {
      "name": "string",
      "initial_state": ["predicate"],
      "goal_state": ["predicate"],
      "plan": ["action_sequence"],
      "source_session": "string",
      "source_trace": "string"
    }
  ],
  "metadata": {
    "extraction_timestamp": "ISO8601",
    "source_sessions": ["session_id"],
    "total_plans": "number",
    "total_actions": "number"
  }
}
```

---

## 4. Common Processing Patterns

### 4.1 Async Batch Processing

All tools that process multiple traces/sessions should use async batch processing:

```python
async def process_session(session_id: str):
    # Fetch trace IDs
    traces = await api.get_traces(sessionId=session_id, fields="core")
    
    # Batch fetch observations
    semaphore = asyncio.Semaphore(10)  # Rate limiting
    async def fetch_with_limit(trace_id):
        async with semaphore:
            return await api.get_observations(traceId=trace_id)
    
    observations = await asyncio.gather(*[
        fetch_with_limit(t.id) for t in traces
    ])
    
    return process_observations(observations)
```


### 4.2 Observation Tree Building

Common pattern for reconstructing hierarchical structure:

```python
def build_observation_tree(observations: List[Observation]):
    # Index by ID
    obs_map = {o.id: o for o in observations}
    
    # Build children map
    children = defaultdict(list)
    roots = []
    
    for obs in observations:
        if obs.parentObservationId:
            children[obs.parentObservationId].append(obs)
        else:
            roots.append(obs)
    
    # Attach children
    for obs in observations:
        obs.children = children.get(obs.id, [])
    
    return roots  # Return root observations
```

### 4.3 Tool Call Identification

Common pattern for identifying tool executions:

```python
def identify_tool_calls(observations: List[Observation]):
    tool_calls = []
    
    for obs in observations:
        # Tool calls are SPAN observations
        if obs.type != "SPAN":
            continue
        
        # Find parent GENERATION for context
        parent = find_parent_generation(obs, observations)
        
        tool_calls.append({
            "observation": obs,
            "tool_name": obs.name,
            "arguments": parse_input(obs.input),
            "result": parse_output(obs.output),
            "context": parent.output if parent else None,
            "timestamp": obs.startTime,
            "duration": (obs.endTime - obs.startTime).total_seconds()
        })
    
    return tool_calls
```

### 4.4 Caching Strategy

Implement multi-level caching for performance:

```python
# Level 1: Raw API responses (1 hour TTL)
@cache(ttl=3600)
async def fetch_trace_cached(trace_id: str):
    return await api.get_trace(trace_id)

# Level 2: Processed structures (6 hour TTL)
@cache(ttl=21600)
def extract_tool_calls_cached(trace_id: str):
    trace = fetch_trace_cached(trace_id)
    return extract_tool_calls(trace)

# Level 3: Analytics (24 hour TTL)
@cache(ttl=86400)
def get_statistics_cached(session_id: str):
    tool_calls = extract_tool_calls_cached(session_id)
    return calculate_statistics(tool_calls)
```

---

## 5. REST API Usage Patterns

### 5.1 Efficient Filtering

Use API filters to reduce data transfer:

```python
# Good: Filter at API level
observations = api.get_observations(
    traceId=trace_id,
    type="SPAN",  # Only tool executions
    fromStartTime=start_time,
    toStartTime=end_time,
    fields="core,io"  # Only needed fields
)

# Bad: Fetch everything and filter client-side
all_observations = api.get_observations(traceId=trace_id)
filtered = [o for o in all_observations if o.type == "SPAN"]
```

### 5.2 Pagination Handling

Handle large result sets with pagination:

```python
async def fetch_all_observations(trace_id: str):
    all_obs = []
    page = 1
    
    while True:
        response = await api.get_observations(
            traceId=trace_id,
            page=page,
            limit=100
        )
        
        all_obs.extend(response.data)
        
        if len(response.data) < 100:  # Last page
            break
        
        page += 1
    
    return all_obs
```

### 5.3 Metrics API for Aggregation

Use Metrics API for heavy aggregations:

```python
# Query tool usage statistics
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
```

---

## 6. Tool Priority and Implementation Order

### Phase 1: Core Extraction (P0)
1. `extract_tool_calls_from_trace` - Foundation for all other tools
2. `extract_tool_calls_from_session` - Session-level extraction
3. `reconstruct_execution_timeline` - Temporal ordering

### Phase 2: Planning Analysis (P0)
4. `extract_llm_plans` - Plan detection and matching
5. `extract_action_dependencies` - Dependency graph building

### Phase 3: Search and Analytics (P0)
6. `search_tool_calls_by_keyword` - Content search
7. `get_tool_call_statistics` - Usage analytics

### Phase 4: Advanced Features (P1)
8. `analyze_plan_success_patterns` - Pattern analysis
9. `export_planning_domain` - Domain export

---

## 7. Integration Considerations

### 7.1 Planning Domain Integration

Output formats should be compatible with:
- **PDDL planners** (Fast Downward, FF, LAMA)
- **Graph databases** (ArangoDB via existing MCP server)
- **Custom planning systems** (JSON/adjacency list format)

### 7.2 Incremental Processing

Support incremental updates for active sessions:
- Track last processed timestamp
- Fetch only new observations since last update
- Merge with existing extracted data
- Invalidate affected caches

### 7.3 Error Handling

Robust error handling for production use:
- Graceful degradation (partial results on API errors)
- Retry logic with exponential backoff
- Clear error messages with context
- Logging for debugging

---

## 8. Next Steps

### 8.1 Validation Requirements

Before implementation:
1. **Stakeholder review** of tool definitions
2. **API capability verification** (test all required endpoints)
3. **Output format validation** (ensure planning system compatibility)
4. **Performance estimation** (expected latency for typical workloads)

### 8.2 Implementation Preparation

1. **Test data preparation** - Create sample Langfuse traces with known plans
2. **API client setup** - Async HTTP client with authentication
3. **Schema definitions** - Pydantic models for all data structures
4. **Unit test framework** - Test individual processing functions

### 8.3 Documentation Needs

1. **Tool usage examples** - Real-world scenarios for each tool
2. **API integration guide** - How to call tools from planning systems
3. **Performance tuning guide** - Optimization strategies
4. **Troubleshooting guide** - Common issues and solutions

---

## Summary

This report defines **9 focused MCP tools** for planning-oriented retrieval from Langfuse traces:

**Core Tools (P0)**:
- Tool call extraction (session and trace level)
- Execution timeline reconstruction
- LLM plan extraction and matching
- Action dependency extraction
- Content search and statistics

**Advanced Tools (P1)**:
- Plan success pattern analysis
- Planning domain export

All tools are designed to support the integration with planning domain systems, with emphasis on:
- Structured output formats (graph, timeline, PDDL)
- Efficient API usage (filtering, pagination, caching)
- Async processing for performance
- Planning-relevant data extraction

The tools provide the foundation for extracting LLM planning behavior and storing it in a format suitable for deterministic planning algorithms.
