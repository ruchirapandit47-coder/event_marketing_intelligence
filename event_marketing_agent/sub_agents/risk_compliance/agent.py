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

"""Risk & Compliance Agent module for auditing plans and content."""

from google.adk import Event, Context
from pydantic import BaseModel, Field
from ...tools.compliance_tools import evaluate_campaign_risks


class RiskComplianceInput(BaseModel):
    """Input parameters for the Risk & Compliance Agent."""

    event_name: str = Field(description="Name of the event")
    event_type: str = Field(description="Type of the event, e.g. B2B, Developer, Consumer")
    target_audience: str = Field(description="Target audience demographics/roles")
    marketing_budget: float = Field(description="Total marketing budget in USD")
    registration_goal: int = Field(description="Target number of registrations")
    allocations: list[dict] = Field(description="List of budget allocations per channel")
    summary: dict = Field(description="Consolidated budget summary and forecast details")
    email_invitation: str = Field(description="Email invitation copy text")
    linkedin_posts: list[str] = Field(description="LinkedIn post texts")


class ContentAudit(BaseModel):
    """Result of a content compliance check on an asset."""

    item: str = Field(description="Asset name, e.g. Budget Allocations, Target Settings, Email invitation")
    status: str = Field(description="PASSED or FAILED")
    issues: list[str] = Field(description="List of issues identified")


class RiskComplianceOutput(BaseModel):
    """Structured audit report returned by the Risk & Compliance Agent."""

    shortfall_percentage: float = Field(description="Shortfall as percentage of goal")
    risk_category: str = Field(description="Risk categorization: LOW RISK, MEDIUM RISK, or HIGH RISK")
    warnings: list[str] = Field(description="List of compliance warnings generated")
    content_audits: list[ContentAudit] = Field(description="Audits on campaign assets and configurations")
    is_approved: bool = Field(description="True if safe to proceed (LOW RISK), False if HITL approval required (MEDIUM/HIGH RISK)")
    explanation: str = Field(description="Detailed reason for approval decision and risk scoring")
    
    # Enhanced Risk & Compliance fields
    risk_score: float = Field(description="Numerical risk score (0-100)")
    risk_factors: list[str] = Field(description="Detailed explanations of every risk factor")
    corrective_actions: list[str] = Field(description="Recommended corrective actions")
    expected_improvement: dict = Field(description="Estimated improvement if recommendations are followed")


def risk_compliance_agent(node_input: dict, ctx: Context) -> Event:
    """Execute Risk & Compliance Agent checks directly."""
    if hasattr(node_input, "model_dump"):
        node_input = node_input.model_dump()
    elif hasattr(node_input, "dict"):
        node_input = node_input.dict()

    result = evaluate_campaign_risks(
        event_name=node_input["event_name"],
        event_type=node_input["event_type"],
        target_audience=node_input["target_audience"],
        marketing_budget=node_input["marketing_budget"],
        registration_goal=node_input["registration_goal"],
        allocations=node_input["allocations"],
        summary=node_input["summary"]
    )
    return Event(output=result)
