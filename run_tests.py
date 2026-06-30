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

"""Test execution script for verifying the Event Marketing Intelligence workflow with three test scenarios."""

from typing import Dict, Any, List
from google.adk import Context

# Import workflow nodes and tools
from event_marketing_agent.agent import (
    parse_brief,
    goal_analysis,
    prepare_creative_input,
    prepare_risk_input,
    route_by_risk,
    generate_final_report,
)
from event_marketing_agent.tools.budget_tools import recommend_channels_and_allocate_budget
from event_marketing_agent.tools.compliance_tools import evaluate_campaign_risks

# Simple mock classes to satisfy Context constructor requirements
class MockSession:
    def __init__(self):
        self.state = {}

class MockInvocationContext:
    def __init__(self):
        self.session = MockSession()


# Simple mock asset generator for testing purposes
def test_asset_generation(event_name: str, target_audience: str, theme: str) -> dict:
    return {
        "instagram_captions": [f"Join us at {event_name}! #learning"],
        "linkedin_posts": [f"Professional value at {event_name} for {target_audience}."],
        "email_invitation": f"Subject: Invitation to {event_name}\n\nHello [Name],\n\nWe invite you to {event_name} concerning {theme}.",
        "ad_headlines": [{"channel": "Google Search Ads", "headline": f"Register for {event_name}"}],
        "call_to_action": ["Register Now"],
        "hashtags": ["#expo", "#networking"]
    }


def execute_workflow_simulation(scenario_name: str, brief: dict) -> None:
    print(f"\n====================================================")
    print(f"RUNNING SCENARIO: {scenario_name}")
    print(f"====================================================")
    print(f"Brief Inputs:")
    print(f"  Event Name: {brief['event_name']}")
    print(f"  Event Type: {brief['event_type']}")
    print(f"  Location: {brief['location']}")
    print(f"  Target Audience: {brief['target_audience']}")
    print(f"  Marketing Budget: {brief['marketing_budget']}")
    print(f"  Registration Goal: {brief['registration_goal']}")
    print(f"  Theme: {brief['theme']}")
    print("-" * 50)

    # Initialize context and state using MockInvocationContext
    mock_invoc = MockInvocationContext()
    ctx = Context(mock_invoc)
    
    # Node 1: parse_brief
    print("[Node 1] Executing: parse_brief")
    brief_out = parse_brief(brief, ctx).output
    
    # Node 2: goal_analysis
    print("[Node 2] Executing: goal_analysis")
    goal_out = goal_analysis(brief_out, ctx).output
    
    # Node 3: data_budget_agent (simulating tool run)
    print("[Node 3] Executing: data_budget_agent (allocating budget & forecasting)...")
    db_output = recommend_channels_and_allocate_budget(
        event_type=goal_out["event_type"],
        target_audience=goal_out["target_audience"],
        marketing_budget=goal_out["marketing_budget"],
        registration_goal=goal_out["registration_goal"],
        apply_optimization=goal_out.get("apply_optimization", False)
    )
    
    # Node 4: prepare_creative_input
    print("[Node 4] Executing: prepare_creative_input")
    creative_in = prepare_creative_input(db_output, ctx).output
    
    # Node 5: creative_studio_agent (simulating creative generation)
    print("[Node 5] Executing: creative_studio_agent (generating assets)...")
    assets_output = test_asset_generation(
        event_name=creative_in["event_name"],
        target_audience=creative_in["target_audience"],
        theme=creative_in["theme"]
    )
    
    # Node 6: prepare_risk_input
    print("[Node 6] Executing: prepare_risk_input")
    risk_in = prepare_risk_input(assets_output, ctx).output
    
    # Node 7: risk_compliance_agent (simulating risk analysis tool run)
    print("[Node 7] Executing: risk_compliance_agent (evaluating compliance & risks)...")
    risk_output = evaluate_campaign_risks(
        event_name=risk_in["event_name"],
        event_type=brief["event_type"],
        target_audience=brief["target_audience"],
        marketing_budget=brief["marketing_budget"],
        registration_goal=risk_in["registration_goal"],
        allocations=db_output["allocations"],
        summary=db_output["summary"]
    )
    
    # Node 8: route_by_risk
    print("[Node 8] Executing: route_by_risk")
    route_event = route_by_risk(risk_output, ctx)
    route = route_event.actions.route
    print(f"  Routing decision: {route}")
    
    if route == "LOW_RISK":
        # Node 9: generate_final_report
        print("[Node 9] Executing: generate_final_report (Bypassing Human approval)")
        report_event = generate_final_report(None, ctx)
        report = report_event.output
        print(f"  Campaign Status: {report['status']}")
        print(f"  Risk Category: {report['risk_and_compliance_audit']['risk_category']}")
        print(f"  Forecasted registrations: {report['campaign_summary']['budget_details']['total_estimated_registrations']}")
        print(f"  Registration Goal: {report['campaign_summary']['budget_details']['registration_goal']}")
        print(f"  Feasibility: {report['campaign_summary']['budget_details']['feasibility_status']}")
        
    elif route == "REQUIRES_APPROVAL":
        # Simulate manager review and loopback approval
        print("[Node 9] Executing: request_human_approval (HITL)")
        print("  Workflow Paused. Displaying allocations, forecast, and risk assessment...")
        print(f"  [Warnings]: {risk_output['warnings']}")
        print(f"  [Shortfall]: {risk_output['shortfall_percentage']}%")
        
        print("  Simulating manager interaction: Rejecting and triggering Reallocation optimization...")
        # Simulates REJECTED loopback by applying optimization and running again
        ctx.state["apply_optimization_directly"] = True
        
        # Node 10: adjust_brief_and_reallocate
        print("[Node 10] Executing: adjust_brief_and_reallocate (Loopback)")
        reallocate_out = goal_analysis(brief_out, ctx).output # retrieve optimized config
        
        print("[Node 3-Loop] Executing: data_budget_agent (optimized run)...")
        db_output_opt = recommend_channels_and_allocate_budget(
            event_type=reallocate_out["event_type"],
            target_audience=reallocate_out["target_audience"],
            marketing_budget=reallocate_out["marketing_budget"],
            registration_goal=reallocate_out["registration_goal"],
            apply_optimization=True
        )
        
        print("[Node 7-Loop] Executing: risk_compliance_agent (optimized run)...")
        risk_output_opt = evaluate_campaign_risks(
            event_name=brief["event_name"],
            event_type=brief["event_type"],
            target_audience=brief["target_audience"],
            marketing_budget=brief["marketing_budget"],
            registration_goal=brief["registration_goal"],
            allocations=db_output_opt["allocations"],
            summary=db_output_opt["summary"]
        )
        
        # Update results in context
        ctx.state["data_budget_results"] = db_output_opt
        ctx.state["risk_assessment_results"] = risk_output_opt
        
        print("[Node 9-Loop] Executing: generate_final_report (After optimization approval)")
        report_event = generate_final_report(None, ctx)
        report = report_event.output
        print(f"  Campaign Status: {report['status']}")
        print(f"  Risk Category: {report['risk_and_compliance_audit']['risk_category']}")
        print(f"  Forecasted registrations: {report['campaign_summary']['budget_details']['total_estimated_registrations']}")
        print(f"  Registration Goal: {report['campaign_summary']['budget_details']['registration_goal']}")
        print(f"  Feasibility: {report['campaign_summary']['budget_details']['feasibility_status']}")
        print(f"  Optimization Applied: {db_output_opt['summary']['optimization_recommendation']}")

    print("====================================================\n")


