import logging
from typing import Dict, List, Optional, Union
from atlassian import Jira
from config import settings
from fastapi import Request

logger = logging.getLogger(__name__)

class JiraService:
    def __init__(self):
        # Check if JIRA credentials are configured
        if not all([settings.JIRA_URL, settings.JIRA_EMAIL, settings.JIRA_API_TOKEN, settings.JIRA_PROJECT_KEY]):
            logger.warning("JIRA credentials not fully configured. JIRA integration will be disabled.")
            self.jira = None
            self.project_key = None
            self.epic_name_field = None
            self.epic_link_field = None
            self.available_issue_types = []
            self.story_issue_type = None
            self.subtask_issue_type = None
            return
        
        try:
            self.jira = Jira(
                url=settings.JIRA_URL,
                username=settings.JIRA_EMAIL,
                password=settings.JIRA_API_TOKEN,
                cloud=True
            )
            self.project_key = settings.JIRA_PROJECT_KEY
            
            # Get Epic fields from settings or auto-detect
            self.epic_name_field = settings.JIRA_EPIC_NAME_FIELD
            self.epic_link_field = settings.JIRA_EPIC_LINK_FIELD
            
            # Auto-detect if not in settings
            if not self.epic_name_field or not self.epic_link_field:
                self._auto_detect_epic_fields()
            
            self.available_issue_types = self._get_available_issue_types()
            self.story_issue_type = self._detect_story_issue_type()
            self.subtask_issue_type = self._detect_subtask_issue_type()
        except Exception as e:
            logger.error(f"Failed to initialize JIRA service: {str(e)}")
            self.jira = None
            self.project_key = None
            self.epic_name_field = None
            self.epic_link_field = None
            self.available_issue_types = []
            self.story_issue_type = None
            self.subtask_issue_type = None
    
    def _is_configured(self) -> bool:
        """Check if JIRA service is properly configured"""
        return self.jira is not None and self.project_key is not None
        
    def _auto_detect_epic_fields(self):
        """Automatically detect Epic Name and Epic Link field IDs"""
        if not self._is_configured():
            return
            
        try:
            fields = self.jira.get_all_fields()
            
            for field in fields:
                field_name = field.get('name', '').lower()
                field_id = field.get('id', '')
                
                if 'epic name' in field_name and not self.epic_name_field:
                    self.epic_name_field = field_id
                    logger.info(f"Auto-detected Epic Name field: {field_id}")
                
                if 'epic link' in field_name and not self.epic_link_field:
                    self.epic_link_field = field_id
                    logger.info(f"Auto-detected Epic Link field: {field_id}")
            
            if not self.epic_name_field:
                # Try common field IDs
                common_epic_name_ids = [
                    'customfield_10011', 'customfield_10021', 
                    'customfield_10001', 'customfield_10002'
                ]
                for field_id in common_epic_name_ids:
                    try:
                        # Test if field exists
                        test_field = next((f for f in fields if f['id'] == field_id), None)
                        if test_field:
                            self.epic_name_field = field_id
                            logger.warning(f"Using fallback Epic Name field: {field_id}")
                            break
                    except:
                        continue
                        
        except Exception as e:
            logger.error(f"Error detecting Epic fields: {str(e)}")
    
    def _get_epic_link_field(self) -> Optional[str]:
        """Get the custom field ID for Epic Link (used to link stories to epics)"""
        if not self._is_configured():
            return None
            
        # If already detected, return it
        if self.epic_link_field:
            return self.epic_link_field
            
        # First try to get all fields and search for Epic Link
        try:
            all_fields = self.jira.get_all_fields()
            for field in all_fields:
                field_name = field.get('name', '').lower()
                field_id = field.get('id', '')
                schema = field.get('schema', {})
                custom = schema.get('custom', '') if schema else ''
                
                if 'epic link' in field_name or 'epiclink' in field_name or custom.endswith('epiclink'):
                    logger.info(f"Found Epic Link field: {field_id} ({field.get('name')})")
                    self.epic_link_field = field_id
                    return field_id
        except Exception as e:
            logger.debug(f"Error getting all fields: {str(e)}")
        
        # Try to get the create metadata for the project
        try:
            metadata = self.jira.issue_createmeta(
                project=self.project_key,
                expand='projects.issuetypes.fields'
            )
            
            # Find the Epic Link field in the metadata
            if metadata and 'projects' in metadata and metadata['projects']:
                project = metadata['projects'][0]
                if 'issuetypes' in project and project['issuetypes']:
                    # Search through all issue types for Epic Link field
                    for issue_type in project['issuetypes']:
                        if issue_type.get('name') == settings.JIRA_STORY_ISSUE_TYPE:
                            fields = issue_type.get('fields', {})
                            for field_id, field_data in fields.items():
                                field_name = field_data.get('name', '').lower()
                                schema = field_data.get('schema', {})
                                custom = schema.get('custom', '') if schema else ''
                                
                                if 'epic link' in field_name or 'epiclink' in field_name or custom.endswith('epiclink'):
                                    logger.info(f"Found Epic Link field via metadata: {field_id} ({field_data.get('name')})")
                                    self.epic_link_field = field_id
                                    return field_id
            
            logger.warning("Could not determine Epic Link field via metadata, using default fallback")
            self.epic_link_field = 'customfield_10014'  # Most common Epic Link field ID
            return self.epic_link_field
            
        except Exception as e:
            logger.warning(f"Error getting Epic Link field metadata: {str(e)}")
            self.epic_link_field = 'customfield_10014'  # Default fallback
            return self.epic_link_field
    
    def _get_available_issue_types(self) -> List[Dict]:
        """Get all available issue types for the project"""
        if not self._is_configured():
            return []
        try:
            metadata = self.jira.issue_createmeta(
                project=self.project_key,
                expand='projects.issuetypes'
            )
            if metadata and 'projects' in metadata and metadata['projects']:
                project = metadata['projects'][0]
                if 'issuetypes' in project:
                    issue_types = project['issuetypes']
                    logger.info(f"Found {len(issue_types)} issue types: {[it.get('name') for it in issue_types]}")
                    return issue_types
        except Exception as e:
            logger.warning(f"Error getting available issue types: {str(e)}")
        return []
    
    def _detect_story_issue_type(self) -> str:
        """Detect the correct issue type name for stories"""
        if not self._is_configured():
            return settings.JIRA_STORY_ISSUE_TYPE
        # First try the configured value
        configured_type = settings.JIRA_STORY_ISSUE_TYPE
        
        # Check if configured type exists in available types
        for issue_type in self.available_issue_types:
            if issue_type.get('name', '').lower() == configured_type.lower():
                logger.info(f"Using configured Story issue type: {configured_type}")
                return configured_type
        
        # Try common alternatives
        common_story_types = ['Story', 'Task', 'User Story', 'Feature', 'Bug']
        for story_type in common_story_types:
            for issue_type in self.available_issue_types:
                if issue_type.get('name', '').lower() == story_type.lower():
                    logger.info(f"Detected Story issue type: {story_type}")
                    return story_type
        
        # If nothing found, try to find any non-epic, non-subtask issue type
        for issue_type in self.available_issue_types:
            name = issue_type.get('name', '').lower()
            if 'epic' not in name and 'subtask' not in name and 'sub-task' not in name:
                detected = issue_type.get('name')
                logger.warning(f"Could not find Story type, using: {detected}")
                return detected
        
        # Final fallback
        logger.warning(f"Could not detect Story issue type, using default: {configured_type}")
        return configured_type
    
    def _detect_subtask_issue_type(self) -> str:
        """Detect the correct issue type name for subtasks"""
        if not self._is_configured():
            return settings.JIRA_SUBTASK_ISSUE_TYPE
        configured_type = settings.JIRA_SUBTASK_ISSUE_TYPE
        
        # Check if configured type exists
        for issue_type in self.available_issue_types:
            if issue_type.get('name', '').lower() == configured_type.lower():
                logger.info(f"Using configured Subtask issue type: {configured_type}")
                return configured_type
        
        # Try common alternatives
        common_subtask_types = ['Sub-task', 'Subtask', 'Sub task']
        for subtask_type in common_subtask_types:
            for issue_type in self.available_issue_types:
                if issue_type.get('name', '').lower() == subtask_type.lower():
                    logger.info(f"Detected Subtask issue type: {subtask_type}")
                    return subtask_type
        
        logger.warning(f"Could not detect Subtask issue type, using default: {configured_type}")
        return configured_type

    async def create_epic(self, epic_data: Dict) -> Optional[Dict]:
        """Create an Epic in JIRA - optimized for modern JIRA Cloud"""
        if not self._is_configured():
            logger.error("JIRA service is not configured. Please set JIRA credentials in .env file.")
            return None
        
        # Build base issue structure (modern JIRA Cloud approach)
        base_issue = {
            'project': {'key': self.project_key},
            'summary': epic_data['summary'],
            'description': epic_data.get('description', ''),
            'issuetype': {'name': settings.JIRA_EPIC_ISSUE_TYPE}
        }
        
        # Strategy 1: Try direct creation (modern JIRA Cloud doesn't need Epic Name field)
        try:
            response = self.jira.issue_create(fields=base_issue)
            logger.info(f"✓ Created Epic (modern approach): {response['key']} - {epic_data['summary']}")
            return {
                'key': response['key'],
                'self': response['self'],
                'summary': epic_data['summary']
            }
        except Exception as e:
            error_msg = str(e).lower()
            logger.debug(f"Modern Epic creation failed: {str(e)}")
            
            # Strategy 2: Try with Epic Name field if we detected one
            if self.epic_name_field and ('field' in error_msg or 'required' in error_msg):
                try:
                    issue = base_issue.copy()
                    issue[self.epic_name_field] = epic_data['summary']
                    
                    response = self.jira.issue_create(fields=issue)
                    logger.info(f"✓ Created Epic with Epic Name field ({self.epic_name_field}): {response['key']} - {epic_data['summary']}")
                    return {
                        'key': response['key'],
                        'self': response['self'],
                        'summary': epic_data['summary']
                    }
                except Exception as e2:
                    logger.debug(f"Epic creation with Epic Name field failed: {str(e2)}")
            
            # Strategy 3: Try common Epic Name field IDs
            common_field_ids = ['customfield_10011', 'customfield_10012', 'customfield_10013', 'customfield_10021']
            for field_id in common_field_ids:
                if field_id == self.epic_name_field:
                    continue  # Already tried this one
                    
                try:
                    issue = base_issue.copy()
                    issue[field_id] = epic_data['summary']
                    
                    response = self.jira.issue_create(fields=issue)
                    logger.info(f"✓ Created Epic with fallback field ({field_id}): {response['key']} - {epic_data['summary']}")
                    # Cache the working field ID
                    self.epic_name_field = field_id
                    return {
                        'key': response['key'],
                        'self': response['self'],
                        'summary': epic_data['summary']
                    }
                except Exception as fallback_error:
                    logger.debug(f"Fallback field {field_id} failed: {str(fallback_error)}")
                    continue
            
            # All strategies failed
            logger.error(f"✗ All Epic creation strategies failed for '{epic_data['summary']}': {str(e)}")
            return None

    async def create_story(self, story_data: Dict, epic_key: str = None) -> Optional[Dict]:
        """Create a Story in Jira, optionally linked to an epic"""
        if not self._is_configured():
            logger.error("JIRA service is not configured. Please set JIRA credentials in .env file.")
            return None
        try:
            issue = {
                'project': {'key': self.project_key},
                'summary': story_data['summary'],
                'description': story_data.get('description', ''),
                'issuetype': {'name': self.story_issue_type}
            }
            
            # Add priority if provided
            priority = story_data.get('priority')
            if priority:
                issue['priority'] = {'name': priority}
            
            # Link to epic if epic_key is provided and Epic Link field is available
            if epic_key and self.epic_link_field:
                try:
                    issue[self.epic_link_field] = epic_key
                    logger.debug(f"Linking story to epic {epic_key} using field {self.epic_link_field}")
                except Exception as e:
                    logger.warning(f"Could not set Epic Link field: {str(e)}, creating story without epic link")
            
            response = self.jira.issue_create(fields=issue)
            logger.info(f"Created Story: {response['key']} - {story_data['summary']}")
            return {
                'key': response['key'],
                'self': response['self'],
                'summary': story_data['summary']
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error creating Story '{story_data.get('summary', 'Unknown')}': {error_msg}")
            
            # If issue type error, try alternative issue types
            if 'issue type' in error_msg.lower() or 'valid issue type' in error_msg.lower():
                logger.warning(f"Issue type '{self.story_issue_type}' is invalid, trying alternatives...")
                # Try other available issue types (excluding Epic and Subtask)
                for issue_type in self.available_issue_types:
                    type_name = issue_type.get('name', '')
                    type_name_lower = type_name.lower()
                    if 'epic' not in type_name_lower and 'subtask' not in type_name_lower and 'sub-task' not in type_name_lower:
                        if type_name != self.story_issue_type:
                            try:
                                logger.info(f"Trying issue type: {type_name}")
                                issue = {
                                    'project': {'key': self.project_key},
                                    'summary': story_data['summary'],
                                    'description': story_data.get('description', ''),
                                    'issuetype': {'name': type_name}
                                }
                                priority = story_data.get('priority')
                                if priority:
                                    issue['priority'] = {'name': priority}
                                # Try to link to epic if available
                                if epic_key and self.epic_link_field:
                                    issue[self.epic_link_field] = epic_key
                                
                                response = self.jira.issue_create(fields=issue)
                                logger.info(f"Created Story with issue type '{type_name}': {response['key']}")
                                # Update the detected issue type for future use
                                self.story_issue_type = type_name
                                return {
                                    'key': response['key'],
                                    'self': response['self'],
                                    'summary': story_data['summary']
                                }
                            except Exception as e2:
                                logger.debug(f"Failed with issue type '{type_name}': {str(e2)}")
                                continue
            
            # Try different fallback strategies
            fallback_attempts = []
            
            # Strategy 1: Try without priority if priority error
            if 'priority' in error_msg.lower():
                fallback_attempts.append(('without priority', lambda: self._create_story_fallback(
                    story_data, epic_key, include_priority=False
                )))
            
            # Strategy 2: Try without priority
            fallback_attempts.append(('without priority', lambda: self._create_story_fallback(
                story_data, None, include_priority=False
            )))
            
            # Execute fallback attempts
            for attempt_name, attempt_func in fallback_attempts:
                try:
                    logger.warning(f"Trying story creation {attempt_name}")
                    result = attempt_func()
                    if result:
                        logger.info(f"Created Story ({attempt_name}): {result['key']} - {story_data['summary']}")
                        return result
                except Exception as e2:
                    logger.debug(f"Fallback attempt '{attempt_name}' failed: {str(e2)}")
                    continue
            
            return None
    
    def _create_story_fallback(self, story_data: Dict, epic_key: str = None, include_priority: bool = True) -> Optional[Dict]:
        """Helper method for fallback story creation attempts"""
        if not self._is_configured():
            return None
        issue = {
            'project': {'key': self.project_key},
            'summary': story_data['summary'],
            'description': story_data.get('description', ''),
            'issuetype': {'name': self.story_issue_type}
        }
        
        if include_priority:
            priority = story_data.get('priority')
            if priority:
                issue['priority'] = {'name': priority}
        
        # Try to link to epic if available
        if epic_key and self.epic_link_field:
            issue[self.epic_link_field] = epic_key
        
        response = self.jira.issue_create(fields=issue)
        return {
            'key': response['key'],
            'self': response['self'],
            'summary': story_data['summary']
        }

    async def create_subtask(self, subtask_data: Dict, parent_key: str) -> Optional[Dict]:
        """Create a Subtask in Jira"""
        if not self._is_configured():
            logger.error("JIRA service is not configured. Please set JIRA credentials in .env file.")
            return None
        try:
            issue = {
                'project': {'key': self.project_key},
                'summary': subtask_data['summary'],
                'description': subtask_data.get('description', ''),
                'issuetype': {'name': self.subtask_issue_type},
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

    async def create_issues(self, data: Dict, request_obj: Request = None) -> Dict:
        """Create Epics, Stories, and Subtasks in Jira with cancellation support"""
        results = {
            'epics': [],
            'stories': [],
            'subtasks': [],
            'errors': []
        }
        
        try:
            for epic in data.get('epics', []):
                # Check for cancellation
                if request_obj and await request_obj.is_disconnected():
                    logger.info("Client disconnected, cancelling ticket creation")
                    results['errors'].append("Ticket creation was cancelled by client")
                    return results
                
                # Create Epic
                epic_result = await self.create_epic(epic)
                if epic_result:
                    results['epics'].append(epic_result)
                    
                    # Create Stories for this Epic, linked to epic
                    epic_key = epic_result['key']
                    for story in epic.get('stories', []):
                        # Check for cancellation
                        if request_obj and await request_obj.is_disconnected():
                            logger.info("Client disconnected, cancelling ticket creation")
                            results['errors'].append("Ticket creation was cancelled by client")
                            return results
                        
                        story_result = await self.create_story(story, epic_key)  # Link to epic
                        if story_result:
                            results['stories'].append(story_result)
                            
                            # Create Subtasks for this Story
                            for subtask in story.get('subtasks', []):
                                # Check for cancellation
                                if request_obj and await request_obj.is_disconnected():
                                    logger.info("Client disconnected, cancelling ticket creation")
                                    results['errors'].append("Ticket creation was cancelled by client")
                                    return results
                                
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