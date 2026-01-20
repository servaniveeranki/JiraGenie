# find_epic_fields.py
"""
Script to find Epic Name and Epic Link field IDs in your JIRA instance
Run this script to get the correct field IDs for your JIRA setup
"""

from atlassian import Jira
import os
from dotenv import load_dotenv
import sys

def main():
    load_dotenv()
    
    # Check if JIRA credentials are configured
    jira_url = os.getenv('JIRA_URL')
    jira_email = os.getenv('JIRA_EMAIL') 
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    project_key = os.getenv('JIRA_PROJECT_KEY')
    
    if not all([jira_url, jira_email, jira_api_token]):
        print(" ERROR: JIRA credentials not found in .env file")
        print("Please ensure these variables are set in your .env file:")
        print("- JIRA_URL")
        print("- JIRA_EMAIL") 
        print("- JIRA_API_TOKEN")
        print("- JIRA_PROJECT_KEY (optional but recommended)")
        sys.exit(1)
    
    print(f" Connecting to JIRA at: {jira_url}")
    print(f" Using email: {jira_email}")
    if project_key:
        print(f" Project key: {project_key}")
    print()
    
    try:
        jira = Jira(
            url=jira_url,
            username=jira_email,
            password=jira_api_token,
            cloud=True
        )
        
        # Test connection
        print(" Testing JIRA connection...")
        try:
            user_info = jira.get_myself()
            print(f"   Connected as: {user_info.get('displayName', user_info.get('name', 'Unknown'))}")
        except:
            # If get_myself fails, try alternative methods
            try:
                user_info = jira.current_user()
                print(f"   Connected as: {user_info.get('displayName', user_info.get('name', 'Unknown'))}")
            except:
                print("   Connected successfully (could not retrieve user details)")
        print()
        
    except Exception as e:
        print(f" ERROR: Failed to connect to JIRA: {str(e)}")
        print("Please check your credentials and try again.")
        sys.exit(1)
    
    print("=" * 80)
    print("CHECKING PROJECT ISSUE TYPES:")
    print("=" * 80)
    
    if project_key:
        try:
            print(f" Getting issue types for project: {project_key}")
            metadata = jira.issue_createmeta(
                project=project_key,
                expand='projects.issuetypes'
            )
            
            if metadata and 'projects' in metadata and metadata['projects']:
                project = metadata['projects'][0]
                if 'issuetypes' in project and project['issuetypes']:
                    issue_types = project['issuetypes']
                    print(f"   Found {len(issue_types)} issue types:")
                    for issue_type in issue_types:
                        name = issue_type.get('name', 'Unknown')
                        print(f"   - {name}")
                    
                    # Check if Epic is available
                    epic_available = any(it.get('name', '').lower() == 'epic' for it in issue_types)
                    if epic_available:
                        print("\n Epic issue type is available!")
                    else:
                        print("\n Epic issue type NOT found in this project!")
                        print("   This might be a JIRA Work Management project instead of JIRA Software.")
                        print("   Epics are typically only available in JIRA Software projects.")
                else:
                    print("   No issue types found")
            else:
                print("   Could not get project metadata")
        except Exception as e:
            print(f"   Error getting issue types: {str(e)}")
    else:
        print("   No project key provided")
    
    print()
    print("=" * 80)
    print("SEARCHING FOR EPIC-RELATED FIELDS:")
    print("=" * 80)
    
    try:
        # Get all fields
        print(" Getting all fields from JIRA...")
        fields = jira.get_all_fields()
        print(f"   Found {len(fields)} total fields")
        print()
        
        epic_fields = []
        for field in fields:
            field_name = field.get('name', '').lower()
            field_id = field.get('id', '')
            schema = field.get('schema', {})
            custom = schema.get('custom', '') if schema else ''
            
            # Look for Epic-related fields
            if 'epic' in field_name:
                epic_fields.append(field)
                print(f"✓ Found Epic Field:")
                print(f"  Name: {field['name']}")
                print(f"  ID: {field['id']}")
                print(f"  Type: {schema.get('type', 'N/A')}")
                print(f"  Custom: {field.get('custom', False)}")
                if custom:
                    print(f"  Custom Type: {custom}")
                print()
        
        if not epic_fields:
            print("  No Epic fields found with 'epic' in the name!")
            print()
            print(" Checking Epic issue type metadata for required fields...")
            
            # Get Epic-specific metadata
            try:
                # Use the existing metadata and filter for Epic
                metadata = jira.issue_createmeta(
                    project=project_key,
                    expand='projects.issuetypes.fields'
                )
                
                if metadata and 'projects' in metadata and metadata['projects']:
                    project_meta = metadata['projects'][0]
                    if 'issuetypes' in project_meta and project_meta['issuetypes']:
                        for issue_type in project_meta['issuetypes']:
                            if issue_type.get('name') == 'Epic':
                                fields = issue_type.get('fields', {})
                                print(f"   Epic has {len(fields)} fields:")
                                required_fields = []
                                for field_id, field_data in fields.items():
                                    field_name = field_data.get('name', 'Unknown')
                                    required = field_data.get('required', False)
                                    if required:
                                        required_fields.append(field_name)
                                        print(f"    REQUIRED: {field_id} = {field_name}")
                                    else:
                                        print(f"   - {field_id} = {field_name}")
                                
                                if not required_fields:
                                    print("    No required fields for Epic creation!")
                                    print("    This means you can create Epics without Epic Name field!")
                                else:
                                    print(f"     Required fields: {', '.join(required_fields)}")
                                break
            except Exception as e:
                print(f"   Error getting Epic metadata: {str(e)}")
            
            print()
            print("🔍 Showing ALL custom fields (look for Epic-related ones):")
            print("-" * 80)
            try:
                custom_fields = [f for f in fields if f.get('custom', False)]
                for field in custom_fields:
                    field_name = field.get('name', '').lower()
                    field_id = field.get('id', '')
                    if any(keyword in field_name for keyword in ['epic', 'link', 'name']):
                        print(f" POTENTIAL MATCH: {field['id']}: {field['name']}")
                    else:
                        print(f"   {field['id']}: {field['name']}")
            except Exception as e:
                print(f"   Error showing custom fields: {str(e)}")
        else:
            print("=" * 80)
            print("SUMMARY - ADD THESE TO YOUR .env FILE:")
            print("=" * 80)
            
            epic_name_field = None
            epic_link_field = None
            
            for field in epic_fields:
                field_name = field['name'].lower()
                field_id = field['id']
                
                if 'name' in field_name and 'epic' in field_name:
                    epic_name_field = field_id
                    print(f"JIRA_EPIC_NAME_FIELD={field_id}")
                elif 'link' in field_name and 'epic' in field_name:
                    epic_link_field = field_id
                    print(f"JIRA_EPIC_LINK_FIELD={field_id}")
            
            print()
            print(" INSTRUCTIONS:")
            print("1. Copy the lines above to your backend/.env file")
            print("2. Restart your backend server")
            print("3. Try creating Epics again")
            
            # Test if we can create an epic with these fields
            if project_key and epic_name_field:
                print()
                print("=" * 80)
                print("TESTING EPIC CREATION:")
                print("=" * 80)
                test_epic_creation(jira, project_key, epic_name_field, epic_link_field)
        
    except Exception as e:
        print(f" ERROR: Failed to get fields: {str(e)}")
        sys.exit(1)

