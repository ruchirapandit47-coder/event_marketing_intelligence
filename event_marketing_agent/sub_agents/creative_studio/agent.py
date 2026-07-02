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

    # Enhanced strategy fields
    campaign_theme: str = Field(description="Campaign theme and why it fits the selected audience")
    messaging_strategy: str = Field(description="Messaging strategy and why it fits the selected audience")
    audience_positioning: str = Field(description="Audience positioning and why it fits the selected audience")
    instagram_caption: str = Field(description="Instagram caption and why it fits the selected audience")
    linkedin_post: str = Field(description="LinkedIn post and why it fits the selected audience")
    email_copy: str = Field(description="Email invitation copy and why it fits the selected audience")
    google_ads_headline: str = Field(description="Google Ads headline and why it fits the selected audience")
    success_kpis: list[str] = Field(description="Success KPIs and why they fit the selected audience")


def mock_asset_generation(event_name, event_type, theme, target_audience, channels):
    """Local generator for creative copywriting assets and strategy."""
    # 1. Campaign Theme (with fit rationale)
    campaign_theme = (
        f"Theme: '{theme}'. "
        f"Fit Rationale: This theme is designed for {target_audience} because it addresses their primary professional interests, "
        f"providing direct value and networking opportunities tailored to their goals."
    )
    
    # 2. Messaging Strategy (with fit rationale)
    messaging_strategy = (
        f"Strategy: Focus on actionable growth and technology integration. "
        f"Fit Rationale: {target_audience} values practical knowledge and case studies over generic theory. "
        f"Positioning the messaging around concrete takeaways maximizes interest and registration intent."
    )
    
    # 3. Audience Positioning (with fit rationale)
    audience_positioning = (
        f"Positioning: Position the event as the premier gathering for {target_audience} in this region. "
        f"Fit Rationale: Emphasizing exclusivity and industry-peer networking builds FOMO (Fear Of Missing Out) "
        f"which drives conversions for {target_audience}."
    )
    
    # 4. Instagram Caption (with fit rationale)
    instagram_caption_str = (
        f"Caption: Ready to unlock the future of '{theme}'? Join us at '{event_name}'! "
        f"Connect with leading experts and peers. Link in bio! 📲 #{event_type.lower()}\n\n"
        f"Fit Rationale: Instagram's visual format combined with a strong direct hook engages {target_audience} "
        f"who search for trending topics via hashtags and interactive bio links."
    )
    
    # 5. LinkedIn Post (with fit rationale)
    linkedin_post_str = (
        f"Post: Announcing '{event_name}'! We are bringing together leading minds to discuss '{theme}'.\n\n"
        f"Key Takeaways:\n"
        f"• Network with other {target_audience} professionals.\n"
        f"• Gain actionable strategies on modern frameworks.\n"
        f"• Participate in live developer Q&As.\n\n"
        f"👉 Register today: [Link]\n\n"
        f"Fit Rationale: LinkedIn's professional user base of {target_audience} expects structured, bulleted value pillars "
        f"and networking-centric copy."
    )
    
    # 6. Email Invitation (with fit rationale)
    email_invitation_str = (
        f"Subject: Exclusive Invitation: {event_name} - {theme[:40]}...\n\n"
        f"Dear Colleague,\n\n"
        f"We are pleased to invite you to '{event_name}', an exclusive gathering for {target_audience} "
        f"focused on '{theme}'.\n\n"
        f"Event details:\n"
        f"• Event: {event_name}\n"
        f"• Main Topic: {theme}\n\n"
        f"Warm regards,\nThe Event Organizing Committee\n\n"
        f"Fit Rationale: Direct email offers a personal invite format that resonates with {target_audience} "
        f"who prioritize curated calendars and private invitations."
    )
    
    # 7. Google Ads Headline (with fit rationale)
    google_ads_headline_str = (
        f"Headline: Register for {event_name} | {theme[:20]}\n\n"
        f"Fit Rationale: Google Search ads capture intent-driven searches from {target_audience} "
        f"actively looking for resource topics related to '{theme}'."
    )

    return {
        # Structured strategy outputs
        "campaign_theme": campaign_theme,
        "messaging_strategy": messaging_strategy,
        "audience_positioning": audience_positioning,
        "instagram_caption": instagram_caption_str,
        "linkedin_post": linkedin_post_str,
        "email_copy": email_invitation_str,
        "google_ads_headline": google_ads_headline_str,
        "success_kpis": [
            f"Registration conversion rate from professional posts (Target: > 8%). Fits {target_audience}'s social sign-up patterns.",
            f"Email RSVP confirmation click-through (Target: > 15%). Fits {target_audience}'s inbox responsiveness."
        ],
        
        # UI backward-compatible fields
        "instagram_captions": [instagram_caption_str],
        "linkedin_posts": [linkedin_post_str],
        "email_invitation": email_invitation_str,
        "ad_headlines": [{"channel": "Google Search Ads", "headline": f"Register for {event_name}"}],
        "call_to_action": [
            f"Register Now (Direct & high-intent, fits {target_audience} preferences)",
            f"Confirm RSVP (Exclusivity-based, fits curated calendar preferences)"
        ],
        "hashtags": [f"#{event_type.lower()}", f"#{theme.replace(' ', '').lower()}"]
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
