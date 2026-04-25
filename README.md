# 🧠 GenAI Autonomous Research Assistant

An autonomous multi-agent system built with **LangGraph**, **Google Gemini**, and **Streamlit** that takes any research topic, breaks it down, searches the web, synthesizes findings, and critiques its own output to produce a structured markdown report.

## 🌟 Features

- **Multi-Agent Workflow**: Utilizes specialized agents (Planner, Search, Summarizer, Critic, and Report) to ensure high-quality research.
- **Parallel Processing**: Employs LangGraph's `Send` API to execute web searches and summarize sub-topics concurrently, vastly improving speed.
- **Self-Correction (Critic Node)**: Analyzes the synthesized summary and re-triggers the research loop (up to 3 times) if the quality score falls below the threshold.
- **Clean UI**: Streamlit-based interface that provides real-time logs of the agents' progress and neatly renders the final Markdown report.

## 🏗️ Architecture

1. **Planner Agent**: Uses Gemini's structured output to break the main topic into 3–5 specific sub-questions.
2. **Search Agent**: Uses Tavily Search API to independently fetch web results for each sub-question in parallel.
3. **Summarizer Agent**: Condenses the raw search results and adds inline URL citations.
4. **Critic Agent**: Reviews the combined summary, scoring it out of 10. If the score is below 7, it feeds feedback back to the Planner for another loop.
5. **Report Agent**: Formats the final, approved findings into a cohesive, professional markdown report.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A Google Gemini API Key
- A Tavily Search API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/NEXwiz/Autonomous-Research-Agent.git
   cd Autonomous-Research-Agent
   ```

2. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**
   Rename `.env.example` to `.env` and add your API keys:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

### Usage

Run the Streamlit application:
```bash
streamlit run app.py
```
Open the provided local URL in your browser, enter a topic, and watch the agents go to work!

## 🛠️ Tech Stack

- **Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/)
- **LLM**: [Google Gemini (2.5 Flash)](https://ai.google.dev/)
- **Search**: [Tavily Search API](https://tavily.com/)
- **Frontend**: [Streamlit](https://streamlit.io/)
