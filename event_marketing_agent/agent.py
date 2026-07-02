import logging
import json
from google.adk import Context, Event, Workflow
from google.adk.events import RequestInput

from .sub_agents import (
    creative_studio_agent,
    data_budget_agent,
    risk_compliance_agent,
)
from .sub_agents.data_budget.agent import DataBudgetInput
from .sub_agents.risk_compliance.agent import RiskComplianceInput
from .sub_agents.creative_studio.agent import CreativeStudioInput

# Configure logger
logger = logging.getLogger("event_marketing_orchestrator")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Workflow Orchestration Nodes
# ---------------------------------------------------------------------------


def parse_brief(node_input: dict, ctx: Context) -> Event:
    """Parse raw brief input, validate parameters, and initialize campaign parameters in state."""
    logger.info("Starting parse_brief stage.")
    try:
        # Validate node_input type
        if not isinstance(node_input, dict):
            raise ValueError("Input to parse_brief must be a dictionary.")

        # Parse and validate event name
        event_name = node_input.get("event_name", "").strip()
        if not event_name:
            raise ValueError("Input validation failed: 'event_name' must be a non-empty string.")

        # Parse and validate event type
        event_type = node_input.get("event_type", "").strip()
        if not event_type:
            raise ValueError("Input validation failed: 'event_type' must be a non-empty string.")

        # Parse and validate target audience
        target_audience = node_input.get("target_audience", "").strip()
        if not target_audience:
            raise ValueError("Input validation failed: 'target_audience' must be a non-empty string.")

        # Parse and validate marketing budget
        try:
            marketing_budget = float(node_input.get("marketing_budget", 10000.0))
            if marketing_budget <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError("Input validation failed: 'marketing_budget' must be a positive number.")

        # Parse and validate registration goal
        try:
            registration_goal = int(node_input.get("registration_goal", 100))
            if registration_goal <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError("Input validation failed: 'registration_goal' must be a positive integer.")

        ctx.state["event_name"] = event_name
        ctx.state["event_type"] = event_type
        ctx.state["location"] = node_input.get("location", "Virtual").strip()
        ctx.state["target_audience"] = target_audience
        ctx.state["marketing_budget"] = marketing_budget
        ctx.state["registration_goal"] = registration_goal
        ctx.state["theme"] = node_input.get("theme", "Growth and Networking").strip()
        
        ctx.state["apply_optimization_directly"] = False
        
        logger.info(f"Successfully parsed brief for event: '{event_name}' (Budget: ${marketing_budget:,.2f}, Goal: {registration_goal}).")
        return Event(output=node_input)
    except Exception as e:
        logger.error(f"Error in parse_brief: {str(e)}", exc_info=True)
        raise e


def goal_analysis(node_input: dict, ctx: Context) -> Event:
    """Analyze campaign brief attributes and prepare inputs for the Data & Budget agent."""
    logger.info("Starting goal_analysis stage.")
    try:
        db_input = DataBudgetInput(
            event_name=ctx.state["event_name"],
            event_type=ctx.state["event_type"],
            location=ctx.state["location"],
            target_audience=ctx.state["target_audience"],
            marketing_budget=ctx.state["marketing_budget"],
            registration_goal=ctx.state["registration_goal"],
            apply_optimization=ctx.state.get("apply_optimization_directly", False)
        )
        logger.info("Successfully validated DataBudgetInput schema.")
        return Event(output=db_input.model_dump())
    except Exception as e:
        logger.error(f"Error in goal_analysis: {str(e)}", exc_info=True)
        raise e


def prepare_risk_input(node_input, ctx: Context) -> Event:
    """Save data budget forecast and prepare inputs for Risk & Compliance."""
    logger.info("Starting prepare_risk_input stage.")
    try:
        if hasattr(node_input, "model_dump"):
            node_input = node_input.model_dump()
        elif hasattr(node_input, "dict"):
            node_input = node_input.dict()

        ctx.state["data_budget_results"] = node_input

        # Validate with RiskComplianceInput Pydantic model
        risk_input = RiskComplianceInput(
            event_name=ctx.state["event_name"],
            event_type=ctx.state["event_type"],
            target_audience=ctx.state["target_audience"],
            marketing_budget=ctx.state["marketing_budget"],
            registration_goal=ctx.state["registration_goal"],
            allocations=node_input.get("allocations", []),
            summary=node_input.get("summary", {}),
            email_invitation="",
            linkedin_posts=[]
        )
        logger.info("Successfully validated RiskComplianceInput schema.")
        return Event(output=risk_input.model_dump())
    except Exception as e:
        logger.error(f"Error in prepare_risk_input: {str(e)}", exc_info=True)
        raise e


