from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import base64
from pathlib import Path
import logging
from jira_router import router as jira_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="JIRA Ticket Generator")

# Include Jira router
app.include_router(jira_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Pydantic models
class TicketGenerationResponse(BaseModel):
    message: str
    stats: dict
    aiOutput: dict

# AI Analysis Function
async def run_ai_analysis(requirements_text: str, images: List[bytes] = None, custom_prompt: str = None):
    """
    Analyze requirements using Google Gemini AI
    Supports both text and image inputs
    """
    try:
        # Use gemini-2.5-flash - supports both text and images
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Use custom prompt if provided, otherwise use optimized default
        system_prompt = custom_prompt if custom_prompt else os.getenv("SYSTEM_PROMPT", """
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
      "epicNumber": "Epic number (e.g., 1, 2, 3...)",
      "stories": [
        {
          "summary": "Story title from requirements",
          "description": "Story description from requirements",
          "priority": "Priority level if mentioned (High/Medium/Low)",
          "storyNumber": "Story number within epic",
          "subtasks": [
            {
              "summary": "Subtask description from requirements",
              "subtaskNumber": "Subtask number"
            }
          ]
        }
      ]
    }
  ]
}

CRITICAL: Extract EVERY epic from the requirements document. Do not limit the number of epics.
If the requirements have 17 epics, output all 17 epics with their complete hierarchy.

Return ONLY valid JSON. No additional text or explanations.
""")
        
        # Prepare content for AI
        content_parts = [system_prompt, "\n\n**Requirements:**\n", requirements_text]
        
        # Add images if provided
        if images and len(images) > 0:
            content_parts.append("\n\n**Architecture Diagrams:**\n")
            for idx, img_bytes in enumerate(images):
                # Upload image to Gemini
                image_part = {
                    'mime_type': 'image/png',
                    'data': img_bytes
                }
                content_parts.append(image_part)
        
        print("--- Sending prompt to AI... ---")
        response = model.generate_content(content_parts)
        
        print("--- AI response received ---")
        
        # Clean up response - robust JSON extraction
        text = response.text
        
        # Try multiple cleaning strategies
        def extract_json(text_input):
            # Strategy 1: Remove markdown code blocks
            cleaned = text_input.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
            
            # Strategy 2: Find JSON between curly braces
            start_idx = text_input.find('{')
            end_idx = text_input.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_text = text_input[start_idx:end_idx + 1]
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass
            
            # Strategy 3: Try to find and parse largest JSON object
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, text_input, re.DOTALL)
            for match in reversed(matches):  # Try largest first
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
            
            return None
        
        # Parse JSON
        structured_data = extract_json(text)
        
        if structured_data is None:
            print(f"Failed to parse AI response as JSON.")
            print(f"Response preview (first 500 chars): {text[:500]}")
            print(f"Response preview (last 500 chars): {text[-500:]}")
            raise HTTPException(status_code=500, detail="AI response was not valid JSON")
        
        return structured_data
            
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

# Routes
@app.get("/")
async def root():
    return {"message": "JIRA Ticket Generator API", "status": "running"}

@app.post("/api/generate-tickets", response_model=TicketGenerationResponse)
async def generate_tickets(
    files: List[UploadFile] = File(...),
    customPrompt: Optional[str] = None
):
    """
    Generate JIRA tickets from requirements files (text and/or images) with optional custom prompt
    """
    try:
        requirements_text = ""
        image_bytes_list = []
        
        print('\n--- 1. Files Received ---')
        
        # Process all uploaded files
        for file in files:
            content = await file.read()
            
            # Check if it's a text file
            if file.filename.endswith('.txt'):
                requirements_text += content.decode('utf-8') + "\n\n"
                print(f"Text file: {file.filename}")
            # Otherwise treat as image
            else:
                image_bytes_list.append(content)
                print(f"Image file: {file.filename} ({len(content)} bytes)")
        
        if not requirements_text.strip():
            raise HTTPException(status_code=400, detail="No text requirements found. Please upload at least one .txt file.")
        
        # Call AI analysis with custom prompt if provided
        print('\n--- 2. Starting AI Analysis ---')
        if customPrompt:
            print("Using custom prompt")
        structured_data = await run_ai_analysis(
            requirements_text, 
            image_bytes_list if image_bytes_list else None,
            customPrompt
        )
        
        # Log partitions
        print('\n--- 3. AI Analysis Complete - Partitions Found ---')
        if structured_data.get('epics'):
            print(f"Found {len(structured_data['epics'])} Epics:")
            for i, epic in enumerate(structured_data['epics']):
                print(f"  [Epic {i+1}] {epic.get('summary', 'No summary')}")
                if epic.get('stories'):
                    print(f"    -> Contains {len(epic['stories'])} Stories")
        else:
            print("WARNING: No 'epics' array found in AI response.")
        
        # Return response
        return TicketGenerationResponse(
            message="Requirements analyzed successfully!",
            stats={
                "epics": len(structured_data.get('epics', [])),
                "imagesProcessed": len(image_bytes_list)
            },
            aiOutput=structured_data
        )
        
    except Exception as e:
        print(f"Error in /api/generate-tickets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error during analysis: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
