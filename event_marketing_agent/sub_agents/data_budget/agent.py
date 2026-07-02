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

"""Data & Budget Agent module for allocating budget and forecasting registrations."""

from google.adk import Event, Context
from pydantic import BaseModel, Field
from ...tools.budget_tools import recommend_channels_and_allocate_budget


class DataBudgetInput(BaseModel):
    """Inputs required by the Data & Budget agent."""

    event_name: str = Field(description="Name of the event")
    event_type: str = Field(description="Type of the event, e.g. B2B, Developer, Consumer, Academic")
    location: str = Field(description="Location of the event (e.g. San Francisco, Virtual, Hybrid)")
    target_audience: str = Field(description="Target audience demographics or job roles")
    marketing_budget: float = Field(description="Total marketing budget in USD")
    registration_goal: int = Field(description="Target number of registrations")
    apply_optimization: bool = Field(default=False, description="If True, apply shift optimizations to the budget split directly.")


class ChannelAllocation(BaseModel):
    """Details of budget allocated to a single channel."""

    channel: str = Field(description="Name of the marketing channel")
    allocation_ratio: float = Field(description="Ratio of total budget allocated")
    budget: float = Field(description="Budget in USD allocated to this channel")
    cost_per_registration: float = Field(description="Cost per registration benchmark")
    estimated_registrations: int = Field(description="Number of registrations estimated from this channel")
    description: str = Field(description="Brief channel explanation")
    selection_rationale: str = Field(description="Why this channel was selected")


class BudgetSummary(BaseModel):
    """Consolidated budget metrics and feasibility results."""

    total_budget: float = Field(description="Total marketing budget in USD")
    total_estimated_registrations: int = Field(description="Total estimated registrations across all channels")
    average_cost_per_registration: float = Field(description="Overall cost per registration")
    registration_goal: int = Field(description="Target registration goal")
    registration_gap: int = Field(description="Difference between goal and estimate (0 if goal met)")
    feasibility_status: str = Field(description="FEASIBLE or RISKY")
    feasibility_message: str = Field(description="Message describing the feasibility of the campaign")
    confidence_score: float = Field(description="Confidence score in percent (e.g. 82.0 for 82%)")
    optimization_recommendation: str = Field(description="Optimization suggestions to improve feasibility")
    
    # Enterprise Decision Support System extensions
    forecast_confidence: dict = Field(description="Details on forecast confidence score and level")
    registration_gap_analysis: dict = Field(description="Details on gap amount and percentage")
    reallocation_recommendations: list[dict] = Field(description="Recommended shifts to bridge gaps")
    improvement_estimate: dict = Field(description="Estimated metrics after executing suggestions")


class DataBudgetOutput(BaseModel):
    """Structured output schema returned by the Data & Budget agent."""

    event_name: str = Field(description="Name of the event")
    event_type: str = Field(description="Type of the event")
    location: str = Field(description="Location of the event")
    target_audience: str = Field(description="Target audience demographics or job roles")
    allocations: list[ChannelAllocation] = Field(description="List of budget allocations per channel")
    summary: BudgetSummary = Field(description="Consolidated budget allocation summary and forecast")


def data_budget_agent(node_input: dict, ctx: Context) -> Event:
    """Execute Data & Budget Agent calculations directly."""
    if hasattr(node_input, "model_dump"):
        node_input = node_input.model_dump()
    elif hasattr(node_input, "dict"):
        node_input = node_input.dict()

    result = recommend_channels_and_allocate_budget(
        event_type=node_input["event_type"],
        target_audience=node_input["target_audience"],
        marketing_budget=node_input["marketing_budget"],
        registration_goal=node_input["registration_goal"],
        apply_optimization=node_input.get("apply_optimization", False)
    )
    return Event(output=result)
