# JIRA Integration Guide

This document provides detailed information about the JIRA integration in the JIRA Ticket Generator application, including how it works, setup instructions, and usage examples.

## Table of Contents
- [Overview](#overview)
- [How It Works](#how-it-works)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The JIRA integration allows you to automatically create Epics, Stories, and Subtasks in your JIRA project based on AI-analyzed requirements. The integration uses the JIRA REST API through the `atlassian-python-api` library.

## How It Works

1. **AI Analysis**: The application processes your requirements using Google's Gemini AI to identify Epics, Stories, and Subtasks.
2. **JIRA Mapping**: The analyzed data is mapped to JIRA's issue types and fields.
3. **API Integration**: The application uses JIRA's REST API to create the issues in your specified project.
4. **Hierarchy Management**: Maintains proper parent-child relationships between Epics, Stories, and Subtasks.

## Setup Instructions

### Prerequisites
1. JIRA Cloud account with admin access
2. API token from JIRA
3. Project key where tickets will be created

### Environment Variables
Create or update the `.env` file in the `backend` directory with the following variables:

```env
# JIRA Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=YOURPROJ

# Optional: Customize issue type names if different from defaults
JIRA_EPIC_ISSUE_TYPE=Epic
JIRA_STORY_ISSUE_TYPE=Story
JIRA_SUBTASK_ISSUE_TYPE=Sub-task

# Google AI Configuration
GOOGLE_API_KEY=your-google-ai-api-key
```

### Obtaining JIRA API Token
1. Log in to your Atlassian account
2. Click on your profile picture → **Account settings**
3. Go to **Security** → **Create and manage API tokens**
4. Click **Create API token** and follow the prompts
5. Copy the generated token (you won't be able to see it again)

## API Endpoints

### 1. Create JIRA Tickets from AI Output

**Endpoint:** `POST /api/jira/create-tickets`

**Request Body:**
```json
{
  "ai_output": {
    "epics": [
      {
        "name": "Epic Name",
        "description": "Epic description...",
        "stories": [
          {
            "name": "Story Name",
            "description": "Story description...",
            "subtasks": [
              {
                "name": "Subtask Name",
                "description": "Subtask description..."
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 2. Create JIRA Tickets from Requirements File

**Endpoint:** `POST /api/jira/create-from-file`

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `files`: One or more requirements files (text/plain)
  - `customPrompt`: (Optional) Custom prompt for AI analysis

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your JIRA email and API token
   - Ensure your account has the necessary permissions in the project

2. **Epic/Story/Sub-task Fields Not Found**
   - Check if the issue type names in your JIRA project match those in your `.env` file
   - Verify that the Epic Name and Epic Link fields exist in your JIRA instance

3. **Rate Limiting**
   - The application includes basic rate limiting. If you encounter rate limits:
     - Wait before making additional requests
     - Process requirements in smaller batches

### Logs
Check the application logs for detailed error messages. The backend logs are output to the console where the server is running.

## Best Practices

1. **Test with a Small Dataset**
   - Start with a small requirements file to test the integration
   - Verify the created tickets in JIRA before processing large batches

2. **Custom Fields**
   - If you need to set custom fields, modify the `_create_epic`, `_create_story`, and `_create_subtask` methods in `jira_service.py`

3. **Error Handling**
   - The application will continue processing even if some tickets fail to create
   - Check the response for any errors that occurred during processing

4. **Backup**
   - Always back up your requirements files
   - Consider exporting the AI analysis results to JSON before creating JIRA tickets

## Support

For additional help, please contact the development team or refer to the [JIRA REST API documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/).
