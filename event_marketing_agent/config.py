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

"""Centralized configuration for the event marketing intelligence agent."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# --- Authentication ---
# If GOOGLE_API_KEY is set, use Gemini API Developer key.
# Otherwise, fall back to Vertex AI with Google Cloud Application Default Credentials.
if os.getenv("GOOGLE_API_KEY"):
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")
else:
    try:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError
        
        try:
            _, project_id = google.auth.default()
            os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id or "")
            os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
            os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
        except DefaultCredentialsError:
            # Fallback when credentials are not found
            os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "mock-project")
            os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
            os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
    except ImportError:
        pass


@dataclass
class EventMarketingAgentConfig:
    """Agent configurations."""

    model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


config = EventMarketingAgentConfig()
