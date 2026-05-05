import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models, schemas, agent
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI CRM API"}

@app.post("/interactions/", response_model=schemas.Interaction)
def create_interaction(interaction: schemas.InteractionCreate, db: Session = Depends(get_db)):
    db_interaction = models.Interaction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@app.get("/interactions/", response_model=List[schemas.Interaction])
def read_interactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    interactions = db.query(models.Interaction).offset(skip).limit(limit).all()
    return interactions

@app.put("/interactions/{interaction_id}", response_model=schemas.Interaction)
def update_interaction(interaction_id: int, interaction: schemas.InteractionUpdate, db: Session = Depends(get_db)):
    db_interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    update_data = interaction.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_interaction, key, value)
        
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@app.post("/chat/", response_model=schemas.ChatResponse)
def chat_with_agent(chat_request: schemas.ChatRequest, db: Session = Depends(get_db)):
    response = agent.run_chat_agent(chat_request.message, db)
    return {"response": response}

@app.post("/extract/")
def extract_form_data(chat_request: schemas.ChatRequest):
    # Endpoint to use LLM to parse text into form fields
    from langchain_groq import ChatGroq
    from pydantic import BaseModel, Field
    import os
    
    class FormExtraction(BaseModel):
        hcp_name: str = Field(default="", description="Name of the Healthcare Professional")
        interaction_type: str = Field(default="Meeting", description="Type of interaction: Meeting, Virtual, Email, or Call")
        interaction_date: str = Field(default="", description="Date of interaction in YYYY-MM-DD format")
        interaction_time: str = Field(default="", description="Time of interaction in HH:MM format")
        attendees: str = Field(default="", description="Other attendees")
        notes: str = Field(default="", description="Main topics discussed or notes")
        materials_shared: str = Field(default="", description="Materials shared")
        samples_distributed: str = Field(default="", description="Samples distributed")
        sentiment: str = Field(default="Neutral", description="Observed sentiment: Positive, Neutral, or Negative")
        outcomes: str = Field(default="", description="Key outcomes")
        action_items: str = Field(default="", description="Follow-up actions or action items")

    if not os.environ.get("GROQ_API_KEY"):
        return FormExtraction().dict()

    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
        structured_llm = llm.with_structured_output(FormExtraction)
        result = structured_llm.invoke(f"Extract the interaction details from the following text to populate a CRM form. If a field is not mentioned, leave it empty or use the default. Text: {chat_request.message}")
        return result.dict()
    except Exception as e:
        print(f"Extraction error: {e}")
        return FormExtraction().dict()
