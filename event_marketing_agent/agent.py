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

"""Workflow definition for the Event Marketing Intelligence Director Agent."""

from google.adk import Context, Event, Workflow
from google.adk.events import RequestInput

from .sub_agents import (
    creative_studio_agent,
    data_budget_agent,
    risk_compliance_agent,
)


# ---------------------------------------------------------------------------
# Workflow Orchestration Nodes
# ---------------------------------------------------------------------------


def parse_brief(node_input: dict, ctx: Context) -> Event:
    """Parse raw brief input and initialize campaign parameters in state."""
    ctx.state["event_name"] = node_input.get("event_name", "Global Seminar")
    ctx.state["event_type"] = node_input.get("event_type", "B2B")
    ctx.state["location"] = node_input.get("location", "Virtual")
    ctx.state["target_audience"] = node_input.get("target_audience", "Professionals")
    ctx.state["marketing_budget"] = float(node_input.get("marketing_budget", 10000.0))
    ctx.state["registration_goal"] = int(node_input.get("registration_goal", 100))
    ctx.state["theme"] = node_input.get("theme", "Growth and Networking")
    
    # Initialize the optimization flag as False initially
    ctx.state["apply_optimization_directly"] = False

    return Event(output=node_input)


def goal_analysis(node_input: dict, ctx: Context) -> Event:
    """Perform campaign goal analysis and calculate limits."""
    budget = ctx.state["marketing_budget"]
    goal = ctx.state["registration_goal"]
    target_cpa_limit = budget / goal if goal > 0 else 0.0
    ctx.state["target_cpa_limit"] = target_cpa_limit

    # Prepare input for the Data & Budget agent
    db_input = {
        "event_name": ctx.state["event_name"],
        "event_type": ctx.state["event_type"],
        "location": ctx.state["location"],
        "target_audience": ctx.state["target_audience"],
        "marketing_budget": ctx.state["marketing_budget"],
        "registration_goal": ctx.state["registration_goal"],
        "apply_optimization": ctx.state.get("apply_optimization_directly", False)
    }
    return Event(output=db_input)


def prepare_creative_input(node_input, ctx: Context) -> Event:
    """Save data budget forecast and prepare inputs for Creative Studio."""
    # Convert Pydantic output to dict
    if hasattr(node_input, "model_dump"):
        node_input = node_input.model_dump()
    elif hasattr(node_input, "dict"):
        node_input = node_input.dict()

    ctx.state["data_budget_results"] = node_input

    channels = [alloc.get("channel") for alloc in node_input.get("allocations", [])]

    creative_input = {
        "event_name": ctx.state["event_name"],
        "event_type": ctx.state["event_type"],
        "theme": ctx.state["theme"],
        "target_audience": ctx.state["target_audience"],
        "channels": channels
    }
    return Event(output=creative_input)


def prepare_risk_input(node_input, ctx: Context) -> Event:
    """Save creative studio assets and prepare inputs for Risk & Compliance."""
    if hasattr(node_input, "model_dump"):
        node_input = node_input.model_dump()
    elif hasattr(node_input, "dict"):
        node_input = node_input.dict()

    ctx.state["creative_assets"] = node_input

    db_res = ctx.state["data_budget_results"]
    
    risk_input = {
        "event_name": ctx.state["event_name"],
        "event_type": ctx.state["event_type"],
        "target_audience": ctx.state["target_audience"],
        "marketing_budget": ctx.state["marketing_budget"],
        "registration_goal": ctx.state["registration_goal"],
        "allocations": db_res.get("allocations", []),
        "summary": db_res.get("summary", {}),
        "email_invitation": node_input.get("email_invitation", ""),
        "linkedin_posts": node_input.get("linkedin_posts", [])
    }
    return Event(output=risk_input)


def route_by_risk(node_input, ctx: Context) -> Event:
    """Check the risk category from the audit output and route accordingly."""
    if hasattr(node_input, "model_dump"):
        node_input = node_input.model_dump()
    elif hasattr(node_input, "dict"):
        node_input = node_input.dict()

    ctx.state["risk_assessment_results"] = node_input
    
    is_approved = node_input.get("is_approved", True)
    risk_cat = node_input.get("risk_category", "LOW RISK")
    
    if is_approved:
        print(f"[Director] Campaign is {risk_cat}. Bypassing human approval.", flush=True)
        return Event(route="LOW_RISK", output=node_input)
    else:
        print(f"[Director] Campaign is {risk_cat}. Manager approval required.", flush=True)
        return Event(route="REQUIRES_APPROVAL", output=node_input)


