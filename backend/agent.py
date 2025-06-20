import httpx
from uuid import uuid4
from pydantic import BaseModel
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langchain_core.tools import tool, InjectedToolCallId
from .ticket.routers.ticket import add
from .ticket.database import get_db
from sqlalchemy.orm import Session
from fastapi.params import Depends



from .llm import get_llm

llm = get_llm()

class Ticket(BaseModel):
    ticket_id: str
    name: str
    email: str
    problem_description: str
    category: str


class State(TypedDict):
    messages: Annotated[list, add_messages]
    ticket: Ticket

def get_state(state):
    messages = state["messages"]
    if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        return "create_ticket"
    elif not isinstance(messages[-1], HumanMessage):
        return END
    return "info"

def get_graph():

    template = """
        You are the IT Ticket Chatbot, a helpful assistant that creates IT support tickets for users.
        You refuse to answer questions or provide support for any other topics.
        You always respond in German.
        
        Step 1: Information Collection
        - Collect the following three pieces of information from the user—in any order:
            1. Email address
            2. Name
            3. Problem description
        - **Rules:**
            - If this information is already included in the user's first message or anywhere else in the chat history, do not ask again.
            - If information is missing or unclear, ask specifically for it.
            - NEVER guess and do NOT make up any information.
            - Only ask for these three pieces of information—nothing more.
            - If and only if the user explicitly mentions the word "Notfall" (case-insensitive) in their input, immediately assign the default values to Name: "Name wird später nachgereicht, da es sich um einen Notfall handelt." and Email: "Email wird später nachgereicht, da es sich um einen Notfall handelt." and continue with Step 2.
            - If the user does not explicitly say the word "Notfall" (case-insensitive) ask for the missing information like an Email and a Name.

        Step 2: Problem Classification
        - Analyze the problem description provided by the user and attempt to derive a Category based on these valid options:
            - If the problem description mentions "Account management", "Login", "Sign in", "Forgot Email or password" or anything related to their Account:
                - Category: Account Management
            - If the problem description mentions "Software":
                - Category: Software
            - If the problem description mentions "Hardware":
                - Category: Hardware
            - If the problem description mentions "printers" or "printing" or anything related to printers:
                - Category: Printer
            - If the problem description mentions "Performance":
                - Category: Performance
            - If the problem description mentions "Network Security" or anything related to security:
                - Category: Security
            - If the problem description does not clearly fall into any of these categories, set the Category to "Help Desk Support".

        Final Step: Ticket Creation
        - Once all the required information (Name, Email address, Problem description, Category) is complete, call the relevant tool to create the IT support ticket.
        - Do not ask for confirmation before calling the tool.
    """

    def get_messages_info(messages):
        return [SystemMessage(content=template)] + messages

    @tool(parse_docstring=True)
    def create_ticket_tool(name: str, email: str, problem_description: str, category: str, tool_call_id: Annotated[str, InjectedToolCallId],) -> Ticket:
        """
        Creates an IT support ticket

        Args:
            name: The users name
            email: The users email
            problem_description: The users problem description
            category: The ticket category

        Return: The newly created ticket.
        """

        
        # this is the place where we want to call the API of our ticketing system.
        # for this demo we simply create a UUID and return a dummy ticket
        ticket = Ticket(
            ticket_id=str(uuid4()),
            name=name,
            email=email,
            problem_description=problem_description,
            category=category,
        )
        db = next(get_db())
        new_ticket = add(request=ticket, db=db)
        
        return Command(update={
            "ticket": new_ticket,
            "messages": [
                ToolMessage("Successfully created ticket", tool_call_id=tool_call_id)
        ]
        })


    llm_with_tool = llm.bind_tools([create_ticket_tool])

    def info_chain(state):
        messages = get_messages_info(state["messages"])
        response = llm_with_tool.invoke(messages)
        return {"messages": [response]}
    
    def confirmation(state):

        ticket: Ticket = state["ticket"]

        return {"messages": [AIMessage(content=f"""
            Ok, Ich habe folgendes Ticket für dich angelegt:
                                       
            - Ticket ID: **{ticket.ticket_id}** 
            - Beschreibung: **{ticket.problem_description}**
            - Kategorie: **{ticket.category}**
            - Nutzername: **{ticket.name}**
            - Nutzer E-Mail: **{ticket.email}**
            
            Unser Support Team ist informiert und wird dich so schnell wie möglich kontaktieren."""
        )]}

    memory = MemorySaver()
    workflow = StateGraph(State)
    workflow.add_node("info", info_chain)
    workflow.add_node("create_ticket", ToolNode([create_ticket_tool]))
    workflow.add_node("confirmation", confirmation)

    workflow.set_entry_point("info")
    workflow.add_conditional_edges("info", get_state, ["create_ticket", "info", END])
    workflow.add_edge("create_ticket", "confirmation")
    workflow.add_edge("confirmation", END)

    graph = workflow.compile(checkpointer=memory)
    return graph