def prepare_creative_input(node_input, ctx: Context) -> Event:
    """Save risk assessment and prepare inputs for Creative Studio."""
    logger.info("Starting prepare_creative_input stage.")
    try:
        if hasattr(node_input, "model_dump"):
            node_input = node_input.model_dump()
        elif hasattr(node_input, "dict"):
            node_input = node_input.dict()

        ctx.state["risk_assessment_results"] = node_input

        db_res = ctx.state["data_budget_results"]
        channels = [alloc.get("channel") for alloc in db_res.get("allocations", [])]

        # Validate with CreativeStudioInput Pydantic model
        creative_input = CreativeStudioInput(
            event_name=ctx.state["event_name"],
            event_type=ctx.state["event_type"],
            theme=ctx.state["theme"],
            target_audience=ctx.state["target_audience"],
            channels=channels,
            risk_assessment=node_input
        )
        logger.info("Successfully validated CreativeStudioInput schema.")
        return Event(output=creative_input.model_dump())
    except Exception as e:
        logger.error(f"Error in prepare_creative_input: {str(e)}", exc_info=True)
        raise e


def prepare_route_input(node_input, ctx: Context) -> Event:
    """Save creative studio assets and extract risk assessment for routing."""
    logger.info("Starting prepare_route_input stage.")
    try:
        if hasattr(node_input, "model_dump"):
            node_input = node_input.model_dump()
        elif hasattr(node_input, "dict"):
            node_input = node_input.dict()

        ctx.state["creative_assets"] = node_input
        
        risk_res = ctx.state["risk_assessment_results"]
        logger.info("Successfully saved creative studio assets and loaded risk results.")
        return Event(output=risk_res)
    except Exception as e:
        logger.error(f"Error in prepare_route_input: {str(e)}", exc_info=True)
        raise e


def route_by_risk(node_input, ctx: Context) -> Event:
    """Check the risk category from the audit output and route accordingly."""
    logger.info("Starting route_by_risk stage.")
    try:
        if hasattr(node_input, "model_dump"):
            node_input = node_input.model_dump()
        elif hasattr(node_input, "dict"):
            node_input = node_input.dict()

        ctx.state["risk_assessment_results"] = node_input
        
        is_approved = node_input.get("is_approved", True)
        risk_cat = node_input.get("risk_category", "LOW RISK")
        
        if is_approved:
            logger.info(f"Campaign routes to LOW_RISK. Category: {risk_cat}.")
            return Event(route="LOW_RISK", output=node_input)
        else:
            logger.warning(f"Campaign routes to REQUIRES_APPROVAL. Category: {risk_cat}.")
            return Event(route="REQUIRES_APPROVAL", output=node_input)
    except Exception as e:
        logger.error(f"Error in route_by_risk: {str(e)}", exc_info=True)
        raise e


def request_human_approval(node_input, ctx: Context):
    """Yield a RequestInput to pause the workflow for human approval."""
    logger.info("Executing request_human_approval pause.")
    try:
        db_res = ctx.state["data_budget_results"]
        risk = ctx.state["risk_assessment_results"]

        payload = {
            "budget_allocation": db_res.get("allocations", []),
            "registration_forecast": db_res.get("summary", {}),
            "risk_assessment": risk
        }

        yield RequestInput(
            message="Approve Marketing Plan? (Approve / Reject)",
            payload=payload
        )
    except Exception as e:
        logger.error(f"Error in request_human_approval: {str(e)}", exc_info=True)
        raise e


def process_approval_decision(node_input, ctx: Context) -> Event:
    """Analyze human decision and feedback to route the campaign plan."""
    logger.info("Starting process_approval_decision stage.")
    try:
        decision = "approve"
        feedback = ""
        
        if isinstance(node_input, dict):
            decision = node_input.get("decision", "approve").lower()
            feedback = node_input.get("feedback", "")
        elif isinstance(node_input, str):
            decision = "approve" if "approve" in node_input.lower() else "reject"
            feedback = node_input

        ctx.state["approval_feedback"] = feedback

        logger.info(f"Processed decision: '{decision}' with feedback: '{feedback}'.")
        if "approve" in decision:
            return Event(route="APPROVED", output={"status": "APPROVED"})
        else:
            return Event(route="REJECTED", output={"feedback": feedback})
    except Exception as e:
        logger.error(f"Error in process_approval_decision: {str(e)}", exc_info=True)
        raise e


