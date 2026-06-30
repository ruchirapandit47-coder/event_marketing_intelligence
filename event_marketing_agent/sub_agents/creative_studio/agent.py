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

from google.adk import Agent
from pydantic import BaseModel, Field

from ...config import config
from .prompt import CREATIVE_STUDIO_INSTRUCTION


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


# Instantiation of the Creative Studio Agent
creative_studio_agent = Agent(
    name="creative_studio_agent",
    model=config.model,
    mode="single_turn",
    instruction=CREATIVE_STUDIO_INSTRUCTION,
    input_schema=CreativeStudioInput,
    output_schema=CreativeStudioOutput,
)
