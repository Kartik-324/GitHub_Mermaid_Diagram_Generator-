# backend/models.py - COMPLETE
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class DiagramRequest(BaseModel):
    """Request model for generating specific diagram types"""
    repo_url: str = Field(..., description="GitHub repository URL")
    diagram_type: Literal[
        "sequence", 
        "component", 
        "database", 
        "flowchart", 
        "class", 
        "state", 
        "journey", 
        "gantt", 
        "mindmap"
    ] = Field(..., description="Type of diagram to generate")
    github_token: Optional[str] = Field(None, description="GitHub personal access token for private repos")

class CustomDiagramRequest(BaseModel):
    """Request model for custom diagram generation"""
    repo_url: str = Field(..., description="GitHub repository URL")
    user_prompt: str = Field(..., description="User's custom prompt for diagram generation")
    diagram_type: Optional[str] = Field(None, description="Optional diagram type hint")
    github_token: Optional[str] = Field(None, description="GitHub personal access token for private repos")

class DiagramResponse(BaseModel):
    """Response model for diagram generation"""
    mermaid_code: str = Field(..., description="Generated Mermaid diagram code")
    diagram_type: str = Field(..., description="Type of diagram generated")
    repo_name: str = Field(..., description="Repository name")

class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """Request model for chat interaction"""
    repo_url: str = Field(..., description="GitHub repository URL")
    question: str = Field(..., description="User's question or request")
    chat_history: Optional[List[ChatMessage]] = Field(
        default_factory=list, 
        description="Previous chat messages for context"
    )
    github_token: Optional[str] = Field(None, description="GitHub personal access token for private repos")
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    """Response model for chat interaction"""
    answer: str = Field(..., description="AI assistant's answer")
    repo_name: str = Field(..., description="Repository name")
    has_diagram: bool = Field(default=False, description="Whether response includes a diagram")
    mermaid_code: Optional[str] = Field(None, description="Mermaid diagram code if generated")
    diagram_type: Optional[str] = Field(None, description="Type of diagram if generated")
    follow_up_questions: Optional[List[str]] = Field(
        default_factory=list, 
        description="Suggested follow-up questions"
    )