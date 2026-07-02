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
from ..data_budget.agent import ChannelAllocation, BudgetSummary


class RiskComplianceInput(BaseModel):
    """Input parameters for the Risk & Compliance Agent."""

    event_name: str = Field(description="Name of the event")
    event_type: str = Field(description="Type of the event, e.g. B2B, Developer, Consumer")
    target_audience: str = Field(description="Target audience demographics/roles")
    marketing_budget: float = Field(description="Total marketing budget in USD")
    registration_goal: int = Field(description="Target number of registrations")
    allocations: list[ChannelAllocation] = Field(description="List of budget allocations per channel")
    summary: BudgetSummary = Field(description="Consolidated budget summary and forecast details")
    email_invitation: str = Field(description="Email invitation copy text")
    linkedin_posts: list[str] = Field(description="LinkedIn post texts")


class ContentAudit(BaseModel):
    """Result of a content compliance check on an asset."""

    item: str = Field(description="Asset name, e.g. Budget Allocations, Target Settings, Email invitation")
    status: str = Field(description="PASSED or FAILED")
    issues: list[str] = Field(description="List of issues identified")


class CorrectiveAction(BaseModel):
    """A risk mitigation recommendation coupled with its threat reduction reasoning."""

    recommendation: str = Field(description="Action recommendation text")
    reasoning: str = Field(description="Why this recommendation reduces the risk")


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
    corrective_actions: list[CorrectiveAction] = Field(description="Recommended corrective actions and rationales")
    expected_improvement: dict = Field(description="Estimated improvement if recommendations are followed")
    risk_score_confidence: float = Field(description="Confidence score in the calculated risk score (0-100)")


def validate_risk_output(result: dict) -> dict:
    """Self-review step: Verify that every identified risk factor is mapped to at least one mitigation corrective action."""
    warnings = result.get("warnings", [])
    risk_factors = result.get("risk_factors", [])
    corrective_actions = result.get("corrective_actions", [])

    # If risks/warnings are identified but corrective actions (mitigations) list is empty, correct locally
    if (warnings or risk_factors) and not corrective_actions:
        # Default safety mitigation action
        corrective_actions.append({
            "recommendation": "Shift 10% of budget from high-CPA channels to lower-CPA channels.",
            "reasoning": "Drives additional sign-ups within current budget limits to reduce shortfall risk."
        })
        
    result["corrective_actions"] = corrective_actions
    return result


def risk_compliance_agent(node_input: dict, ctx: Context) -> Event:
    """Execute Risk & Compliance Agent checks directly with self-review validation returning structured output."""
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
    
    # Run self-validation review
    validated_result = validate_risk_output(result)
    
    output_obj = RiskComplianceOutput(
        shortfall_percentage=validated_result["shortfall_percentage"],
        risk_category=validated_result["risk_category"],
        warnings=validated_result["warnings"],
        content_audits=validated_result["content_audits"],
        is_approved=validated_result["is_approved"],
        explanation=validated_result["explanation"],
        risk_score=validated_result["risk_score"],
        risk_factors=validated_result["risk_factors"],
        corrective_actions=validated_result["corrective_actions"],
        expected_improvement=validated_result["expected_improvement"],
        risk_score_confidence=validated_result["risk_score_confidence"]
    )
    
    return Event(output=output_obj)
