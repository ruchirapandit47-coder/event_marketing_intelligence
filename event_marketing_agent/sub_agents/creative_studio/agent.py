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
    risk_assessment: dict = Field(default={}, description="Audit risk assessment parameters")


class AdHeadline(BaseModel):
    """Headline copy associated with a channel."""

    channel: str = Field(description="Marketing channel name")
    headline: str = Field(description="Ad headline copy")


class StrategicRecommendation(BaseModel):
    """A creative or copy recommendation coupled with its target audience fit reasoning."""

    recommendation: str = Field(description="The creative content or strategy recommendation")
    reasoning: str = Field(description="Why this recommendation fits the target audience")


class CreativeStudioOutput(BaseModel):
    """Structured copywriting assets produced by the Creative Studio Agent."""

    instagram_captions: list[str] = Field(description="Generated Instagram captions")
    linkedin_posts: list[str] = Field(description="Generated LinkedIn posts")
    email_invitation: str = Field(description="Generated email invitation copy")
    ad_headlines: list[AdHeadline] = Field(description="Ad headlines for each channel")
    call_to_action: list[str] = Field(description="Call-to-action suggestions")
    hashtags: list[str] = Field(description="Hashtag recommendations")

    # Enhanced strategy fields
    campaign_theme: StrategicRecommendation = Field(description="Campaign theme and why it fits the selected audience")
    messaging_strategy: StrategicRecommendation = Field(description="Messaging strategy and why it fits the selected audience")
    audience_positioning: StrategicRecommendation = Field(description="Audience positioning and why it fits the selected audience")
    instagram_caption: StrategicRecommendation = Field(description="Instagram caption and why it fits the selected audience")
    linkedin_post: StrategicRecommendation = Field(description="LinkedIn post and why it fits the selected audience")
    email_copy: StrategicRecommendation = Field(description="Email invitation copy and why it fits the selected audience")
    google_ads_headline: StrategicRecommendation = Field(description="Google Ads headline and why it fits the selected audience")
    success_kpis: list[StrategicRecommendation] = Field(description="Success KPIs and why they fit the selected audience")
    messaging_alignment_confidence: float = Field(description="Confidence score that selected messaging aligns with target audience (0-100)")