def adjust_brief_and_reallocate(node_input: dict, ctx: Context) -> Event:
    """Adjust campaign brief parameters based on feedback and re-route to budget allocation."""
    logger.info("Starting adjust_brief_and_reallocate loopback.")
    try:
        feedback = node_input.get("feedback", "Adjust budget allocation")
        logger.info(f"Re-routing campaign budget allocation based on feedback: {feedback}")
        
        ctx.state["apply_optimization_directly"] = True

        db_input = DataBudgetInput(
            event_name=ctx.state["event_name"],
            event_type=ctx.state["event_type"],
            location=ctx.state["location"],
            target_audience=ctx.state["target_audience"],
            marketing_budget=ctx.state["marketing_budget"],
            registration_goal=ctx.state["registration_goal"],
            apply_optimization=True
        )
        logger.info("Successfully validated DataBudgetInput for reallocation.")
        return Event(output=db_input.model_dump())
    except Exception as e:
        logger.error(f"Error in adjust_brief_and_reallocate: {str(e)}", exc_info=True)
        raise e


def generate_final_report(node_input, ctx: Context) -> Event:
    """Generate the final marketing intelligence report by combining sub-agent outputs."""
    logger.info("Starting generate_final_report stage.")
    try:
        db_res = ctx.state.get("data_budget_results") or {}
        creative = ctx.state.get("creative_assets") or {}
        risk = ctx.state.get("risk_assessment_results") or {}

        # 1. Executive Summary
        exec_summary = {
            "event_name": ctx.state.get("event_name", "Global Seminar"),
            "event_type": ctx.state.get("event_type", "B2B"),
            "location": ctx.state.get("location", "Virtual"),
            "target_audience": ctx.state.get("target_audience", "Professionals"),
            "theme": ctx.state.get("theme", "Growth and Networking"),
            "status": "APPROVED",
            "overall_feasibility": db_res.get("summary", {}).get("feasibility_status", "FEASIBLE"),
            "director_decision": risk.get("explanation", "Approved by Director Agent.")
        }

        report = {
            "status": "APPROVED",
            "executive_summary": exec_summary,
            "campaign_summary": {
                "event_name": ctx.state.get("event_name", "Global Seminar"),
                "event_type": ctx.state.get("event_type", "B2B"),
                "location": ctx.state.get("location", "Virtual"),
                "target_audience": ctx.state.get("target_audience", "Professionals"),
                "budget_details": db_res.get("summary", {}),
                "allocations": db_res.get("allocations", []),
            },
            "budget_recommendations": db_res.get("allocations", []),
            "registration_forecast": db_res.get("summary", {}),
            "risk_assessment": risk,
            "campaign_creative_strategy": {
                "campaign_theme": creative.get("campaign_theme"),
                "messaging_strategy": creative.get("messaging_strategy"),
                "audience_positioning": creative.get("audience_positioning"),
                "success_kpis": creative.get("success_kpis"),
                "confidence_score": creative.get("messaging_alignment_confidence")
            },
            "marketing_assets": {
                "email_copy": creative.get("email_copy"),
                "linkedin_post": creative.get("linkedin_post"),
                "instagram_caption": creative.get("instagram_caption"),
                "google_ads_headline": creative.get("google_ads_headline"),
                "channel_strategies": creative.get("channel_strategies", []),
                "ad_headlines": creative.get("ad_headlines", []),
                "call_to_actions": creative.get("call_to_action", []),
                "hashtags": creative.get("hashtags", [])
            },
            "creative_deliverables": creative,
            "risk_and_compliance_audit": risk,
            "comments": "Campaign approved and ready for execution."
        }
        logger.info("Final report generated successfully.")
        return Event(output=report)
    except Exception as e:
        logger.error(f"Error in generate_final_report: {str(e)}", exc_info=True)
        raise e


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
        # 3. Data & Budget Agent -> Prepare Risk Input
        (data_budget_agent, prepare_risk_input),
        # 4. Prepare Risk Input -> Risk & Compliance Agent (evaluates compliance warnings)
        (prepare_risk_input, risk_compliance_agent),
        # 5. Risk & Compliance Agent -> Prepare Creative Input
        (risk_compliance_agent, prepare_creative_input),
        # 6. Prepare Creative Input -> Creative Studio Agent (generates copywriting strategy adapted to risk)
        (prepare_creative_input, creative_studio_agent),
        # 7. Creative Studio Agent -> Prepare Route Input
        (creative_studio_agent, prepare_route_input),
        # 8. Prepare Route Input -> Route By Risk
        (prepare_route_input, route_by_risk),
        # 9. Route By Risk split:
        #    - LOW RISK -> Go straight to final report
        #    - REQUIRES_APPROVAL -> Route to human approval (RequestInput)
        (
            route_by_risk,
            {
                "LOW_RISK": generate_final_report,
                "REQUIRES_APPROVAL": request_human_approval,
            },
        ),
        # 10. Human Approval -> Approval router
        (request_human_approval, process_approval_decision),
        (
            process_approval_decision,
            {
                "APPROVED": generate_final_report,
                "REJECTED": adjust_brief_and_reallocate,
            },
        ),
        # 11. Loopback: Adjust brief & reallocate -> Data & Budget Agent
        (adjust_brief_and_reallocate, data_budget_agent),
    ],
)
