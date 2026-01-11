# JIRA Ticket Generator

A full-stack application that automatically generates JIRA tickets (Epics, Stories, and Subtasks) from text requirements and architecture diagrams using AI.

## Features

- 📝 Upload text-based requirements files
- 🖼️ Process architecture diagrams and images (supports multiple images)
- 🤖 AI-powered analysis using Google Gemini 1.5 Pro
- 📊 Generate structured Epics, Stories, and Subtasks
- 💾 Export results as JSON for JIRA import
- 🎨 Modern, responsive UI with TailwindCSS
- ✅ Fixed: Now uses correct Gemini model (gemini-1.5-pro-latest)

## Tech Stack

**Frontend:**
- React 18
- Vite
- TailwindCSS
- Axios
- Lucide Icons

**Backend:**
- FastAPI
- Python 3.10+
- Google Generative AI (Gemini)
- Uvicorn

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Google AI API Key ([Get it here](https://makersuite.google.com/app/apikey))

## Setup Instructions

### 1. Clone the Repository

```bash
cd c:\Users\91957\JIRA_TICKET\jira_ticket.io
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env and add your Google API Key
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### 4. Run the Application

**Option A: Quick Start (Automated)**
```bash
# Run setup once
setup.bat

# Then start backend (Terminal 1)
start-backend.bat

# Start frontend (Terminal 2)
start-frontend.bat
```

**Option B: Manual Start**
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python main.py
# Backend runs on http://localhost:8000

# Terminal 2 - Frontend
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

### 5. Test the Application

1. Open http://localhost:5173 in your browser
2. Upload the `sample_requirements.txt` file (text requirements)
3. **(Optional but recommended)** Upload architecture diagram images
   - Supports: PNG, JPG, JPEG, GIF, etc.
   - Multiple images allowed
   - AI analyzes text + images together
4. Click **"Generate Tickets"**
5. Wait 10-30 seconds for AI processing
6. View the generated Epics, Stories, and Subtasks
7. Click **"Download JSON"** to export for JIRA

## API Endpoints

### `POST /api/generate-tickets`
Generate JIRA tickets from requirements and images.

**Request:**
- `requirementsFile`: Text file (multipart/form-data)
- `images`: Array of image files (optional)

**Response:**
```json
{
  "message": "Requirements analyzed successfully!",
  "stats": {
    "epics": 4,
    "imagesProcessed": 1
  },
  "aiOutput": {
    "epics": [...]
  }
}
```

## Project Structure

```
jira_ticket.io/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (create this)
│   └── .env.example         # Example environment file
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── main.jsx        # Entry point
│   │   └── index.css       # Global styles
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   └── tailwind.config.js  # Tailwind configuration
├── sample_requirements.txt  # Example requirements file
└── README.md               # This file
```

## How It Works

1. **Upload**: User uploads a requirements text file and optional architecture diagrams
2. **Analysis**: Backend sends the content to Google Gemini AI with a structured prompt
3. **Processing**: AI analyzes the requirements and generates structured output
4. **Display**: Frontend displays the Epics, Stories, and Subtasks in a hierarchical view
5. **Export**: User can download the structured JSON for JIRA import

## Customization

### Modify AI Prompt

Edit the `SYSTEM_PROMPT` in `backend/.env` or modify the default prompt in `backend/main.py` to customize how the AI generates tickets.

### Adjust UI

Edit `frontend/src/App.jsx` to customize the user interface and styling.

## Deployment

### Docker Compose (Local Full Stack)

1. Build and start both services:
   ```bash
   docker-compose up --build
   ```
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000

2. Stop containers:
   ```bash
   docker-compose down
   ```

### Render Deployment (Backend)

1. Push the backend code to your GitHub repo.
2. Go to [Render](https://render.com/) and create a new Web Service:
   - Select your repo and choose Python as the environment.
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
   - Set environment variables (copy from your `.env` file, including `GOOGLE_API_KEY`).
   - Set port to `10000` (or as required by Render).
3. Deploy and note your Render backend URL (e.g., `https://your-backend.onrender.com`).

### Vercel Deployment (Frontend)

1. Push the frontend code to your GitHub repo.
2. In Vercel, import the repo and set the build output directory to `dist` (for Vite).
3. Set environment variable `VITE_API_URL` to your Render backend URL (e.g., `https://your-backend.onrender.com`).
4. (Optional) Use the provided `vercel.json` to rewrite `/api/*` calls to your backend.
5. Deploy. Your frontend will be live on your Vercel domain and will proxy API requests to Render.

---

## Troubleshooting

**CORS Issues:**
- Ensure backend allows the frontend origin in CORS settings
- Check that backend is running on port 8000

**API Key Issues:**
- Verify your Google API key is valid
- Check `.env` file is in the backend directory
- Ensure `.env` is not gitignored during development

**Import Errors:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Future Enhancements

- Direct JIRA API integration for automatic ticket creation
- Support for multiple AI models (OpenAI, Claude, etc.)
- Batch processing of multiple requirement files
- User authentication and project management
- Export to other formats (CSV, Excel)
- Real-time collaboration features

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
