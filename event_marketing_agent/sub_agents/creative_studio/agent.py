# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Creative Studio Agent module for generating campaign assets."""

from google.adk import Event, Context
from pydantic import BaseModel, Field


class CreativeStudioInput(BaseModel):
    """Input parameters for the Creative Studio Agent."""

    event_name: str = Field(description="Name of the event")
    event_type: str = Field(description="Type of the event, e.g. B2B, Developer, Consumer")
    theme: str = Field(description="Theme or description of the event")
    target_audience: str = Field(description="Target audience demographics/roles")
    channels: list[str] = Field(description="List of marketing channels that were recommended")


class AdHeadline(BaseModel):
    """Headline copy associated with a channel."""

    channel: str = Field(description="Marketing channel name")
    headline: str = Field(description="Ad headline copy")


class CreativeStudioOutput(BaseModel):
    """Structured copywriting assets produced by the Creative Studio Agent."""

    instagram_captions: list[str] = Field(description="Generated Instagram captions")
    linkedin_posts: list[str] = Field(description="Generated LinkedIn posts")
    email_invitation: str = Field(description="Generated email invitation copy")
    ad_headlines: list[AdHeadline] = Field(description="Ad headlines for each channel")
    call_to_action: list[str] = Field(description="Call-to-action suggestions")
    hashtags: list[str] = Field(description="Hashtag recommendations")


def mock_asset_generation(event_name, event_type, theme, target_audience, channels):
    """Local generator for creative copywriting assets."""
    return {
        "instagram_captions": [f"Join us at {event_name}! #{event_type.lower()}"],
        "linkedin_posts": [f"Learn about {theme} at {event_name}."],
        "email_invitation": f"Subject: Invite to {event_name}\n\nDear [Name],\n\nWelcome to {event_name}.",
        "ad_headlines": [{"channel": c, "headline": f"Join {event_name}"} for c in channels],
        "call_to_action": ["Register Now"],
        "hashtags": [f"#{event_type.lower()}"]
    }


def creative_studio_agent(node_input: dict, ctx: Context) -> Event:
    """Execute Creative Studio Agent calculations directly."""
    if hasattr(node_input, "model_dump"):
        node_input = node_input.model_dump()
    elif hasattr(node_input, "dict"):
        node_input = node_input.dict()

    result = mock_asset_generation(
        event_name=node_input["event_name"],
        event_type=node_input["event_type"],
        theme=node_input["theme"],
        target_audience=node_input["target_audience"],
        channels=node_input["channels"]
    )
    return Event(output=result)
