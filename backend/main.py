from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import json
import asyncio
from agent import graph
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GenAI Autonomous Research API")

# Configure CORS to allow our React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    topic: str

@app.post("/api/research")
async def start_research(req: ResearchRequest):
    topic = req.topic
    
    async def event_generator():
        initial_state = {"topic": topic, "search_results": []}
        config = {"configurable": {"thread_id": "1"}}
        
        # Stream events from the LangGraph execution
        for event in graph.stream(initial_state, config=config):
            for node, state in event.items():
                
                # Extract only necessary display data for the UI
                data = {
                    "node": node,
                    "loop_count": state.get("loop_count", 1),
                    "sub_questions": state.get("sub_questions", []),
                    "critic_score": state.get("critic_score"),
                    "critic_feedback": state.get("critic_feedback"),
                    "report": state.get("report")
                }
                
                yield {
                    "event": "message",
                    "data": json.dumps(data)
                }
                await asyncio.sleep(0.01) # Yield control loop

    return EventSourceResponse(event_generator())
