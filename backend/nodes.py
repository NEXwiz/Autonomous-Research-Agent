import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
from state import AgentState, SearchNodeState, SubQuestion, SearchResult, SubQuestionSummary

load_dotenv()

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
search_tool = TavilySearchResults(max_results=3)

class PlannerOutput(BaseModel):
    sub_questions: List[str] = Field(description="A list of 3-5 sub-questions to research the topic.")

def planner_node(state: AgentState):
    topic = state["topic"]
    loop_count = state.get("loop_count", 0)
    critic_feedback = state.get("critic_feedback", "")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a research planner. Break the given topic into 3-5 specific sub-questions that need to be researched to write a comprehensive report."),
        ("user", "Topic: {topic}\n\n{feedback}")
    ])
    
    feedback_msg = f"Previous attempt feedback: {critic_feedback}\nPlease adjust the sub-questions accordingly to improve the research." if critic_feedback else ""
    
    # Generate sub-questions using structured output
    chain = prompt | llm.with_structured_output(PlannerOutput)
    result = chain.invoke({"topic": topic, "feedback": feedback_msg})
    
    sq_list = [{"question": q} for q in result.sub_questions]
    
    return {
        "sub_questions": sq_list,
        "loop_count": loop_count + 1
    }

def search_node(state: SearchNodeState):
    question = state["sub_question"]["question"]
    
    results = search_tool.invoke({"query": question})
    formatted_results = "\n\n".join([f"Source: {r['url']}\nContent: {r['content']}" for r in results])
    
    return {"search_results": [{"question": question, "results": formatted_results}]}

def summarizer_node(state: AgentState):
    sub_questions = [sq["question"] for sq in state["sub_questions"]]
    search_results = state["search_results"]
    
    # Only summarize search results belonging to the current iteration of sub-questions
    current_results = {}
    for res in search_results:
        if res["question"] in sub_questions:
            current_results[res["question"]] = res["results"]
            
    summaries = []
    combined_summary_parts = []
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a research summarizer. Summarize the following search results for the given question. Include inline citations to the sources (URLs) provided in the text. Be concise but comprehensive."),
        ("user", "Question: {question}\n\nSearch Results:\n{results}")
    ])
    
    chain = prompt | llm
    
    for q in sub_questions:
        res_text = current_results.get(q, "No results found.")
        summary = chain.invoke({"question": q, "results": res_text}).content
        summaries.append({"question": q, "summary": summary})
        combined_summary_parts.append(f"### {q}\n{summary}")
        
    combined_summary = "\n\n".join(combined_summary_parts)
    
    return {"summaries": summaries, "combined_summary": combined_summary}

class CriticOutput(BaseModel):
    score: int = Field(description="Score from 1 to 10 for the summary quality.")
    feedback: str = Field(description="Feedback on what is missing or poor in the summary.")
    pass_threshold: bool = Field(description="True if score >= 7, False otherwise.")

def critic_node(state: AgentState):
    topic = state["topic"]
    combined_summary = state["combined_summary"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a critical reviewer. Evaluate the provided research summary for the given topic. Score it from 1 to 10 based on comprehensiveness, clarity, and citations. If the score is below 7, provide specific feedback on what to improve."),
        ("user", "Topic: {topic}\n\nSummary:\n{summary}")
    ])
    
    chain = prompt | llm.with_structured_output(CriticOutput)
    result = chain.invoke({"topic": topic, "summary": combined_summary})
    
    return {
        "critic_score": result.score,
        "critic_feedback": result.feedback
    }

def report_node(state: AgentState):
    topic = state["topic"]
    summaries = state["summaries"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert report writer. Combine the provided findings into a cohesive, professional markdown report.\n\nFormatting requirements:\n- Executive Summary (2-3 sentences)\n- Findings per Sub-question (one section each, with bullet points, using H2 headers)\n- Citations (inline links from the provided URLs)\n- Conclusion (synthesized takeaway)\n- DO NOT include a Limitations section.\n- Keep styling clean with horizontal rules (---) between major sections."),
        ("user", "Topic: {topic}\n\nFindings:\n{findings}")
    ])
    
    findings_text = "\n\n".join([f"Question: {s['question']}\nSummary: {s['summary']}" for s in summaries])
    
    chain = prompt | llm
    report = chain.invoke({"topic": topic, "findings": findings_text}).content
    
    return {"report": report}
