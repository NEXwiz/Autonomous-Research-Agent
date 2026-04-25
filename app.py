import streamlit as st
from agent import graph
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="GenAI Autonomous Research Assistant", layout="wide")

st.title("🧠 GenAI Autonomous Research Assistant")
st.markdown("This multi-agent system uses LangGraph to autonomously plan, search, summarize, and critique research on any topic.")

topic = st.text_input("Enter a research topic:", placeholder="e.g. The impact of quantum computing on cryptography")

if st.button("Start Research"):
    if not topic:
        st.warning("Please enter a topic.")
    elif not os.getenv("GOOGLE_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        st.error("Please ensure GOOGLE_API_KEY and TAVILY_API_KEY are set in the .env file.")
    else:
        st.info("Starting multi-agent workflow...")
        
        status_placeholder = st.empty()
        
        config = {"configurable": {"thread_id": "1"}}
        
        with st.spinner("Agents are working..."):
            # Initialize state with an empty list for search results
            initial_state = {"topic": topic, "search_results": []}
            
            for event in graph.stream(initial_state, config=config):
                for node, state in event.items():
                    if node == "planner_node":
                        status_placeholder.markdown(f"**Planner Agent:** Generated sub-questions. (Loop {state.get('loop_count', 1)})")
                        with st.expander(f"View Sub-questions (Loop {state.get('loop_count', 1)})"):
                            for sq in state.get('sub_questions', []):
                                st.write(f"- {sq['question']}")
                    elif node == "summarizer_node":
                        status_placeholder.markdown("**Summarizer Agent:** Synthesizing search results...")
                    elif node == "critic_node":
                        score = state.get("critic_score")
                        feedback = state.get("critic_feedback")
                        st.markdown(f"**Critic Agent:** Scored {score}/10. Feedback: {feedback}")
                        if score and score < 7:
                            st.warning("Quality below threshold. Retrying loop...")
                    elif node == "report_node":
                        status_placeholder.markdown("**Report Agent:** Formatting final report...")
                        st.success("Research Complete!")
                        st.markdown("---")
                        st.markdown(state.get("report", ""))
