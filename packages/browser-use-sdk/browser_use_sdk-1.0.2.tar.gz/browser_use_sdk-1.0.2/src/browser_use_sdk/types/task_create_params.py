# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["TaskCreateParams", "AgentSettings", "BrowserSettings"]


class TaskCreateParams(TypedDict, total=False):
    task: Required[str]

    agent_settings: Annotated[AgentSettings, PropertyInfo(alias="agentSettings")]
    """Configuration settings for the agent

    Attributes: llm: The LLM model to use for the agent start_url: Optional URL to
    start the agent on (will not be changed as a step) profile_id: Unique identifier
    of the agent profile to use for the task
    """

    browser_settings: Annotated[BrowserSettings, PropertyInfo(alias="browserSettings")]
    """Configuration settings for the browser session

    Attributes: session_id: Unique identifier of existing session to continue
    profile_id: Unique identifier of browser profile to use (use if you want to
    start a new session)
    """

    included_file_names: Annotated[Optional[List[str]], PropertyInfo(alias="includedFileNames")]

    metadata: Optional[Dict[str, str]]

    secrets: Optional[Dict[str, str]]

    structured_output_json: Annotated[Optional[str], PropertyInfo(alias="structuredOutputJson")]


class AgentSettings(TypedDict, total=False):
    llm: Literal[
        "gpt-4.1",
        "gpt-4.1-mini",
        "o4-mini",
        "o3",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "claude-sonnet-4-20250514",
        "gpt-4o",
        "gpt-4o-mini",
        "llama-4-maverick-17b-128e-instruct",
        "claude-3-7-sonnet-20250219",
    ]

    profile_id: Annotated[Optional[str], PropertyInfo(alias="profileId")]

    start_url: Annotated[Optional[str], PropertyInfo(alias="startUrl")]


class BrowserSettings(TypedDict, total=False):
    profile_id: Annotated[Optional[str], PropertyInfo(alias="profileId")]

    session_id: Annotated[Optional[str], PropertyInfo(alias="sessionId")]
