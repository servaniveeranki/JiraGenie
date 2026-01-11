from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
from jira_service import JiraService
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

router = APIRouter(prefix="/api/jira", tags=["Jira Integration"])

# Initialize Jira Service (may be None if JIRA credentials not configured)
try:
    jira_service = JiraService()
    if not jira_service._is_configured():
        logger = logging.getLogger(__name__)
        logger.warning("JIRA service initialized but not configured. JIRA endpoints will return errors.")
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to initialize JIRA service: {str(e)}")
    jira_service = None

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
        
        if not jira_service or not jira_service._is_configured():
            return JiraCreateResponse(
                success=False,
                message="JIRA service is not configured. Please set JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, and JIRA_PROJECT_KEY in the .env file.",
                created_issues={},
                errors=["JIRA credentials not configured"]
            )
        
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

@router.post("/create-from-file", response_model=JiraCreateResponse)
async def create_jira_tickets_from_file(
    files: List[UploadFile] = File(...),
    customPrompt: Optional[str] = None
):
    """
    Directly create JIRA tickets from requirements file - independent flow
    Processes requirements, analyzes with AI, and creates tickets in one step
    """
    logger = logging.getLogger(__name__)
    try:
        if not jira_service or not jira_service._is_configured():
            return JiraCreateResponse(
                success=False,
                message="JIRA service is not configured. Please set JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN, and JIRA_PROJECT_KEY in the .env file.",
                created_issues={},
                errors=["JIRA credentials not configured"]
            )
        
        logger.info("Starting direct Jira ticket creation from file...")
        
        # Read requirements file
        requirements_text = ""
        image_bytes_list = []
        for file in files:
            if file.filename.endswith('.txt'):
                content = await file.read()
                requirements_text += content.decode('utf-8') + "\n\n"
            else:
                image_bytes_list.append(await file.read())
        
        if not requirements_text.strip() and not image_bytes_list:
            raise HTTPException(status_code=400, detail="No requirements found. Please upload at least one .txt file or image file.")
        if not requirements_text.strip():
            requirements_text = (
                "The following upload contains only architecture diagrams or images. "
                "Analyze these diagrams carefully and extract ALL possible EPICS, STORIES, and SUBTASKS that could be inferred from the system, workflows, modules, integrations, or features depicted. "
                "If there are swimlanes, modules, or components, treat them as potential epics or stories. "
                "For each, provide a summary, description, and any subtasks that can be logically deduced. "
                "If you cannot extract anything, return an empty epics array."
            )
        
        # Run AI analysis (reuse run_ai_analysis from main.py for consistency)
        logger.info("Running AI analysis on requirements...")
        try:
            from main import run_ai_analysis
        except ImportError:
            raise HTTPException(status_code=500, detail="Server misconfiguration: cannot import run_ai_analysis")
        structured_data = await run_ai_analysis(requirements_text, image_bytes_list if image_bytes_list else None, customPrompt)
        logger.info(f"AI analysis complete. Found {len(structured_data.get('epics', []))} epics")
        
        # Create tickets directly
        logger.info("Creating tickets in Jira...")
        result = await jira_service.create_issues(structured_data)
        
        if result['errors']:
            return JiraCreateResponse(
                success=False,
                message=f"Created {len(result['epics'])} epics, {len(result['stories'])} stories, {len(result['subtasks'])} subtasks. Some issues had errors.",
                created_issues={
                    'epics': result['epics'],
                    'stories': result['stories'],
                    'subtasks': result['subtasks']
                },
                errors=result['errors']
            )
        
        return JiraCreateResponse(
            success=True,
            message=f"Successfully created {len(result['epics'])} epics, {len(result['stories'])} stories, and {len(result['subtasks'])} subtasks in Jira!",
            created_issues={
                'epics': result['epics'],
                'stories': result['stories'],
                'subtasks': result['subtasks']
            }
        )
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse AI response: {str(e)}"
        logger.error(error_msg)
        return JiraCreateResponse(
            success=False,
            message=error_msg,
            created_issues={},
            errors=[error_msg]
        )
    except Exception as e:
        error_msg = f"Failed to create JIRA tickets from file: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return JiraCreateResponse(
            success=False,
            message=error_msg,
            created_issues={},
            errors=[error_msg]
        )
