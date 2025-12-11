# How Text + Image Processing Works

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER UPLOADS                          │
├─────────────────────────────────────────────────────────────┤
│  1. sample_requirements.txt (TEXT)                           │
│     ├─ Project Overview                                      │
│     ├─ Business Requirements                                 │
│     ├─ Technical Architecture                                │
│     └─ Success Metrics                                       │
│                                                              │
│  2. Architecture Diagrams (IMAGES - Optional)                │
│     ├─ System Architecture.png                               │
│     ├─ Database Schema.jpg                                   │
│     ├─ User Flow Diagram.png                                 │
│     └─ ... (multiple images supported)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
├─────────────────────────────────────────────────────────────┤
│  • Collects both text file and images                        │
│  • Packages into FormData                                    │
│  • Sends POST to /api/generate-tickets                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
├─────────────────────────────────────────────────────────────┤
│  1. Receives requirementsFile + images[]                     │
│  2. Reads text content from file                             │
│  3. Reads binary data from each image                        │
│  4. Passes BOTH to AI analysis function                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              AI ANALYSIS (Google Gemini 1.5 Pro)             │
├─────────────────────────────────────────────────────────────┤
│  Model: gemini-1.5-pro-latest                                │
│                                                              │
│  Input Processed:                                            │
│  ┌──────────────────────────────────────────────────┐       │
│  │ System Prompt (Instructions)                      │       │
│  │ ↓                                                 │       │
│  │ Requirements Text                                 │       │
│  │ ↓                                                 │       │
│  │ Image 1 (Architecture Diagram)                    │       │
│  │ ↓                                                 │       │
│  │ Image 2 (Database Schema)                         │       │
│  │ ↓                                                 │       │
│  │ Image N (More diagrams...)                        │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  AI Analyzes:                                                │
│  • Text requirements (features, tech stack, etc.)            │
│  • Visual diagrams (architecture, flows, schemas)            │
│  • Combines understanding from BOTH sources                  │
│  • Generates comprehensive JIRA structure                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    STRUCTURED OUTPUT                         │
├─────────────────────────────────────────────────────────────┤
│  {                                                           │
│    "epics": [                                                │
│      {                                                       │
│        "summary": "User & Driver Management",                │
│        "description": "Based on text + architecture...",     │
│        "stories": [                                          │
│          {                                                   │
│            "summary": "User Registration Flow",              │
│            "description": "From diagram + requirements...",  │
│            "subtasks": [                                     │
│              {"summary": "Design API endpoints"},            │
│              {"summary": "Implement auth service"}           │
│            ]                                                 │
│          }                                                   │
│        ]                                                     │
│      }                                                       │
│    ]                                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND DISPLAY                          │
├─────────────────────────────────────────────────────────────┤
│  Beautiful UI showing:                                       │
│  📦 Epic 1: User & Driver Management                         │
│     📋 Story 1: User Registration Flow                       │
│        ✓ Subtask: Design API endpoints                      │
│        ✓ Subtask: Implement auth service                    │
│     📋 Story 2: Profile Management                           │
│        ✓ Subtask: Create profile schema                     │
│  📦 Epic 2: Real-time Tracking                               │
│     ...                                                      │
└─────────────────────────────────────────────────────────────┘
```

## Key Points

### ✅ Single API Call
The frontend sends **one request** containing:
- 1 requirements file (text)
- Multiple images (0 to N images)

### ✅ Combined Analysis
Google Gemini 1.5 Pro analyzes **both** inputs together:
- Reads text requirements
- Interprets visual diagrams
- Cross-references information
- Generates comprehensive tickets

### ✅ Example Scenario

**Text says:**
> "Real-time location tracking with Redis cache"

**Diagram shows:**
> [Architecture diagram with: Location Service → Redis → Dispatch Service]

**AI generates:**
```json
{
  "summary": "Real-time Location Services",
  "stories": [
    {
      "summary": "Implement Location Caching",
      "subtasks": [
        {"summary": "Set up Redis cluster"},
        {"summary": "Create Location Service"},
        {"summary": "Integrate with Dispatch Service"}
      ]
    }
  ]
}
```

The AI **combines** text description + visual architecture to create detailed, actionable tasks.

## Why This Works Better Than Text Alone

| Text Only | Text + Images |
|-----------|---------------|
| "Use microservices" | See exact service boundaries in diagram |
| "Store in database" | See database schema and relationships |
| "Real-time updates" | See WebSocket flow and data path |
| "User journey" | See complete user flow diagram |

## Usage Tips

### 📝 Best Text Requirements
- Clear feature descriptions
- Technical specifications
- Business requirements
- Success metrics

### 🖼️ Best Images to Upload
- System architecture diagrams
- Database schemas (ERD)
- User flow / journey maps
- Wireframes / mockups
- Sequence diagrams
- Component diagrams
- Network topology
- API flow diagrams

### 🎯 Result
The AI creates tickets that are:
- **Comprehensive** - Covers both high-level and details
- **Technical** - Includes architecture insights
- **Actionable** - Clear subtasks for implementation
- **Aligned** - Text + visuals inform each other

## Code Reference

### Frontend Upload
```javascript
// frontend/src/App.jsx
const formData = new FormData()
formData.append('requirementsFile', requirementsFile)  // Text file
imageFiles.forEach((img) => {
  formData.append('images', img)  // Multiple images
})
```

### Backend Reception
```python
# backend/main.py
async def generate_tickets(
    requirementsFile: UploadFile = File(...),      # Required text
    images: Optional[List[UploadFile]] = File(None) # Optional images
)
```

### AI Processing
```python
# backend/main.py
content_parts = [system_prompt, requirements_text]
if images:
    for img_bytes in images:
        content_parts.append({'mime_type': 'image/png', 'data': img_bytes})

response = model.generate_content(content_parts)  # All together!
```

## Try It Now!

1. Start the application
2. Upload `sample_requirements.txt`
3. Add some architecture diagrams (if you have any)
4. Click "Generate Tickets"
5. See comprehensive Epics and Stories generated from both sources!
