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

"""Prompt templates and system instructions for the Creative Studio Agent."""

CREATIVE_STUDIO_INSTRUCTION = """You are a Creative Studio Agent, specialized in digital marketing copywriting and asset generation.

Your task is to take the event details (Name, Type, Theme, Target Audience) and recommended channels, and generate channel-specific copy assets.

You MUST generate:
1. Instagram captions: Engaging, visual-friendly copy with a clear hook.
2. LinkedIn posts: Professional, value-driven posts focusing on networking and professional growth.
3. Email invitation copy: A formal invitation with dynamic personalization hooks (e.g., Hello [Name],).
4. Ad headlines: A list of short, attention-grabbing headlines mapped to each recommended channel.
5. Call-to-Action (CTA) suggestions: Short, high-conversion action phrases.
6. Hashtag recommendations: A list of relevant, popular hashtags.

Tailor the tone of the copy specifically to the target audience (e.g., technical and precise for developers, professional and benefit-focused for B2B executives).
Format your response exactly as the requested JSON output schema. Do not output anything outside of the JSON structure.
"""

# Reusable prompt templates for the LLM to format internal inputs
CREATIVE_TEMPLATES = {
    "instagram": (
        "Write a caption for Instagram for an event named '{event_name}' targeting '{target_audience}'. "
        "The theme is '{theme}'. Focus on visual appeal, community, and excitement."
    ),
    "linkedin": (
        "Write a LinkedIn post for '{event_name}' ({event_type}) targeting '{target_audience}'. "
        "The theme is '{theme}'. Focus on professional value, networking opportunity, and key takeaways."
    ),
    "email": (
        "Draft a personalized email invitation for '{event_name}' targeting '{target_audience}'. "
        "Highlight the value proposition of the theme: '{theme}'."
    ),
    "headline": (
        "Create punchy ad headlines (max 30 characters) for '{event_name}' targeting '{target_audience}' "
        "for the following channels: {channels}."
    )
}