def mock_asset_generation(event_name, event_type, theme, target_audience, channels, risk_assessment=None):
    """Local generator for creative copywriting assets and strategy, adapted based on audit risk checks."""
    risk_assessment = risk_assessment or {}
    risk_score = risk_assessment.get("risk_score", 0.0)
    warnings = risk_assessment.get("warnings", [])

    # 1. Campaign Theme (with fit rationale)
    campaign_theme_rec = f"Theme: '{theme}'"
    campaign_theme_reason = f"Addresses primary professional interests of {target_audience}, providing direct value."
    
    # 2. Messaging Strategy (with fit rationale, dynamically adapted by risk results)
    messaging_strategy_rec = "Focus on actionable growth and technology integration."
    messaging_strategy_reason = f"{target_audience} values practical knowledge and case studies over generic theory."
    
    if risk_score > 35.0:
        messaging_strategy_rec += " Mitigate shortfall risk by prioritizing low-cost organic email list referral loops."
        messaging_strategy_reason += " Adjusts to address strict budget limitations flagged by the risk compliance audit."
    elif warnings:
        messaging_strategy_rec += " Adjust messaging to emphasize lower Cost-Per-Registration campaigns."
        messaging_strategy_reason += " Helps buffer the target CPA deviations flagged during risk review."

    # 3. Audience Positioning (with fit rationale)
    audience_positioning_rec = f"Position the event as the premier gathering for {target_audience} in this region."
    audience_positioning_reason = "Emphasizing exclusivity and industry-peer networking builds FOMO, which drives conversions."
    
    # 4. Instagram Caption (with fit rationale)
    instagram_caption_rec = f"Ready to unlock the future of '{theme}'? Join us at '{event_name}'! Connect with leading experts. Link in bio! 📲 #{event_type.lower()}"
    instagram_caption_reason = f"Instagram's visual format combined with hashtags engages {target_audience} actively looking for trending topics."
    
    # 5. LinkedIn Post (with fit rationale)
    linkedin_post_rec = f"Announcing '{event_name}'! We are bringing together leading minds to discuss '{theme}'. Gain actionable strategies and network with other {target_audience} professionals. Register today! 👉 [Link]"
    linkedin_post_reason = f"LinkedIn's professional user base of {target_audience} expects structured value pillars and networking opportunities."
    
    # 6. Email Invitation (with fit rationale)
    email_invitation_rec = (
        f"Subject: Exclusive Invitation: {event_name} - {theme[:40]}...\n\n"
        f"Dear Colleague,\n\n"
        f"We are pleased to invite you to '{event_name}', an exclusive gathering for {target_audience} "
        f"focused on '{theme}'.\n\nWarm regards,\nThe Event Organizing Committee"
    )
    email_invitation_reason = f"Direct email offers a personal invite format that resonates with {target_audience} who prioritize curated calendars."
    
    # 7. Google Ads Headline (with fit rationale)
    google_ads_headline_rec = f"Register for {event_name} | {theme[:20]}"
    google_ads_headline_reason = f"Google Search ads capture intent-driven searches from {target_audience} actively looking for resource topics."

    return {
        # Structured strategy outputs
        "campaign_theme": {
            "recommendation": campaign_theme_rec,
            "reasoning": campaign_theme_reason
        },
        "messaging_strategy": {
            "recommendation": messaging_strategy_rec,
            "reasoning": messaging_strategy_reason
        },
        "audience_positioning": {
            "recommendation": audience_positioning_rec,
            "reasoning": audience_positioning_reason
        },
        "instagram_caption": {
            "recommendation": instagram_caption_rec,
            "reasoning": instagram_caption_reason
        },
        "linkedin_post": {
            "recommendation": linkedin_post_rec,
            "reasoning": linkedin_post_reason
        },
        "email_copy": {
            "recommendation": email_invitation_rec,
            "reasoning": email_invitation_reason
        },
        "google_ads_headline": {
            "recommendation": google_ads_headline_rec,
            "reasoning": google_ads_headline_reason
        },
        "success_kpis": [
            {
                "recommendation": "Registration conversion rate from professional posts (Target: > 8%)",
                "reasoning": f"Fits {target_audience}'s social sign-up patterns."
            },
            {
                "recommendation": "Email RSVP confirmation click-through (Target: > 15%)",
                "reasoning": f"Fits {target_audience}'s inbox responsiveness."
            }
        ],
        
        # UI backward-compatible fields
        "instagram_captions": [f"{instagram_caption_rec}\n\nFit Rationale: {instagram_caption_reason}"],
        "linkedin_posts": [f"{linkedin_post_rec}\n\nFit Rationale: {linkedin_post_reason}"],
        "email_invitation": f"{email_invitation_rec}\n\nFit Rationale: {email_invitation_reason}",
        "ad_headlines": [{"channel": "Google Search Ads", "headline": google_ads_headline_rec}],
        "call_to_action": [
            f"Register Now (Direct & high-intent, fits {target_audience} preferences)",
            f"Confirm RSVP (Exclusivity-based, fits curated calendar preferences)"
        ],
        "hashtags": [f"#{event_type.lower()}", f"#{theme.replace(' ', '').lower()}"],
        "messaging_alignment_confidence": round(min(98.0, 85.0 + len(target_audience) * 0.2), 1)
    }


def validate_creative_output(node_input: dict, result: dict) -> dict:
    """Self-review step: Verify every selected marketing channel has corresponding creative assets (ad headlines)."""
    channels = node_input.get("channels", [])
    ad_headlines = result.get("ad_headlines", [])

    # Map existing headlines by channel name
    channels_with_headlines = {h.get("channel") if isinstance(h, dict) else h.channel for h in ad_headlines}
    
    for channel in channels:
        if channel not in channels_with_headlines:
            # Regenerate only the missing section: add a baseline headline for this channel
            ad_headlines.append({
                "channel": channel,
                "headline": f"Discover {node_input.get('event_name', 'Event')} | Focused on {node_input.get('theme', 'our theme')}"
            })
            
    result["ad_headlines"] = ad_headlines
    return result


def creative_studio_agent(node_input: dict, ctx: Context) -> Event:
    """Execute Creative Studio Agent calculations directly with self-review validation."""
    if hasattr(node_input, "model_dump"):
        node_input = node_input.model_dump()
    elif hasattr(node_input, "dict"):
        node_input = node_input.dict()

    result = mock_asset_generation(
        event_name=node_input["event_name"],
        event_type=node_input["event_type"],
        theme=node_input["theme"],
        target_audience=node_input["target_audience"],
        channels=node_input["channels"],
        risk_assessment=node_input.get("risk_assessment", {})
    )
    
    # Run self-validation review
    validated_result = validate_creative_output(node_input, result)
    
    return Event(output=validated_result)
