from langchain_groq import ChatGroq
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain import hub
from langchain.tools.render import render_text_description # <-- IMPORT the tool renderer
from sqlalchemy.orm import Session
from src.services.analysis import calculate_financial_ratios
from src.db.session import SessionLocal
from src.core.config import settings
import json

@tool
def financial_analyzer_tool(ticker: str) -> str:
    """
    Calculates key financial ratios (P/E, P/B, ROE, Altman Z-Score) for a given stock ticker.
    Returns the analysis as a JSON string. This is the primary tool for financial analysis.
    """
    db: Session = SessionLocal()
    try:
        ratios = calculate_financial_ratios(db, ticker=ticker)
        return json.dumps(ratios)
    finally:
        db.close()

def create_agent_executor():
    """
    Creates and returns a LangChain agent executor using Groq.
    """
    print(f"--- [DEBUG] Using Groq API Key: {settings.GROQ_API_KEY[:5]}...{settings.GROQ_API_KEY[-4:]} ---")
    
    llm = ChatGroq(
        temperature=0.6,
        model_name="llama3-8b-8192",
        groq_api_key=settings.GROQ_API_KEY
    )
    
    tools = [financial_analyzer_tool]
    
    # --- FIX: Manually render the tools for the prompt ---
    # 1. Pull the base prompt from the hub
    prompt = hub.pull("hwchase17/react")
    
    # 2. Render the tool descriptions into the format the prompt expects
    rendered_tools = render_text_description(tools)
    
    # 3. Partially format the prompt with the rendered tools
    prompt = prompt.partial(
        tools=rendered_tools,
        tool_names=", ".join([t.name for t in tools]),
    )
    
    # --- FIX: Bind stop sequences and pass the updated prompt ---
    agent = create_react_agent(llm.bind(stop=["\nObservation"]), tools, prompt)
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor
