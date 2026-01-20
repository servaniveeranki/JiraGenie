

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
from pathlib import Path

# Import AI service (NOT from router to avoid circular imports)
from ai_service import run_ai_analysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="JIRA Ticket Generator",
    description="AI-powered JIRA ticket generation from requirements",
    version="2.0.0"
)

# ============================================
# CRITICAL FIX #1: ADD CORS BEFORE ROUTERS
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        
        # Production Vercel deployments
        "https://jira-genie.vercel.app",
        "https://jira-genie-git-main-sofias-projects-ec574c4e.vercel.app",
        
        # Allow all Vercel preview deployments
        "https://jira-genie-*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ============================================
# INCLUDE ROUTERS AFTER CORS
# ============================================
from jira_router import router as jira_router
app.include_router(jira_router)

# ============================================
# PYDANTIC MODELS
# ============================================
class TicketGenerationResponse(BaseModel):
    message: str
    stats: dict
    aiOutput: dict

# ============================================
# ROUTES
# ============================================
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "JIRA Ticket Generator API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "generate_tickets": "/api/generate-tickets",
            "jira_create_from_file": "/api/jira/create-from-file",
            "jira_create_tickets": "/api/jira/create-tickets"
        }
    }

@app.get("/health")
async def health_check():
    """Health check for deployment platforms"""
    return {"status": "healthy", "service": "jira-ticket-generator"}

@app.post("/api/generate-tickets", response_model=TicketGenerationResponse)
async def generate_tickets(
    files: List[UploadFile] = File(...),
    customPrompt: Optional[str] = Form(None)
):
    """
    Generate JIRA tickets from requirements files (text and/or images) with optional custom prompt
    
    This endpoint:
    1. Accepts multiple files (text and images)
    2. Analyzes them with AI
    3. Returns structured ticket data (does NOT create in JIRA)
    
    For direct JIRA creation, use /api/jira/create-from-file instead
    """
    try:
        requirements_text = ""
        image_bytes_list = []
        
        logger.info('=== FILES RECEIVED ===')
        
        # Process all uploaded files
        for file in files:
            content = await file.read()
            
            # Check if it's a text file
            if file.filename.endswith('.txt'):
                requirements_text += content.decode('utf-8') + "\n\n"
                logger.info(f"Text file: {file.filename}")
            # Otherwise treat as image
            else:
                image_bytes_list.append(content)
                logger.info(f"Image file: {file.filename} ({len(content)} bytes)")
        
        if not requirements_text.strip() and not image_bytes_list:
            raise HTTPException(
                status_code=400,
                detail="No requirements found. Please upload at least one .txt file or image file."
            )
        
        # If only images are uploaded, provide a default text for requirements
        if not requirements_text.strip():
            requirements_text = (
                "No text requirements provided. Please analyze the following architecture diagrams "
                "and generate all possible epics, stories, and subtasks based on the images."
            )
        
        # Call AI analysis with custom prompt if provided
        logger.info('=== STARTING AI ANALYSIS ===')
        if customPrompt:
            logger.info("Using custom prompt")
        
        structured_data = await run_ai_analysis(
            requirements_text, 
            image_bytes_list if image_bytes_list else None,
            customPrompt
        )
        
        # Log partitions
        logger.info('=== AI ANALYSIS COMPLETE ===')
        if structured_data.get('epics'):
            epics_count = len(structured_data['epics'])
            logger.info(f"Found {epics_count} Epics")
            
            total_stories = 0
            total_subtasks = 0
            
            for i, epic in enumerate(structured_data['epics']):
                logger.info(f"  [Epic {i+1}] {epic.get('summary', 'No summary')}")
                if epic.get('stories'):
                    stories_count = len(epic['stories'])
                    total_stories += stories_count
                    logger.info(f"    -> Contains {stories_count} Stories")
                    
                    # Count subtasks
                    for story in epic['stories']:
                        if story.get('subtasks'):
                            total_subtasks += len(story['subtasks'])
            
            logger.info(f"Total: {epics_count} Epics, {total_stories} Stories, {total_subtasks} Subtasks")
        else:
            logger.warning("No 'epics' array found in AI response")
        
        # Calculate stats
        epics_count = len(structured_data.get('epics', []))
        total_stories_count = sum(
            len(epic.get('stories', []))
            for epic in structured_data.get('epics', [])
        )
        total_subtasks_count = sum(
            len(story.get('subtasks', []))
            for epic in structured_data.get('epics', [])
            for story in epic.get('stories', [])
        )
        
        # Return response
        return TicketGenerationResponse(
            message="Requirements analyzed successfully!",
            stats={
                "epics": epics_count,
                "stories": total_stories_count,
                "subtasks": total_subtasks_count,
                "imagesProcessed": len(image_bytes_list)
            },
            aiOutput=structured_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /api/generate-tickets: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Server error during analysis: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )