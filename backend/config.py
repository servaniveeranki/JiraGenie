from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # JIRA settings (optional - only needed for JIRA integration)
    JIRA_URL: Optional[str] = Field(default=None, env="JIRA_URL")
    JIRA_EMAIL: Optional[str] = Field(default=None, env="JIRA_EMAIL")
    JIRA_API_TOKEN: Optional[str] = Field(default=None, env="JIRA_API_TOKEN")
    JIRA_PROJECT_KEY: Optional[str] = Field(default=None, env="JIRA_PROJECT_KEY")
    JIRA_EPIC_ISSUE_TYPE: str = Field(default="Epic", env="JIRA_EPIC_ISSUE_TYPE")
    JIRA_STORY_ISSUE_TYPE: str = Field(default="Story", env="JIRA_STORY_ISSUE_TYPE")
    JIRA_SUBTASK_ISSUE_TYPE: str = Field(default="Sub-task", env="JIRA_SUBTASK_ISSUE_TYPE")
    # Google AI API Key (required for ticket generation)
    GOOGLE_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file

# Try to load settings, but don't fail if some are missing
try:
    settings = Settings()
except Exception as e:
    # If loading fails, create settings with defaults
    import os
    settings = Settings(
        GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY"),
        JIRA_URL=os.getenv("JIRA_URL"),
        JIRA_EMAIL=os.getenv("JIRA_EMAIL"),
        JIRA_API_TOKEN=os.getenv("JIRA_API_TOKEN"),
        JIRA_PROJECT_KEY=os.getenv("JIRA_PROJECT_KEY"),
    )
