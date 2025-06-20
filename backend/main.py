import uuid
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from .agent import get_graph
from .ticket import models
from .ticket.database import engine
from .ticket.routers import ticket

app = FastAPI(
    title="Agentic Ticket System",
    description="Agent that gets user input and creates a new ticket in ticket DB",
)

app.include_router(ticket.router)
models.Base.metadata.create_all(engine)

class ChatRequest(BaseModel):
    message: str
    thread_id: str

graph = get_graph()

@app.post("/chat", tags=["Agent"])
async def chat(request: ChatRequest):

    async def stream_tokens():

        config = {"configurable": {"thread_id": request.thread_id}}

        for chunk_type, data in graph.stream(
            {"messages": [HumanMessage(content=request.message)]},
            config,
            stream_mode=["messages", "updates"]
        ):
            if chunk_type == "messages":
                msg_obj, metadata = data
                if msg_obj.type != 'tool':
                    yield msg_obj.content
            elif chunk_type == "updates":
                if agent_msg := data.get("info"):
                    msg_obj = agent_msg["messages"][0]
                elif tools_msg := data.get("add_tool_message"):
                    msg_obj = tools_msg["messages"][0]
                elif tools_msg := data.get("create_ticket"):
                    msg_obj = tools_msg["messages"][0]
                elif confirmation_msg := data.get("confirmation"):
                    msg_obj = confirmation_msg["messages"][0]
                else:
                    print('penguin')
                    continue

                msg_obj.pretty_print()
                # yield msg_obj.content
                
    return StreamingResponse(stream_tokens(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)