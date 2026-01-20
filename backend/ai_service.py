


from typing import List, Optional
import google.generativeai as genai
import os
import json
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


async def run_ai_analysis(requirements_text: str, images: List[bytes] = None, custom_prompt: Optional[str] = None):
    """
    Analyze requirements using Google Gemini AI
    Supports both text and image inputs
    
    Args:
        requirements_text: Text requirements to analyze
        images: Optional list of image bytes to analyze
        custom_prompt: Optional custom prompt to override default
    
    Returns:
        Dict containing structured epics, stories, and subtasks
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
        
        logger.info("Sending prompt to AI...")
        response = model.generate_content(content_parts)
        
        logger.info("AI response received")
        
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
            logger.error("Failed to parse AI response as JSON")
            logger.error(f"Response preview (first 500 chars): {text[:500]}")
            logger.error(f"Response preview (last 500 chars): {text[-500:]}")
            raise HTTPException(status_code=500, detail="AI response was not valid JSON")
        
        return structured_data
            
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")