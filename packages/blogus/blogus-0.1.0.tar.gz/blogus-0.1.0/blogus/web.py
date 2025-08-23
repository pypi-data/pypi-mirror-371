"""
Web interface for Blogus using FastAPI.
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import re
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from blogus.core import (
    TargetLLMModel,
    JudgeLLMModel,
    Fragment,
    Log,
    Test,
    PromptAnalysis,
    get_llm_response,
    infer_goal,
    analyze_fragments,
    analyze_logs,
    analyze_prompt,
    generate_test,
    execute_prompt,
)

app = FastAPI()

# Mount static files and templates
static_dir = os.path.join(os.path.dirname(__file__), "..", "app", "static")
templates_dir = os.path.join(os.path.dirname(__file__), "..", "app", "templates")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)


# Request models
class FragmentAnalysisRequest(BaseModel):
    prompt: str
    target_model: TargetLLMModel
    judge_model: JudgeLLMModel
    goal: Optional[str] = None

class FragmentResponse(BaseModel):
    text: str
    type: str
    goal_alignment: int
    improvement_suggestion: str

class LogResponse(BaseModel):
    type: str
    message: str

class PromptAnalysisRequest(BaseModel):
    prompt: str
    target_model: TargetLLMModel
    judge_model: JudgeLLMModel
    goal: Optional[str] = None

class PromptAnalysisResponse(BaseModel):
    overall_goal_alignment: int
    suggested_improvements: List[str]
    estimated_effectiveness: int
    inferred_goal: Optional[str] = None
    is_goal_inferred: bool

class TestGenerationRequest(BaseModel):
    prompt: str
    target_model: TargetLLMModel
    judge_model: JudgeLLMModel
    goal: Optional[str] = None

class TestResponse(BaseModel):
    input: Dict[str, str]
    expected_output: str
    goal_relevance: int

class PromptExecutionRequest(BaseModel):
    prompt: str
    target_model: TargetLLMModel

class GoalInferenceRequest(BaseModel):
    prompt: str
    judge_model: JudgeLLMModel


@app.post("/api/infer-goal", response_model=str)
async def infer_goal_endpoint(request: GoalInferenceRequest):
    try:
        return infer_goal(request.prompt, request.judge_model).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-fragments", response_model=List[FragmentResponse])
async def analyze_fragments_endpoint(request: FragmentAnalysisRequest):
    try:
        fragments = analyze_fragments(request.prompt, request.judge_model, request.goal)
        return [
            FragmentResponse(
                text=f.text,
                type=f.type,
                goal_alignment=f.goal_alignment,
                improvement_suggestion=f.improvement_suggestion,
            )
            for f in fragments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-logs", response_model=List[LogResponse])
async def analyze_logs_endpoint(request: PromptAnalysisRequest):
    try:
        logs = analyze_logs(request.prompt, request.judge_model, request.goal)
        return [LogResponse(type=l.type, message=l.message) for l in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-prompt", response_model=PromptAnalysisResponse)
async def analyze_prompt_endpoint(request: PromptAnalysisRequest):
    try:
        analysis = analyze_prompt(request.prompt, request.judge_model, request.goal)
        return PromptAnalysisResponse(
            overall_goal_alignment=analysis.overall_goal_alignment,
            suggested_improvements=analysis.suggested_improvements,
            estimated_effectiveness=analysis.estimated_effectiveness,
            inferred_goal=analysis.inferred_goal,
            is_goal_inferred=analysis.is_goal_inferred,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-test", response_model=TestResponse)
async def generate_test_endpoint(request: TestGenerationRequest):
    try:
        test_case = generate_test(request.prompt, request.judge_model, request.goal)
        return TestResponse(
            input=test_case.input,
            expected_output=test_case.expected_output,
            goal_relevance=test_case.goal_relevance,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute-prompt", response_model=str)
async def execute_prompt_endpoint(request: PromptExecutionRequest):
    try:
        return execute_prompt(request.prompt, request.target_model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def index(request: Request):
    if os.path.exists(templates_dir):
        return templates.TemplateResponse("index.html", {"request": request})
    return {"message": "Logus API is running. Visit /docs for API documentation."}


@app.get("/agent")
async def agent(request: Request):
    if os.path.exists(templates_dir):
        return templates.TemplateResponse("agent.html", {"request": request})
    return {"message": "Logus Agent Interface. Visit /docs for API documentation."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
