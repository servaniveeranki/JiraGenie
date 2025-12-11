# Quick Start Guide

## Prerequisites Check
✅ Python 3.10+ installed  
✅ Node.js 18+ installed  
✅ Google AI API Key ready ([Get here](https://makersuite.google.com/app/apikey))

## Setup (First Time Only)

### 1. Configure API Key
Edit `backend\.env` and add your Google API key:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

### 2. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## Run the Application

### Start Backend (Terminal 1)
```bash
cd backend
venv\Scripts\activate
python main.py
```
✅ Backend running on http://localhost:8000

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
✅ Frontend running on http://localhost:5173

## How to Use

### Upload Requirements
1. Open http://localhost:5173 in your browser
2. Click **"Click to upload requirements.txt"**
3. Select `sample_requirements.txt` from the project root
4. **(Optional)** Click **"Click to upload architecture diagrams"** to add images
5. Click **"Generate Tickets"**
6. Wait for AI analysis (10-30 seconds)
7. View generated Epics, Stories, and Subtasks
8. Click **"Download JSON"** to export

### Expected Output Structure
```json
{
  "epics": [
    {
      "summary": "Epic Title",
      "description": "Epic description...",
      "stories": [
        {
          "summary": "Story Title",
          "description": "Story description...",
          "subtasks": [
            {"summary": "Subtask 1"},
            {"summary": "Subtask 2"}
          ]
        }
      ]
    }
  ]
}
```

## Troubleshooting

### Model Error (404)
✅ **FIXED** - Now using `gemini-1.5-pro-latest` model

### CORS Error
- Ensure backend is running on port 8000
- Ensure frontend is running on port 5173

### API Key Error
- Verify your API key in `backend\.env`
- Check you copied the key correctly (no extra spaces)
- Ensure the file is named `.env` (not `.env.txt`)

### Module Not Found
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

## Features

✅ **Text Requirements** - Upload .txt files with project requirements  
✅ **Architecture Diagrams** - Upload multiple images (PNG, JPG, etc.)  
✅ **AI Analysis** - Google Gemini processes text and images together  
✅ **Structured Output** - Epics → Stories → Subtasks hierarchy  
✅ **JSON Export** - Download for JIRA import  
✅ **Modern UI** - Beautiful, responsive interface  

## Tips

- **Better Results**: Write clear, detailed requirements
- **Images**: Upload architecture diagrams, flowcharts, wireframes
- **Multiple Images**: You can upload several images at once
- **Export**: The JSON output can be imported into JIRA or other tools

## Next Steps

Want to customize?
- Edit AI prompt in `backend/main.py` line 50
- Modify UI in `frontend/src/App.jsx`
- Add more features like direct JIRA API integration!
