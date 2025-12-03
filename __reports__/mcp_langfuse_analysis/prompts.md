# Kiro Prompts

## 1. Iterating over MVP tool definitions report.

This is the design phase of what this project will become. The design  is a good entry point. I want to iterate on  .


This report `__reports__\mcp_langfuse_analysis\02-new_mcp_server_perspective_v1.md` is good but I want it to be more focused and not contain algorithm implementation (this will be for.. the implementation time!). However, pseudo-code is very welcome, and strategic code snippets of ~20 lines can be included as supporting material.

Regarding:
```
1. **Knowledge Extraction**: Build knowledge graphs from conversations
2. **Interaction Analysis**: Understand user-LLM dynamics
3. **Plan Tracking**: Monitor LLM decision-making
4. **Performance Optimization**: Identify bottlenecks and waste
5. **Debugging**: Trace errors and failure patterns
6. **Training Data**: Generate high-quality datasets
```

the stakeholders do not necessiraly agree with the order.

Insight for you: I already have another MCP server that connects to the Graph database ArangDB, so the feature of storing knowledge graphs with this MCP server is a bit overkill. But it's true we want to be able to retrieve the information, and probably return a graph structure --> we don't need to decide now but we need to discuss a bit the alternatives for an MCP-friendly representation of graphs as input and output.

Which means, we need to focus more on what exactly might be comming as input of the MCP servers aznd what might be comming as output. Some of the REST API usage logic will be common to all tools (I guess). 

Let's focus on rebuilding the activity of LLMs-Human interactions. To give you the context, this MCP server will first be integrated within a stack which allows to extract tool usage plans carried out by LLMs in order to store them in a very well-defined way, and then be able to store each actions independantly in a planning domain where planning algorithms can find plans independantly of the stochasticity of the LLM. It is a complex system.

hence your suggestions 

`extract_tool_calls_from_session` | Session-level tool extraction | Medium | P0 |
`extract_tool_calls_from_trace` | Trace-level tool extraction | Medium | P0 |
`search_tool_calls_by_keyword |` Content search | Low | P1 |
`get_tool_call_statistics |` Usage analytics | Low | P1 |
`reconstruct_execution_timeline |` Temporal ordering | High | P0 |

And

| `extract_llm_plans` | Plan extraction | High | P2 |

Are, in fact, probably all P0 for us.

Generally speaking, we need tools that can scrap the traces for "planing-oriented retrieval" (just made it up, but I think it's a good one, let's use it as reference)

**Your task**: Write a focused planning-oriented retrieval tools definition report. You can suggest additional tools given your understanding of the topic and the available Langfuse REST API at `__temp__\langfuse_rest_api_power_document.txt` (WARNING: very long --> grep-search it)


**Constraints**

-  REPORTING GUIDELINES

## 2. Comments and iteration over planning oriented retrieval tools

**About SPAN**!
- LiteLLM only creates GENERATION observations - one per LLM API call
- Tool calls are logged as metadata within the generation's output, not as separate SPANs
- So it's not that easy because we could be looking for SPANs given it's the main Langfuse way of doing it. But not every application using Langfuse actually leverage the SPAN and Langfuse "normal" instrumentation
- We cannot change this, we must support both looking for tool calls that could be in SPANs or metadata.
- But I gess, it's not so complicated given SPANS would be immediately visible in "observation" while LLM calls can simply be searched for tools metadata.

**About getting traces or sessions**
- If the LLM based agent is very autonomous in the search, then it won't always be given the trace/session/user IDs
- Plus, IDs are super annoying to retrieve and not human-friendly.
- So we must implement a tool for the LLM to retrieve such IDs. I see two main possibilities:
  - leveraging the same timestamps pattern you included before
  - related to keywords?
  - do yu see any other smart query pattern?
- I like the arguments `"include_context"` and `"include_results"` :D


**About `extract_llm_plans`**
- You are suggesting three retrieval strategies; I am not sure any of them will work. Typically `metadata.is_plan=true` doesn't exist to my knowledge. And parsing LLM output or detect tool call sequences seems very fragile because of the unstructured outputs of LLMs as well as the diversity of LLMs. Hence, here I am more thinking of leveraging LLM sampling sch that the tools, with well-engineered prompts, can query back LLMs to analyze concatenated traces with context/no context based on the time stamps or within complete sessions. The LLM sampling will help outputing whether a i) Plan was detected in this trace and ii)what is the plan, what are the tools involved.

**About AI PLanning-related things**
- I like you suggestion to have different export formats such as `PDDL/JSON/GraphML`
  - Although, the rest of our infrstructure will not be using any of those
  - But I understand why you suggested them.
  - For now, in the pseudo code and the definition report, I prefer to be agnostic of the return format, and we will simply implement an abstraction that will allows us to expand later based on the demands of the output type later.
- Actually, if this is an LLM that is going to generate the export formats as well (because I have already tried to do programatic generation of the planning domain from unstructured text data and god knows it's hard), I think we could do the pattern that developpers of the MCP servers will put the grammar of the expected format (PDDL or other) vin MCP ressources, that will be injected into LLM Sampling.
  - We will/might need also need to include a validator at the generation step to make sure the output follows the grammar.
  - But the validator is already in other parts of the system for the strict construction of the planning domain with another (very) well-designed MCP server.
  - Hence, our priority is to make the output not "stupid" to make sure it is clear enough for the LLM to leverage the other Action & Planning domain ingestion

**About extract_action_dependencies**
- It is a very interresting tool.
- Definitly, the three `2. Analyze temporal ordering (A before B)`, `3. Detect data flow (output of A used as input to B)`, `4. Identify causal relationships (A triggers B)` will be useful information. But I think inferring causal relationship programmatically might be complicated, unless you are suggesting to use LLM sampling as well to analyze a complete trace and let the LLM be the judge of the causality?
- Minor inconsistency: you are mixing the terminology of "parent-child" and "causal"
- it is VERY good that you included information `"preconditions"` and `"effects"` for the actions. It is indeed a crucial aspect of action definitions in AI Planning


**About execution of the tools**
- I am extermely worried about the time complexity of these because it will be a lot if IO requests + Json parsing + in Python: all of which are slow by nature.
- Hence, I knwo you wrote a little `4.1 Async Batch Processing` but I want the pseudo code of the MCP server to explicitly include small guidance for multi-threading/caching friendly. 
- I also want to be able to send as many IO queries while not exceeding RPMs (to be a good internet citizen :) )
  - Maybe RPMs can be an argument fo all the tool calls?
  - Are there official RPMs for all Langfuse servers (even if, in our case, everything is hostedf locally)?
- You chose asyncio batch but why not multithread processing? At least for the reading/reconstructing of the trees or all data acquisition, shouldn't we multi-thread or multi-process it?

**Your task**: Write a new version of the report accounting for all the comments.

## 3. Comments and iteration over planning oriented retrieval tools 2

**About 
```json
{
    "content": null,
    "role": "assistant",
    "tool_calls": [
        {
            "function": {
                "arguments": {
                    "a": 78,
                    "b": 98
                },
                "name": "tool_exponentiate_post"
            },
            "id": "9dn7O9167",
            "type": "function"
        }
    ],
    "function_call": null
}
```