from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import base64
from pathlib import Path

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="JIRA Ticket Generator")

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
Analyze the requirements and generate JIRA tickets in JSON format.

Create 3-5 Epics, each with 2-4 Stories, each Story with 3-5 Subtasks.

Output Format:
{
  "epics": [
    {
      "summary": "Epic title (concise)",
      "description": "Epic scope and value (1-2 sentences)",
      "stories": [
        {
          "summary": "Story title",
          "description": "Story details (1-2 sentences)",
          "subtasks": [
            {"summary": "Task description"}
          ]
        }
      ]
    }
  ]
}

Return ONLY valid JSON. Be concise but comprehensive.
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
        
        # Clean up response
        text = response.text
        cleaned_text = text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        try:
            structured_data = json.loads(cleaned_text)
            return structured_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {text}")
            raise HTTPException(status_code=500, detail="AI response was not valid JSON")
            
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
