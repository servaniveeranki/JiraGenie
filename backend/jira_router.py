from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
from jira_service import JiraService

router = APIRouter(prefix="/api/jira", tags=["Jira Integration"])

# Initialize Jira Service
jira_service = JiraService()

class JiraCreateRequest(BaseModel):
    ai_output: Dict[str, Any] = Field(..., description="AI-generated output with epics, stories, and subtasks")

class JiraCreateResponse(BaseModel):
    success: bool
    message: str
    created_issues: Dict[str, List[Dict]]
    errors: List[str] = []

@router.post("/create-tickets", response_model=JiraCreateResponse)
async def create_jira_tickets(request: JiraCreateRequest):
    """
    Create JIRA tickets from the AI-generated output
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info("Starting Jira ticket creation...")
        
        result = await jira_service.create_issues(request.ai_output)
        
        if result['errors']:
            return JiraCreateResponse(
                success=False,
                message="Some issues were not created successfully",
                created_issues={
                    'epics': result['epics'],
                    'stories': result['stories'],
                    'subtasks': result['subtasks']
                },
                errors=result['errors']
            )
        
        return JiraCreateResponse(
            success=True,
            message="All JIRA tickets created successfully",
            created_issues={
                'epics': result['epics'],
                'stories': result['stories'],
                'subtasks': result['subtasks']
            }
        )
    except Exception as e:
        error_msg = f"Failed to create JIRA tickets: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return JiraCreateResponse(
            success=False,
            message=error_msg,
            created_issues={},
            errors=[error_msg]
        )