def request_human_approval(node_input, ctx: Context):
    """Yield a RequestInput to pause the workflow for human approval."""
    db_res = ctx.state["data_budget_results"]
    risk = ctx.state["risk_assessment_results"]

    payload = {
        "budget_allocation": db_res.get("allocations", []),
        "registration_forecast": db_res.get("summary", {}),
        "risk_assessment": risk
    }

    # Pause execution and request feedback/approval
    yield RequestInput(
        message="Approve Marketing Plan? (Approve / Reject)",
        payload=payload
    )


def process_approval_decision(node_input, ctx: Context) -> Event:
    """Analyze human decision and feedback to route the campaign plan."""
    decision = "approve"
    feedback = ""
    
    if isinstance(node_input, dict):
        decision = node_input.get("decision", "approve").lower()
        feedback = node_input.get("feedback", "")
    elif isinstance(node_input, str):
        decision = "approve" if "approve" in node_input.lower() else "reject"
        feedback = node_input

    ctx.state["approval_feedback"] = feedback

    if "approve" in decision:
        return Event(route="APPROVED", output={"status": "APPROVED"})
    else:
        return Event(route="REJECTED", output={"feedback": feedback})


def adjust_brief_and_reallocate(node_input: dict, ctx: Context) -> Event:
    """Adjust campaign brief parameters based on feedback and re-route to budget allocation."""
    feedback = node_input.get("feedback", "Adjust budget allocation")
    print(f"[Director] Re-routing campaign budget allocation based on feedback: {feedback}", flush=True)
    
    # Enable optimized split calculation on the next loop
    ctx.state["apply_optimization_directly"] = True

    # Regenerate DataBudgetInput payload
    db_input = {
        "event_name": ctx.state["event_name"],
        "event_type": ctx.state["event_type"],
        "location": ctx.state["location"],
        "target_audience": ctx.state["target_audience"],
        "marketing_budget": ctx.state["marketing_budget"],
        "registration_goal": ctx.state["registration_goal"],
        "apply_optimization": True
    }
    return Event(output=db_input)


def generate_final_report(node_input, ctx: Context) -> Event:
    """Generate the final marketing intelligence report by combining sub-agent outputs."""
    db_res = ctx.state["data_budget_results"]
    creative = ctx.state["creative_assets"]
    risk = ctx.state["risk_assessment_results"]

    report = {
        "status": "APPROVED",
        "campaign_summary": {
            "event_name": ctx.state["event_name"],
            "event_type": ctx.state["event_type"],
            "location": ctx.state["location"],
            "target_audience": ctx.state["target_audience"],
            "budget_details": db_res.get("summary", {}),
            "allocations": db_res.get("allocations", []),
        },
        "creative_deliverables": creative,
        "risk_and_compliance_audit": risk,
        "comments": "Campaign approved and ready for execution."
    }
    return Event(output=report)


# ---------------------------------------------------------------------------
# ADK 2.0 Graph Workflow Registration
# ---------------------------------------------------------------------------

root_agent = Workflow(
    name="event_marketing_director",
    edges=[
        # 1. Event Brief Input -> Goal Analysis
        ("START", parse_brief, goal_analysis),
        # 2. Goal Analysis -> Data & Budget Agent (recommends channels, allocates budget, forecasts registrations)
        (goal_analysis, data_budget_agent),
        # 3. Data & Budget Agent -> Prepare Creative Input
        (data_budget_agent, prepare_creative_input),
        # 4. Prepare Creative Input -> Creative Studio Agent (generates copywriting assets)
        (prepare_creative_input, creative_studio_agent),
        # 5. Creative Studio Agent -> Prepare Risk Input
        (creative_studio_agent, prepare_risk_input),
        # 6. Prepare Risk Input -> Risk & Compliance Agent (assesses shortfall and content)
        (prepare_risk_input, risk_compliance_agent),
        # 7. Risk & Compliance Agent -> Route By Risk
        (risk_compliance_agent, route_by_risk),
        # 8. Route By Risk split:
        #    - LOW RISK -> Go straight to final report
        #    - REQUIRES_APPROVAL -> Route to human approval (RequestInput)
        (
            route_by_risk,
            {
                "LOW_RISK": generate_final_report,
                "REQUIRES_APPROVAL": request_human_approval,
            },
        ),
        # 9. Human Approval -> Approval router
        (request_human_approval, process_approval_decision),
        (
            process_approval_decision,
            {
                "APPROVED": generate_final_report,
                "REJECTED": adjust_brief_and_reallocate,
            },
        ),
        # 10. Loopback: Adjust brief & reallocate -> Data & Budget Agent
        (adjust_brief_and_reallocate, data_budget_agent),
    ],
)
