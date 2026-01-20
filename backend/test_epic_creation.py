# test_epic_creation.py
"""
Simple test script to verify Epic creation works
"""

from atlassian import Jira
import os
from dotenv import load_dotenv
import time

def main():
    load_dotenv()
    
    jira_url = os.getenv('JIRA_URL')
    jira_email = os.getenv('JIRA_EMAIL') 
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    project_key = os.getenv('JIRA_PROJECT_KEY')
    
    if not all([jira_url, jira_email, jira_api_token, project_key]):
        print(" ERROR: Missing JIRA credentials")
        return
    
    try:
        jira = Jira(
            url=jira_url,
            username=jira_email,
            password=jira_api_token,
            cloud=True
        )
        
        print("🧪 Testing Epic creation...")
        
        # Create a test epic
        test_summary = f"Test Epic - {int(time.time())}"
        test_description = "This is a test epic to verify Epic creation works"
        
        epic_data = {
            'project': {'key': project_key},
            'summary': test_summary,
            'description': test_description,
            'issuetype': {'name': 'Epic'}
        }
        
        print(f"   Creating Epic: {test_summary}")
        response = jira.issue_create(fields=epic_data)
        epic_key = response['key']
        
        print(f" SUCCESS! Created Epic: {epic_key}")
        print(f"   View at: {jira_url}/browse/{epic_key}")
        print()
        print(" Epic creation is working correctly!")
        print(" No Epic Name field is required for this JIRA instance.")
        print(" You can delete this test epic from JIRA.")
        
    except Exception as e:
        print(f" ERROR: {str(e)}")

if __name__ == "__main__":
    main()