# Scenario Inputs
test_scenarios = {
    "Test Scenario 1 (Pune Property Expo)": {
        "event_name": "Pune Property Expo",
        "event_type": "Consumer",
        "location": "Pune Exhibition Center",
        "target_audience": "Families and individual home buyers",
        "marketing_budget": 200000.0,
        "registration_goal": 1000,
        "theme": "Find your dream home in Pune. Meet top builders and explore budget apartments to luxury villas."
    },
    "Test Scenario 2 (Startup Networking Event)": {
        "event_name": "Startup Networking Event",
        "event_type": "Community",
        "location": "Co-Working Hub, Pune",
        "target_audience": "Founders, early-stage investors, and software developer enthusiasts",
        "marketing_budget": 50000.0,
        "registration_goal": 500,
        "theme": "Pitches, feedback, and networking for early-stage founders."
    },
    "Test Scenario 3 (B2B Real Estate Expo)": {
        "event_name": "B2B Real Estate Expo",
        "event_type": "B2B",
        "location": "JW Marriott, Pune",
        "target_audience": "Real estate brokers, commercial builders, and institutional investors",
        "marketing_budget": 300000.0,
        "registration_goal": 1500,
        "theme": "Commercial development opportunities, market reports, and property technology integration."
    },
    "Test Scenario 4 (High Shortfall B2B Event)": {
        "event_name": "Tech Agent Summit",
        "event_type": "B2B",
        "location": "Virtual",
        "target_audience": "Software Developers and Product Managers",
        "marketing_budget": 10000.0,
        "registration_goal": 350,
        "theme": "Deep dive into multi-agent systems and ADK 2.0 developer integrations."
    }
}

if __name__ == "__main__":
    for name, brief in test_scenarios.items():
        execute_workflow_simulation(name, brief)