def test_epic_creation(jira, project_key, epic_name_field, epic_link_field):
    """Test creating a sample epic to verify field IDs work"""
    import time
    
    test_summary = f"Test Epic - {int(time.time())}"
    test_description = "This is a test epic created by find_epic_fields.py script"
    
    print(f" Testing Epic creation with field: {epic_name_field}")
    print(f"   Project: {project_key}")
    print(f"   Summary: {test_summary}")
    print()
    
    try:
        # Try to create epic
        epic_data = {
            'project': {'key': project_key},
            'summary': test_summary,
            'description': test_description,
            'issuetype': {'name': 'Epic'}
        }
        
        # Add Epic Name field if we have it
        if epic_name_field:
            epic_data[epic_name_field] = test_summary
        
        print(" Sending Epic creation request...")
        epic = jira.issue_create(fields=epic_data)
        epic_key = epic.get('key')
        
        print(f" SUCCESS! Created Epic: {epic_key}")
        print(f"   You can view it at: {jira.url}/browse/{epic_key}")
        print()
        print(" Your Epic field configuration is working correctly!")
        print(" You may want to delete this test epic from JIRA")
        
    except Exception as e:
        print(f" FAILED to create test epic: {str(e)}")
        print()
        print(" TROUBLESHOOTING:")
        print("1. Make sure your JIRA project has Epic issue type enabled")
        print("2. Check if the Epic Name field is required in your project")
        print("3. Verify you have permission to create Epics")
        print("4. Try creating an Epic manually in JIRA web interface first")

if __name__ == "__main__":
    main()
