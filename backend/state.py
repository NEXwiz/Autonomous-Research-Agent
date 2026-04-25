import operator
from typing import Annotated, List, TypedDict

class SubQuestion(TypedDict):
    question: str

class SearchResult(TypedDict):
    question: str
    results: str

class SubQuestionSummary(TypedDict):
    question: str
    summary: str

class AgentState(TypedDict):
    topic: str
    sub_questions: List[SubQuestion]
    # Aggregates results from parallel search nodes
    search_results: Annotated[List[SearchResult], operator.add]
    summaries: List[SubQuestionSummary]
    combined_summary: str
    critic_score: int
    critic_feedback: str
    report: str
    loop_count: int

class SearchNodeState(TypedDict):
    sub_question: SubQuestion
