from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JIRA_URL: str = Field(..., env="JIRA_URL")
    JIRA_EMAIL: str = Field(..., env="JIRA_EMAIL")
    JIRA_API_TOKEN: str = Field(..., env="JIRA_API_TOKEN")
    JIRA_PROJECT_KEY: str = Field(..., env="JIRA_PROJECT_KEY")
    JIRA_EPIC_ISSUE_TYPE: str = Field(default="Epic", env="JIRA_EPIC_ISSUE_TYPE")
    JIRA_STORY_ISSUE_TYPE: str = Field(default="Story", env="JIRA_STORY_ISSUE_TYPE")
    JIRA_SUBTASK_ISSUE_TYPE: str = Field(default="Sub-task", env="JIRA_SUBTASK_ISSUE_TYPE")
    GOOGLE_API_KEY: str = Field(..., env="GOOGLE_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
