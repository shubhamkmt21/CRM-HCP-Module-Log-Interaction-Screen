import os
from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from database import SessionLocal
from models import Interaction

@tool
def log_interaction(hcp_name: str, interaction_type: str, notes: str, interaction_date: str = None, interaction_time: str = None, attendees: str = None, materials_shared: str = None, samples_distributed: str = None, sentiment: str = None, outcomes: str = None, action_items: str = None) -> str:
    """Logs a new interaction with a Healthcare Professional (HCP)."""
    db = SessionLocal()
    try:
        interaction = Interaction(
            hcp_name=hcp_name,
            interaction_type=interaction_type,
            interaction_date=interaction_date,
            interaction_time=interaction_time,
            attendees=attendees,
            notes=notes,
            materials_shared=materials_shared,
            samples_distributed=samples_distributed,
            sentiment=sentiment,
            outcomes=outcomes,
            action_items=action_items
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return f"Interaction logged successfully with ID {interaction.id}."
    except Exception as e:
        db.rollback()
        return f"Error logging interaction: {str(e)}"
    finally:
        db.close()

@tool
def edit_interaction(interaction_id: str, notes: str = None, action_items: str = None, interaction_type: str = None, sentiment: str = None, outcomes: str = None) -> str:
    """Edits an existing interaction."""
    db = SessionLocal()
    try:
        interaction_id = int(interaction_id)
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return f"Interaction with ID {interaction_id} not found."
        
        if notes:
            interaction.notes = notes
        if action_items:
            interaction.action_items = action_items
        if interaction_type:
            interaction.interaction_type = interaction_type
        if sentiment:
            interaction.sentiment = sentiment
        if outcomes:
            interaction.outcomes = outcomes
            
        db.commit()
        return f"Interaction {interaction_id} updated successfully."
    except Exception as e:
        db.rollback()
        return f"Error updating interaction: {str(e)}"
    finally:
        db.close()

@tool
def list_interactions(limit: str = "5") -> str:
    """Lists the most recent interactions to view history."""
    db = SessionLocal()
    try:
        limit = int(limit)
        interactions = db.query(Interaction).order_by(Interaction.timestamp.desc()).limit(limit).all()
        if not interactions:
            return "No interactions found."
        
        result = "Recent Interactions:\n"
        for i in interactions:
            result += f"- ID: {i.id} | HCP: {i.hcp_name} | Date: {i.interaction_date} | Type: {i.interaction_type} | Sentiment: {i.sentiment}\n"
        return result
    finally:
        db.close()

@tool
def summarize_notes(interaction_id: str) -> str:
    """Summarizes the notes for a specific interaction ID."""
    db = SessionLocal()
    try:
        interaction_id = int(interaction_id)
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return f"Interaction with ID {interaction_id} not found."
        if not interaction.notes:
            return "No notes found for this interaction."
        return f"Notes for {interaction.hcp_name}: {interaction.notes}"
    finally:
        db.close()

@tool
def suggest_next_action(interaction_id: str) -> str:
    """Suggests the next action for a specific interaction based on its details."""
    db = SessionLocal()
    try:
        interaction_id = int(interaction_id)
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return f"Interaction with ID {interaction_id} not found."
        
        return f"Interaction Details for {interaction.hcp_name}:\nMaterials: {interaction.materials_shared}\nSamples: {interaction.samples_distributed}\nNotes: {interaction.notes}\nCurrent Action Items: {interaction.action_items}"
    finally:
        db.close()

tools = [log_interaction, edit_interaction, list_interactions, summarize_notes, suggest_next_action]

from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def build_graph():
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: AgentState):
        messages = state['messages']
        response = llm_with_tools.invoke(messages)
        print("--- MODEL INVOKED ---")
        if hasattr(response, 'tool_calls'):
            print("Tool Calls:", response.tool_calls)
        else:
            print("Content:", response.content)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    
    def should_continue(state: AgentState):
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()

try:
    graph = build_graph()
except Exception as e:
    graph = None
    print(f"Warning: Failed to initialize graph. {e}")

def run_chat_agent(user_message: str, db_session=None) -> str:
    if not os.environ.get("GROQ_API_KEY"):
        # Mock behavior for demo purposes when key is missing
        if "log" in user_message.lower() or "met" in user_message.lower():
            db = SessionLocal()
            from models import Interaction
            interaction = Interaction(
                hcp_name="Dr. Smith (Mock)",
                interaction_type="In-Person",
                notes=user_message,
                action_items="Follow up next week",
                samples_distributed="Insulin Mock Sample"
            )
            db.add(interaction)
            db.commit()
            db.close()
            return "Mock AI: I've logged the interaction with Dr. Smith for you. (Please add GROQ_API_KEY to use the real LangGraph AI)."
        return "Mock AI: Please set GROQ_API_KEY environment variable in backend/.env to use the real LangGraph AI."
        
    system_prompt = (
        "You are a professional AI assistant for medical sales reps. Your job is to help them log, edit, and manage interactions with Healthcare Professionals (HCPs). "
        "Call the appropriate tools to fulfill their requests. Always structure your responses cleanly. "
        "IMPORTANT RULES:\n"
        "1. When a user logs a new interaction, do NOT dump a list of all past interactions into the chat. Instead, strictly reply with: "
        "'Your interaction with [HCP Name] has been logged and all the details have been automatically populated based on your summary. Would you like to summarize the notes or suggest the next action for this interaction?'\n"
        "2. Don't invent IDs. Only use `list_interactions` if the user explicitly asks to view their history or if you need to find a specific ID to fulfill a user's direct request.\n"
        "3. When a user asks you to summarize notes or suggest an action, call the corresponding tool and then IMMEDIATELY reply to the user with the result. Do NOT call `edit_interaction` to save your summary or suggestions unless explicitly told to do so. Just present the information professionally."
    )
    
    inputs = {"messages": [("system", system_prompt), ("user", user_message)]}
    
    # Run graph
    try:
        if not graph:
            return "Mock AI: LangGraph failed to initialize (likely missing GROQ_API_KEY). Please check the server logs."
        config = {"recursion_limit": 10}
        result = graph.invoke(inputs, config)
        return result['messages'][-1].content
    except Exception as e:
        return f"An error occurred: {str(e)}"
