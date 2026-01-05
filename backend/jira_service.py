import logging
from typing import Dict, List, Optional
from atlassian import Jira
from config import settings

logger = logging.getLogger(__name__)

class JiraService:
    def __init__(self):
        self.jira = Jira(
            url=settings.JIRA_URL,
            username=settings.JIRA_EMAIL,
            password=settings.JIRA_API_TOKEN,
            cloud=True
        )
        self.project_key = settings.JIRA_PROJECT_KEY
        self.epic_name_field = self._get_epic_name_field()
        
    def _get_epic_name_field(self) -> str:
        """Get the custom field ID for Epic Name"""
        # Try to get the create metadata for the project and issue type
        try:
            metadata = self.jira.get_create_meta(
                project_keys=self.project_key,
                issuetype_names=settings.JIRA_EPIC_ISSUE_TYPE,
                expand='projects.issuetypes.fields'
            )
            
            # Find the Epic Name field in the metadata
            if metadata and 'projects' in metadata and metadata['projects']:
                project = metadata['projects'][0]
                if 'issuetypes' in project and project['issuetypes']:
                    fields = project['issuetypes'][0].get('fields', {})
                    for field_id, field_data in fields.items():
                        if field_data.get('name', '').lower() == 'epic name' or \
                           field_data.get('fieldId', '').lower() == 'epicname':
                            return field_id
            
            # Fallback to common field IDs if metadata lookup fails
            for field_id in ['customfield_10011', 'customfield_10014', 'customfield_10015', 'customfield_10016']:
                try:
                    # Check if we can get field info
                    field_info = self.jira.get_field(field_id)
                    if field_info and ('epic' in field_info.get('name', '').lower() or 
                                     'epic' in field_info.get('clauseNames', [''])[0].lower()):
                        return field_id
                except:
                    continue
                    
            logger.warning("Could not determine Epic Name field, trying direct creation")
            return 'customfield_10011'  # Default fallback
            
        except Exception as e:
            logger.warning(f"Error getting Epic Name field metadata: {str(e)}")
            return 'customfield_10011'  # Default fallback

    async def create_epic(self, epic_data: Dict) -> Optional[Dict]:
        """Create an Epic in Jira"""
        try:
            # First try with the detected field
            issue = {
                'project': {'key': self.project_key},
                'summary': epic_data['summary'],
                'description': epic_data.get('description', ''),
                'issuetype': {'name': settings.JIRA_EPIC_ISSUE_TYPE}
            }
            
            # Only add the epic name field if we have a valid field ID
            if hasattr(self, 'epic_name_field') and self.epic_name_field:
                issue[self.epic_name_field] = epic_data['summary']
            
            # Try to create the issue
            response = self.jira.issue_create(fields=issue)
            
            # If we get here, it worked!
            logger.info(f"Created Epic: {response['key']} - {epic_data['summary']}")
            return {
                'key': response['key'],
                'self': response['self'],
                'summary': epic_data['summary']
            }
            
        except Exception as e:
            # If we get a field error, try without the epic name field
            if 'field' in str(e).lower() and 'cannot be set' in str(e).lower():
                try:
                    logger.warning(f"Epic creation with field {self.epic_name_field} failed, trying without it")
                    issue = {
                        'project': {'key': self.project_key},
                        'summary': epic_data['summary'],
                        'description': epic_data.get('description', ''),
                        'issuetype': {'name': settings.JIRA_EPIC_ISSUE_TYPE}
                    }
                    response = self.jira.issue_create(fields=issue)
                    logger.info(f"Created Epic (without name field): {response['key']} - {epic_data['summary']}")
                    return {
                        'key': response['key'],
                        'self': response['self'],
                        'summary': epic_data['summary']
                    }
                except Exception as e2:
                    logger.error(f"Error creating Epic (second attempt): {str(e2)}")
                    return None
            else:
                logger.error(f"Error creating Epic: {str(e)}")
                return None

    async def create_story(self, story_data: Dict, parent_key: str = None) -> Optional[Dict]:
        """Create a Story in Jira, optionally linked to a parent Epic"""
        try:
            issue = {
                'project': {'key': self.project_key},
                'summary': story_data['summary'],
                'description': story_data.get('description', ''),
                'issuetype': {'name': settings.JIRA_STORY_ISSUE_TYPE},
                'priority': {'name': story_data.get('priority', 'Medium')}
            }
            
            if parent_key:
                issue['parent'] = {'key': parent_key}
                
            response = self.jira.issue_create(fields=issue)
            logger.info(f"Created Story: {response['key']} - {story_data['summary']}")
            return {
                'key': response['key'],
                'self': response['self'],
                'summary': story_data['summary']
            }
        except Exception as e:
            logger.error(f"Error creating Story: {str(e)}")
            return None

    async def create_subtask(self, subtask_data: Dict, parent_key: str) -> Optional[Dict]:
        """Create a Subtask in Jira"""
        try:
            issue = {
                'project': {'key': self.project_key},
                'summary': subtask_data['summary'],
                'description': subtask_data.get('description', ''),
                'issuetype': {'name': settings.JIRA_SUBTASK_ISSUE_TYPE},
                'parent': {'key': parent_key}
            }
            
            response = self.jira.issue_create(fields=issue)
            logger.info(f"Created Subtask: {response['key']} - {subtask_data['summary']}")
            return {
                'key': response['key'],
                'self': response['self'],
                'summary': subtask_data['summary']
            }
        except Exception as e:
            logger.error(f"Error creating Subtask: {str(e)}")
            return None

    async def create_issues(self, data: Dict) -> Dict:
        """Create Epics, Stories, and Subtasks in Jira"""
        results = {
            'epics': [],
            'stories': [],
            'subtasks': [],
            'errors': []
        }
        
        try:
            for epic in data.get('epics', []):
                # Create Epic
                epic_result = await self.create_epic(epic)
                if epic_result:
                    results['epics'].append(epic_result)
                    
                    # Create Stories for this Epic
                    for story in epic.get('stories', []):
                        story_result = await self.create_story(story, epic_result['key'])
                        if story_result:
                            results['stories'].append(story_result)
                            
                            # Create Subtasks for this Story
                            for subtask in story.get('subtasks', []):
                                subtask_result = await self.create_subtask(subtask, story_result['key'])
                                if subtask_result:
                                    results['subtasks'].append(subtask_result)
                                else:
                                    results['errors'].append(f"Failed to create subtask: {subtask['summary']}")
                        else:
                            results['errors'].append(f"Failed to create story: {story['summary']}")
                else:
                    results['errors'].append(f"Failed to create epic: {epic['summary']}")
            
            return results
            
        except Exception as e:
            error_msg = f"Error creating issues in Jira: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results