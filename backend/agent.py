from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from state import AgentState
from nodes import planner_node, search_node, summarizer_node, critic_node, report_node

def continue_to_search(state: AgentState):
    # Send API initiates parallel execution for each sub-question
    return [Send("search_node", {"sub_question": sq}) for sq in state["sub_questions"]]

def route_critic(state: AgentState):
    score = state.get("critic_score", 0)
    loop_count = state.get("loop_count", 0)
    
    # Route to report if score passes threshold, otherwise retry up to 3 times
    if score >= 7 or loop_count >= 4:
        return "report_node"
    else:
        return "planner_node"

builder = StateGraph(AgentState)

builder.add_node("planner_node", planner_node)
builder.add_node("search_node", search_node)
builder.add_node("summarizer_node", summarizer_node)
builder.add_node("critic_node", critic_node)
builder.add_node("report_node", report_node)

builder.add_edge(START, "planner_node")
builder.add_conditional_edges("planner_node", continue_to_search, ["search_node"])
builder.add_edge("search_node", "summarizer_node")
builder.add_edge("summarizer_node", "critic_node")
builder.add_conditional_edges("critic_node", route_critic, ["planner_node", "report_node"])
builder.add_edge("report_node", END)

graph = builder.compile()
