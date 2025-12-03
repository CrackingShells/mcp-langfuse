# MCP Langfuse Analysis Reports

Analysis reports for justifying and designing a new Langfuse MCP server focused on advanced trace exploration and tool call extraction.

---

## Documents

### Phase 1: Analysis

- **[00-existing_mcp_servers_analysis_v0.md](./00-existing_mcp_servers_analysis_v0.md)** ⭐ **CURRENT** - Analysis of existing Langfuse MCP servers
  - Evaluated 3 existing implementations (avivsinai, langfuse official, native)
  - Identified critical gaps: no tool call extraction, no temporal reconstruction, no context association
  - Conclusion: All existing servers are either basic API wrappers or prompt-management focused

- **[01-rest_api_capabilities_analysis_v0.md](./01-rest_api_capabilities_analysis_v0.md)** ⭐ **CURRENT** - Deep dive into Langfuse REST API
  - Comprehensive analysis of traces, observations, sessions, and metrics endpoints
  - Advanced filtering capabilities (JSON filter syntax)
  - Data structures for temporal reconstruction
  - Tool call identification patterns
  - Design implications for new server

- **[03-planning_oriented_retrieval_tools_v0.md](./03-planning_oriented_retrieval_tools_v0.md)** ⭐ **CURRENT** - Focused planning-oriented retrieval tools
  - 9 focused MCP tools for planning domain integration
  - Planning-oriented retrieval: extract LLM plans, tool calls, execution timelines, dependencies
  - Graph representation alternatives for MCP (adjacency list, nested, DOT, JSON-LD)
  - REST API usage patterns (filtering, pagination, metrics aggregation)
  - Implementation phases and integration considerations
  - All tools prioritized as P0 for planning use case

- **[02-new_mcp_server_perspective_v1.md](./02-new_mcp_server_perspective_v1.md)** 📦 **ARCHIVED** - Comprehensive architecture (too broad)
  - Expanded scope: 16 tools across 6 use case categories
  - Architectural decisions (async, streaming, caching, modular pipeline)
  - Detailed algorithms (temporal reconstruction, tool extraction, context association, knowledge extraction, performance profiling)
  - Note: Superseded by focused planning-oriented approach

- **[02-new_mcp_server_perspective_v0.md](./02-new_mcp_server_perspective_v0.md)** 📦 **ARCHIVED** - Initial MVP design
  - Problem statement and gap analysis
  - 5 core MVP tools
  - Basic technical architecture

---

## Quick Summary

### Critical Findings

**Existing Servers**:
- avivsinai/langfuse-mcp: Basic API wrapper, no data processing
- langfuse/mcp-server-langfuse: Prompt management only (TypeScript)
- Langfuse Native MCP: Prompt management only (official)

**REST API Capabilities**:
- Rich observation data with parent-child relationships
- Temporal markers (startTime, endTime, completionStartTime)
- Type discrimination (SPAN, GENERATION, EVENT)
- Advanced JSON filtering
- Metrics API for aggregation
- Session grouping for context boundaries

**Gap Identified**:
- No existing server provides intelligent trace exploration
- API provides all primitives, but requires processing layer
- Tool call extraction, temporal reconstruction, and context association are missing

### Recommended Approach

**Build a new MCP server focused on planning-oriented retrieval** that:
1. Extracts tool calls with full planning context
2. Reconstructs execution timelines with dependency tracking
3. Extracts and matches LLM plans to actual executions
4. Analyzes action dependencies for planning domains
5. Exports data in planning-compatible formats (PDDL, graph structures)

**Core Tools (P0)** - 9 tools:
1. `extract_tool_calls_from_session` - Session-level tool extraction
2. `extract_tool_calls_from_trace` - Trace-level tool extraction
3. `search_tool_calls_by_keyword` - Content search across tool calls
4. `get_tool_call_statistics` - Usage analytics and patterns
5. `reconstruct_execution_timeline` - Temporal ordering with parallelism detection
6. `extract_llm_plans` - Plan detection and execution matching
7. `extract_action_dependencies` - Dependency graph extraction
8. `analyze_plan_success_patterns` - Success/failure pattern analysis
9. `export_planning_domain` - Export to planning formats (PDDL, JSON, GraphML)

**Key Design Decisions**:
- Graph representation: Support multiple formats (adjacency list, DOT, PDDL)
- Integration: Compatible with ArangoDB MCP server for graph storage
- Focus: Planning domain integration, not general analytics
- Processing: Async batch processing, multi-level caching, streaming for large datasets

### Implementation Phases

**Phase 1: Core Extraction** (P0)
- Tools 1, 2, 5: Foundation extraction and timeline reconstruction

**Phase 2: Planning Analysis** (P0)
- Tools 6, 7: Plan extraction and dependency analysis

**Phase 3: Search and Analytics** (P0)
- Tools 3, 4: Search and statistics

**Phase 4: Advanced Features** (P1)
- Tools 8, 9: Pattern analysis and domain export

### Current Status

- ✅ Phase 1: Analysis complete (existing servers, REST API)
- ✅ Phase 2: Planning-oriented tool design complete
- ⏳ Phase 3: Stakeholder review and iteration
- ⏳ Phase 4: Implementation

---

## Status

- ✅ Existing servers analyzed (Report 00)
- ✅ REST API capabilities documented (Report 01)
- ✅ Initial architecture explored (Report 02-v0, 02-v1)
- ✅ **Planning-oriented retrieval tools defined (Report 03-v0)** ⭐
- ⏳ Ready for stakeholder review and refinement

---

**Last Updated**: 2025-12-03
**Report Version**: v0 (Planning-oriented focus)
**Total Tools Designed**: 9 (all P0 for planning use case)
**Focus**: Planning domain integration, LLM plan extraction, execution analysis
