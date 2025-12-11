# Testing Guide - Verify All Fixes

## Pre-Test Checklist

✅ Ensure `backend/.env` has your Google API key  
✅ Python virtual environment created  
✅ Node modules installed  

## Test 1: Model Error Fix

### What Was Fixed
Changed from `gemini-1.5-flash` to `gemini-1.5-pro-latest`

### How to Test
```bash
# Terminal 1
cd backend
venv\Scripts\activate
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ PASS:** Server starts without errors  
**❌ FAIL:** Import errors or model errors

---

## Test 2: Spelling Corrections

### What Was Fixed
Completely recreated `sample_requirements.txt` with correct spelling

### How to Test
Open `sample_requirements.txt` and verify:

**Line 1:** 
```
PROJECT: Real-Time Ride-Sharing Platform  ✅
```
NOT: `ROJECTRealTi Rid-Sharing` ❌

**Line 5-6:**
```
Build a scalable, cloud-native ride-sharing platform  ✅
```
NOT: `calabl,clud-native d-haringplatform` ❌

**Lines 108-114:** (Phases section)
```
PHASE 1 MVP (3-4 months):
- Basic rider and driver registration
- Simple ride request and driver matching
...
```
✅ Clean, readable, properly formatted

**✅ PASS:** All text is properly spelled and formatted  
**❌ FAIL:** Typos or formatting issues remain

---

## Test 3: Text + Image Processing

### What to Test
System should accept and process both text requirements AND images together

### Test Setup
1. Prepare test files:
   - `sample_requirements.txt` (provided)
   - Any architecture diagram images (PNG, JPG)

### Test Steps

**Step 1: Start Backend**
```bash
cd backend
venv\Scripts\activate
python main.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Step 2: Start Frontend**
```bash
# New terminal
cd frontend
npm run dev
```
Wait for: `Local: http://localhost:5173/`

**Step 3: Open Browser**
Navigate to: http://localhost:5173

**Step 4: Upload Text Only**
1. Click "Click to upload requirements.txt"
2. Select `sample_requirements.txt`
3. Do NOT upload images yet
4. Click "Generate Tickets"

**Expected Result:**
- ✅ Shows "Analyzing..." spinner
- ✅ After 10-30 seconds, shows success message
- ✅ Displays epics, stories, subtasks
- ✅ Stats show: "X Epic(s) • 0 Image(s) Processed"

**Step 5: Upload Text + Images**
1. Click "Reset" button
2. Upload `sample_requirements.txt`
3. Click "Click to upload architecture diagrams"
4. Select 1-3 architecture images
5. Verify images show: "3 image(s) selected"
6. Click "Generate Tickets"

**Expected Result:**
- ✅ Shows "Analyzing..." spinner
- ✅ After 20-40 seconds (longer due to images)
- ✅ Shows success message
- ✅ Displays epics, stories, subtasks
- ✅ Stats show: "X Epic(s) • 3 Image(s) Processed"
- ✅ Output includes insights from images

**Step 6: Verify AI Combined Analysis**
Check generated stories for references to:
- Architecture components (from diagrams)
- Service names (from diagrams)
- Data flows (from diagrams)
- Technical details (from text)

**✅ PASS:** All uploads work, images are processed  
**❌ FAIL:** Errors during upload or processing

---

## Test 4: Full End-to-End Flow

### Complete User Journey

1. **Start Application**
   ```bash
   # Terminal 1
   start-backend.bat
   
   # Terminal 2
   start-frontend.bat
   ```

2. **Upload Requirements**
   - Open http://localhost:5173
   - Upload `sample_requirements.txt`
   - Upload 2-3 architecture images (optional)

3. **Generate Tickets**
   - Click "Generate Tickets"
   - Wait for processing
   - Verify success message

4. **Review Output**
   - Check for 4-6 Epics
   - Verify each Epic has multiple Stories
   - Confirm each Story has Subtasks
   - Look for well-structured descriptions

5. **Download JSON**
   - Click "Download JSON"
   - Verify file downloads as `jira-tickets.json`
   - Open file and verify JSON structure

6. **Check Backend Logs**
   Review terminal for:
   ```
   --- 1. File Received ---
   --- 2. Starting AI Analysis ---
   --- Sending prompt to AI... ---
   --- AI response received ---
   --- 3. AI Analysis Complete - Partitions Found ---
   Found X Epics:
     [Epic 1] ...
     [Epic 2] ...
   ```

**✅ PASS:** Complete flow works end-to-end  
**❌ FAIL:** Any step fails or errors occur

---

## Expected Console Outputs

### Backend Terminal (Success)
```
--- 1. File Received ---
Requirements file: sample_requirements.txt

--- Processing 2 images ---
Image: architecture.png (45678 bytes)
Image: schema.jpg (34567 bytes)

--- 2. Starting AI Analysis ---
--- Sending prompt to AI... ---
--- AI response received ---

--- 3. AI Analysis Complete - Partitions Found ---
Found 5 Epics:
  [Epic 1] User & Driver Management
    -> Contains 3 Stories
  [Epic 2] Ride Request & Matching
    -> Contains 4 Stories
  [Epic 3] Real-time Tracking
    -> Contains 3 Stories
  ...
```

### Frontend Browser (Success)
- ✅ Green success banner
- ✅ "Tickets Generated Successfully!"
- ✅ Stats: "5 Epic(s) • 2 Image(s) Processed"
- ✅ Hierarchical display of tickets
- ✅ Download button works

---

## Common Issues & Solutions

### Issue: "Model not found" error
**Solution:** Already fixed! Using `gemini-1.5-pro-latest`

### Issue: Spelling errors in sample file
**Solution:** Already fixed! File recreated with correct spelling

### Issue: Images not uploading
**Check:**
- File size < 20MB per image
- Supported formats: PNG, JPG, JPEG, GIF
- Browser console for errors

### Issue: CORS errors
**Solution:**
- Ensure backend on port 8000
- Ensure frontend on port 5173
- Check CORS config in `backend/main.py`

### Issue: Slow processing
**Normal:** 
- Text only: 10-20 seconds
- With images: 20-40 seconds
- More images = longer processing

---

## Success Criteria

✅ All 3 tests pass  
✅ No console errors  
✅ Generates structured Epics/Stories  
✅ JSON export works  
✅ Text + images processed together  

## Report Results

If all tests pass: **🎉 System is working perfectly!**

If any test fails:
1. Check terminal logs for errors
2. Verify `.env` has correct API key
3. Ensure all dependencies installed
4. Check browser console (F12)

---

## Next Steps

Once all tests pass:
- ✅ Use with your own requirements files
- ✅ Upload your architecture diagrams
- ✅ Export JSON for JIRA import
- ✅ Customize prompts for your needs
