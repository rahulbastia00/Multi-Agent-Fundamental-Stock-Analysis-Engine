from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.services.agent import create_agent_executor
import json

router = APIRouter()

class AnalysisRequest(BaseModel):
    ticker: str
    query: str = "Run a full financial analysis."

agent_executor = create_agent_executor()

@router.post("/analyze", status_code=200)
async def analyze_ticker(request: AnalysisRequest):
    """
    Receives a ticker and runs the financial analysis agent.
    """
    try:
        input_data = {"input": f"Analyze the company with ticker {request.ticker}. {request.query}"}
        
        result = await agent_executor.ainvoke(input_data)
        
        output_str = result.get('output', '{}')

        # --- FIX: Handle cases where the agent's output is not valid JSON ---
        try:
            # Try to parse the output as a JSON object
            output_json = json.loads(output_str)
            return output_json
        except json.JSONDecodeError:
            # If parsing fails, return the raw string output in a structured way
            return {"message": "Agent finished with a non-JSON response.", "output": output_str}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run analysis: {str(e)}")
