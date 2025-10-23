"""Advanced LangGraph implementations for complex workflows."""

from typing import Any, Dict, List

from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from .tools import get_mcp_tools


# State definition for the graph
class AgentState(TypedDict):
    """State for the agent graph."""

    messages: List[Any]
    tools_used: List[str]
    context: Dict[str, Any]


def add_tools_used(left: List[str], right: List[str]) -> List[str]:
    """Add new tools to the tools_used list."""
    return list(set(left + right))


# Enhanced state with reducers
class EnhancedAgentState(TypedDict):
    """Enhanced state with proper reducers."""

    messages: List[Any]  # Will be managed by add_messages
    tools_used: List[str]  # Will be managed by add_tools_used
    context: Dict[str, Any]


async def create_rag_workflow():
    """
    Create a RAG (Retrieve-Augment-Generate) workflow using LangGraph.

    This is more advanced than the simple agent and provides:
    - Explicit retrieval step
    - Context management
    - Multi-step reasoning
    """

    # Get MCP tools
    tools = await get_mcp_tools(["retrieve_documents"])

    async def retrieve_step(state: AgentState) -> Dict[str, Any]:
        """Step 1: Retrieve relevant documents."""
        messages = state["messages"]
        last_message = messages[-1]

        # Use retrieval tool
        if tools:
            retrieval_tool = tools[0]  # Assuming first tool is retrieval
            try:
                result = await retrieval_tool.ainvoke({"query": last_message.content})
                context = {"retrieved_docs": result}
                tools_used = state.get("tools_used", []) + [retrieval_tool.name]

                return {
                    "context": {**state.get("context", {}), **context},
                    "tools_used": tools_used,
                }
            except Exception as e:
                print(f"Retrieval failed: {e}")
                return {"context": state.get("context", {})}

        return {"context": state.get("context", {})}

    async def generate_step(state: AgentState) -> Dict[str, Any]:
        """Step 2: Generate response based on retrieved context."""
        context = state.get("context", {})

        # Build contextualized prompt
        retrieved_docs = context.get("retrieved_docs", "No documents retrieved")

        # Create response message
        response = AIMessage(
            content=f"Based on the retrieved information: {retrieved_docs}"
        )

        return {"messages": [response]}

    def should_retrieve(state: AgentState) -> str:
        """Decision function: should we retrieve documents?"""
        messages = state["messages"]
        last_message = messages[-1]

        # Simple heuristic: retrieve if the message contains question words
        question_words = ["what", "how", "why", "when", "where", "who"]
        if any(word in last_message.content.lower() for word in question_words):
            return "retrieve"
        return "generate"

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("retrieve", retrieve_step)
    workflow.add_node("generate", generate_step)

    # Add edges
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    # Compile the graph
    return workflow.compile()


async def create_multi_tool_workflow():
    """
    Create a workflow that can use multiple tools intelligently.
    """
    tools = await get_mcp_tools()  # Get all available tools

    async def tool_selection_step(state: AgentState) -> Dict[str, Any]:
        """Analyze the request and select appropriate tools."""
        messages = state["messages"]
        last_message = messages[-1]

        # Simple tool selection logic (can be enhanced with LLM)
        selected_tools = []
        content = last_message.content.lower()

        if "search" in content or "find" in content or "retrieve" in content:
            selected_tools.extend(
                [t for t in tools if "retrieve" in t.name or "search" in t.name]
            )

        if "email" in content or "send" in content:
            selected_tools.extend(
                [t for t in tools if "email" in t.name or "send" in t.name]
            )

        return {
            "context": {
                **state.get("context", {}),
                "selected_tools": [t.name for t in selected_tools],
            }
        }

    async def execute_tools_step(state: AgentState) -> Dict[str, Any]:
        """Execute the selected tools."""
        context = state.get("context", {})
        selected_tool_names = context.get("selected_tools", [])

        results = {}
        tools_used = state.get("tools_used", [])

        for tool_name in selected_tool_names:
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                try:
                    # This would need to be customized based on each tool's input requirements
                    result = await tool.ainvoke(
                        {"query": state["messages"][-1].content}
                    )
                    results[tool_name] = result
                    tools_used.append(tool_name)
                except Exception as e:
                    print(f"Error using tool {tool_name}: {e}")

        return {
            "context": {**context, "tool_results": results},
            "tools_used": tools_used,
        }

    async def synthesize_response_step(state: AgentState) -> Dict[str, Any]:
        """Synthesize final response from tool results."""
        context = state.get("context", {})
        tool_results = context.get("tool_results", {})

        # Create a comprehensive response
        response_parts = ["Based on the available information:"]

        for tool_name, result in tool_results.items():
            response_parts.append(f"\nFrom {tool_name}: {result}")

        response = AIMessage(content="\n".join(response_parts))

        return {"messages": [response]}

    # Build workflow
    workflow = StateGraph(AgentState)

    workflow.add_node("select_tools", tool_selection_step)
    workflow.add_node("execute_tools", execute_tools_step)
    workflow.add_node("synthesize", synthesize_response_step)

    workflow.set_entry_point("select_tools")
    workflow.add_edge("select_tools", "execute_tools")
    workflow.add_edge("execute_tools", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()


# Factory function to create different types of workflows
async def create_workflow(workflow_type: str = "simple"):
    """
    Factory function to create different workflow types.

    Args:
        workflow_type: "simple", "rag", or "multi_tool"
    """
    if workflow_type == "rag":
        return await create_rag_workflow()
    elif workflow_type == "multi_tool":
        return await create_multi_tool_workflow()
    else:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
