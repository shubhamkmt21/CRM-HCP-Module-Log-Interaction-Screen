🧠 AI-First CRM – HCP Interaction Module
📌 Overview
This project is an AI-powered CRM module designed for medical sales representatives to log and manage interactions with Healthcare Professionals (HCPs).

It allows users to:

Log interactions via structured form
Log interactions via AI chat interface
Automatically extract and store key details using an LLM
🚀 Features
📋 Form-based interaction logging
💬 AI chat → structured data conversion
✏️ Edit interaction records
📊 View interaction history
🧠 AI-generated summaries & insights
🏗️ Tech Stack
Frontend: React + Redux
Backend: FastAPI (Python)
AI Framework: LangGraph
LLM: Groq (gemma2-9b-it)
Database: MySQL / PostgreSQL
Styling: Google Inter Font
⚙️ System Architecture
User (Form/Chat)
        ↓
React + Redux (Frontend)
        ↓
FastAPI (Backend API)
        ↓
LangGraph Agent
        ↓
Groq LLM (gemma2-9b-it)
        ↓
Database (MySQL/Postgres)
🧩 LangGraph Tools Implemented
Log Interaction – Stores interaction data using AI extraction
Edit Interaction – Updates existing records
Get Interaction History – Fetch past interactions
Summarize Interaction – Generates concise summaries
Suggest Follow-up – Recommends next actions
🔑 Setup Instructions
1. Clone Repository
git clone https://github.com/your-username/ai-crm-hcp-module.git
cd ai-crm-hcp-module
2. Backend Setup
cd backend
pip install -r requirements.txt
Create .env file:

GROQ_API_KEY=your_api_key_here
DATABASE_URL=your_database_url
Run server:

uvicorn main:app --reload
3. Frontend Setup
cd frontend
npm install
npm start
4. Database Setup
Create MySQL/PostgreSQL database
Add table:
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    hcp_name VARCHAR(255),
    date DATE,
    time TIME,
    notes TEXT,
    product VARCHAR(255),
    sentiment VARCHAR(50),
    summary TEXT
);
🧪 Example Usage
Chat Input:
Met Dr. Patel, discussed insulin, he was positive.
AI Output:
{
  "hcp_name": "Dr. Patel",
  "product": "Insulin",
  "sentiment": "Positive"
}
