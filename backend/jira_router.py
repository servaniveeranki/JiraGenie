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

# Initialize Jira Service
jira_service = JiraService()

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
        logger.info("Starting direct Jira ticket creation from file...")
        
        # Read requirements file
        requirements_text = ""
        for file in files:
            if file.filename.endswith('.txt'):
                content = await file.read()
                requirements_text += content.decode('utf-8') + "\n\n"
        
        if not requirements_text.strip():
            raise HTTPException(status_code=400, detail="No text requirements found. Please upload a .txt file.")
        
        # Run AI analysis
        logger.info("Running AI analysis on requirements...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = customPrompt if customPrompt else os.getenv("SYSTEM_PROMPT", """
Analyze the requirements document and extract ALL EPICS, STORIES, and SUBTASKS into JSON format.

IMPORTANT INSTRUCTIONS:
1. Extract ALL epics from the requirements (both FUNCTIONAL and NON-FUNCTIONAL categories)
2. For each epic, extract ALL stories listed under it
3. For each story, extract ALL subtasks listed under it
4. Maintain the category information (functional vs non-functional)
5. Preserve the priority levels mentioned in stories
6. Keep the exact structure and hierarchy from the requirements

Output Format:
{
  "epics": [
    {
      "summary": "Epic title from requirements",
      "description": "Epic description from requirements",
      "category": "FUNCTIONAL" or "NON-FUNCTIONAL",
      "stories": [
        {
          "summary": "Story title from requirements",
          "description": "Story description from requirements",
          "priority": "Priority level if mentioned (High/Medium/Low)",
          "subtasks": [
            {
              "summary": "Subtask description from requirements"
            }
          ]
        }
      ]
    }
  ]
}

Return ONLY valid JSON. No additional text or explanations.
""")
        
        content_parts = [system_prompt, "\n\n**Requirements:**\n", requirements_text]
        response = model.generate_content(content_parts)
        
        # Extract JSON
        text = response.text
        cleaned = text.replace("```json", "").replace("```", "").strip()
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_text = cleaned[start_idx:end_idx + 1]
            structured_data = json.loads(json_text)
        else:
            raise HTTPException(status_code=500, detail="AI response was not valid JSON")
        
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
