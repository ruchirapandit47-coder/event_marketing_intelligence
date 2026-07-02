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

"""Streamlit business dashboard for the Event Marketing Intelligence Agent."""

import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import asyncio
import json
from google.adk import Context, Event
from google.adk.events import RequestInput
from event_marketing_agent.agent import root_agent

# Page styling and header
st.set_page_config(
    page_title="Event Marketing Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom css for modern aesthetics (vibrant headers, card designs, custom text)
st.markdown("""
<style>
    .reportview-container {
        background: #f8f9fa;
    }
    .main-title {
        color: #1a73e8;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #5f6368;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #202124;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border-bottom: 2px solid #e8eaed;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1.25rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        border-left: 5px solid #1a73e8;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #202124;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #5f6368;
        text-transform: uppercase;
        font-weight: 500;
    }
    .asset-box {
        background: #f1f3f4;
        border: 1px solid #dadce0;
        border-radius: 6px;
        padding: 1rem;
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main Application Title
st.markdown("<div class='main-title'>Event Marketing Intelligence Agent</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>ADK 2.0 Graph Workflow Planning, Budget Optimization, and Asset Generation</div>", unsafe_allow_html=True)

# Sidebar - Event Brief Inputs
st.sidebar.markdown("### 📝 Event Brief Input")

# Preset Test Scenarios Dictionary
test_scenarios = {
    "Custom Campaign": {
        "event_name": "Google Cloud Next Recap",
        "event_type": "B2B",
        "location": "San Francisco & Hybrid",
        "target_audience": "Software Engineers and Cloud Architects",
        "marketing_budget": 10000.0,
        "registration_goal": 300,
        "theme": "Deep dive into Vertex AI, GenAI Agents, and cloud modernization strategies."
    },
    "Pune Property Expo (Scenario 1)": {
        "event_name": "Pune Property Expo",
        "event_type": "Consumer",
        "location": "Pune Exhibition Center",
        "target_audience": "Families and individual home buyers",
        "marketing_budget": 200000.0,
        "registration_goal": 1000,
        "theme": "Find your dream home in Pune. Meet top builders and explore budget apartments to luxury villas."
    },
    "Startup Networking Event (Scenario 2)": {
        "event_name": "Startup Networking Event",
        "event_type": "Community",
        "location": "Co-Working Hub, Pune",
        "target_audience": "Founders, early-stage investors, and software developer enthusiasts",
        "marketing_budget": 50000.0,
        "registration_goal": 500,
        "theme": "Pitches, feedback, and networking for early-stage founders."
    },
    "B2B Real Estate Expo (Scenario 3)": {
        "event_name": "B2B Real Estate Expo",
        "event_type": "B2B",
        "location": "JW Marriott, Pune",
        "target_audience": "Real estate brokers, commercial builders, and institutional investors",
        "marketing_budget": 300000.0,
        "registration_goal": 1500,
        "theme": "Commercial development opportunities, market reports, and property technology integration."
    },
    "Tech Agent Summit (Scenario 4)": {
        "event_name": "Tech Agent Summit",
        "event_type": "B2B",
        "location": "Virtual",
        "target_audience": "Software Developers and Product Managers",
        "marketing_budget": 10000.0,
        "registration_goal": 350,
        "theme": "Deep dive into multi-agent systems and ADK 2.0 developer integrations."
    }
}

selected_preset = st.sidebar.selectbox(
    "Load Campaign Preset",
    list(test_scenarios.keys()),
    index=0,
    help="Select a preset scenario to auto-populate the inputs."
)

preset = test_scenarios[selected_preset]

# Keep state of active preset and reset approval/optimization states if preset changes
if 'active_preset' not in st.session_state:
    st.session_state.active_preset = selected_preset

if st.session_state.active_preset != selected_preset:
    st.session_state.active_preset = selected_preset
    st.session_state.optimized = False
    st.session_state.approved = False
    st.session_state.reallocated = False

# Bind widget values to the active preset
event_name = st.sidebar.text_input("Event Name", value=preset["event_name"])
event_types = ["B2B", "Developer", "Consumer", "Academic", "Community"]
event_type_idx = event_types.index(preset["event_type"]) if preset["event_type"] in event_types else 0
event_type = st.sidebar.selectbox("Event Type", event_types, index=event_type_idx)
location = st.sidebar.text_input("Location / Venue", value=preset["location"])
target_audience = st.sidebar.text_input("Target Audience", value=preset["target_audience"])
marketing_budget = st.sidebar.number_input("Marketing Budget ($)", min_value=500.0, max_value=1000000.0, value=preset["marketing_budget"], step=500.0)
registration_goal = st.sidebar.number_input("Registration Goal", min_value=10, max_value=100000, value=preset["registration_goal"], step=10)
theme = st.sidebar.text_area("Event Theme / Description", value=preset["theme"])

# Keep state of calculations
if 'optimized' not in st.session_state:
    st.session_state.optimized = False
if 'approved' not in st.session_state:
    st.session_state.approved = False
if 'reallocated' not in st.session_state:
    st.session_state.reallocated = False

# Reset optimization if inputs are changed in the sidebar
def on_input_change():
    st.session_state.optimized = False
    st.session_state.approved = False
    st.session_state.reallocated = False

# Apply trigger on input edits
# (Streamlit handles inputs changing, but we can reset state if button is clicked)
generate_clicked = st.sidebar.button("Generate Campaign Plan", use_container_width=True)

if generate_clicked:
    st.session_state.optimized = False
    st.session_state.approved = False
    st.session_state.reallocated = False

# Mock Asset Generator to match Creative Studio Agent
def mock_asset_generation(event_name, event_type, theme, target_audience, channels):
    instagram = [
        f"🚀 Big news! '{event_name}' is officially open! Calling all {target_audience}—we are diving deep into the theme: '{theme}'. "
        f"Get ready for network updates, live demos, and expert talks. Don't miss out! #event #tech #networking #learning",
        f"Interested in '{theme}'? 💡 Register now for {event_name}! Learn how industry leaders are tackling today's hurdles. "
        f"Link in bio! 📲 #learning #development #careers"
    ]
    
    linkedin = [
        f"📅 Mark your calendar for {event_name}! We are bringing together leading minds to discuss '{theme}'.\n\n"
        f"Why you should attend:\n"
        f"• Network with peer {target_audience} experts.\n"
        f"• Gain actionable takeaways on our main topics.\n"
        f"• Live Q&A and interactive break-outs.\n\n"
        f"👉 Register today: [Link]",
        
        f"Are you looking to expand your knowledge of '{theme}'? Join us at {event_name} in {location}. "
        f"Tailored specifically for {target_audience}, this event focuses on modern best practices. "
        f"Early bird tickets are going fast! #B2B #ProfessionalDevelopment #Networking"
    ]
    
    email = (
        f"Subject: Invitation: {event_name} - Deep Dive into {theme}\n\n"
        f"Hello [Name],\n\n"
        f"We are excited to invite you to '{event_name}', a specialized gathering for {target_audience} "
        f"focused on '{theme}'.\n\n"
        f"Event Details:\n"
        f"• Date: [Event Date]\n"
        f"• Location: {location}\n"
        f"• Format: {event_type}\n\n"
        f"Our sessions will cover core aspects of the topic and provide opportunities to connect with leaders in the field. "
        f"As space is limited, please RSVP to confirm your attendance.\n\n"
        f"Best regards,\n"
        f"The Event Organizing Committee\n"
        f"RSVP Here: [Link]"
    )
    
    headlines = []
    for c in channels:
        headlines.append({
            "channel": c,
            "headline": f"Join {event_name} | {theme[:25]}..."
        })
        
    ctas = [
        "Register Now",
        "Save Your Spot",
        "Confirm RSVP",
        "Secure Tickets"
    ]
    
    hashtags = [
        f"#{event_type.lower()}",
        f"#{target_audience.split()[0].lower() if target_audience else 'event'}",
        f"#{event_name.replace(' ', '').lower()}",
        "#growth"
    ]
    
    return {
        "instagram_captions": instagram,
        "linkedin_posts": linkedin,
        "email_invitation": email,
        "ad_headlines": headlines,
        "call_to_action": ctas,
        "hashtags": hashtags
    }

# Keep state of whether campaign has been generated in session state
if 'generated' not in st.session_state:
    st.session_state.generated = False

if 'db_result' not in st.session_state:
    st.session_state.db_result = None
if 'risk_result' not in st.session_state:
    st.session_state.risk_result = None
if 'assets' not in st.session_state:
    st.session_state.assets = None

# Setup Mock Session and Invocation Context
class MockSession:
    def __init__(self):
        self.id = "streamlit-session"
        self.state = {}
        self.events = []

    def model_copy(self, **kwargs):
        return self

class MockInvocationContext:
    def __init__(self, session):
        self.session = session
        self.invocation_id = "streamlit-invocation"
        self.branch = None
        self.isolation_scope = None
        self._event_queue = asyncio.Queue()
        self.end_invocation = False

    def model_copy(self, **kwargs):
        return self

    async def _enqueue_event(self, event):
        self.session.events.append(event)

async def run_workflow_stream(brief_input, user_response_event=None):
    if "workflow_session" not in st.session_state:
        st.session_state.workflow_session = MockSession()
    session = st.session_state.workflow_session
    
    if user_response_event is not None:
        session.events.append(user_response_event)
        
    ctx = Context(MockInvocationContext(session=session))
    
    async for event in root_agent.run(ctx=ctx, node_input=brief_input):
        node_path = event.node_info.path if event.node_info else ''
        if 'parse_brief' in node_path:
            st.write("🔍 **[Director Agent] Parsing campaign brief parameters...**")
        elif 'goal_analysis' in node_path:
            st.write("📈 **[Director Agent] Analyzing event goals and calculating target limits...**")
        elif 'run_data_budget_agent' in node_path:
            st.write("📊 **[Data & Budget Agent] Recommending channels and calculating budget allocation...**")
        elif 'run_creative_studio_agent' in node_path:
            st.write("🎨 **[Creative Studio Agent] Crafting campaign headlines and copywriting copy assets...**")
        elif 'run_risk_compliance_agent' in node_path:
            st.write("⚠️ **[Risk & Compliance Agent] Auditing plan for budget and shortfall compliance...**")
        elif 'adjust_brief_and_reallocate' in node_path:
            st.write("🔄 **[Director Agent] Re-routing to Data & Budget Agent with optimization instructions...**")
        time.sleep(0.5)

brief_payload = {
    'event_name': event_name,
    'event_type': event_type,
    'location': location,
    'target_audience': target_audience,
    'marketing_budget': marketing_budget,
    'registration_goal': registration_goal,
    'theme': theme
}

if generate_clicked:
    # Clear session to start fresh
    st.session_state.workflow_session = MockSession()
    st.session_state.optimized = False
    st.session_state.approved = False
    st.session_state.reallocated = False
    
    with st.status("Event Marketing Director: Orchestrating agent workflow...", expanded=True) as status:
        asyncio.run(run_workflow_stream(brief_payload))
        status.update(label="Campaign Plan Generated successfully!", state="complete", expanded=False)
        
    st.session_state.generated = True
    st.rerun()

# Check if we should render results or display the welcome page
if not st.session_state.generated:
    # Welcome / Intro layout
    st.markdown("""
    <div style='background: white; padding: 2.25rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #1a73e8; margin-top: 1.5rem;'>
        <h3 style='color: #1a73e8; margin-top: 0; font-family: "Inter", sans-serif;'>Welcome to the Campaign Planner</h3>
        <p style='color: #5f6368; font-size: 1.1rem; line-height: 1.6;'>
            This system runs an interactive <b>ADK 2.0 Graph Workflow</b> to optimize marketing plans. Fill out the brief or select a preset in the sidebar, and run the workflow.
        </p>
        <div style='background: #f8f9fa; border-left: 4px solid #1a73e8; padding: 1rem; border-radius: 4px; margin: 1.5rem 0;'>
            <h5 style='color: #202124; margin: 0 0 0.5rem 0; font-weight: 600;'>Specialized Agents in the Network:</h5>
            <ul style='color: #5f6368; font-size: 0.95rem; margin: 0; padding-left: 1.2rem; line-height: 1.5;'>
                <li><b>Event Marketing Director (Orchestrator):</b> Routes the campaign through planning, auditing, and loopback steps.</li>
                <li><b>Data & Budget Agent:</b> Forecasts registrations and splits budget based on Cost Per Acquisition (CPA) benchmarks.</li>
                <li><b>Creative Studio Agent:</b> Generates targeted social posts, captions, headlines, and email templates.</li>
                <li><b>Risk & Compliance Agent:</b> Analyzes budget limits, target realism, and checks for shortfall categories.</li>
            </ul>
        </div>
        <p style='color: #202124; font-weight: 500; margin: 0;'>
            👈 Get started by selecting a preset in the sidebar and clicking <b>Generate Campaign Plan</b>!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render a diagram of the orchestrator workflow map
    st.markdown("<div class='section-header'>🗺️ Workflow Graph Architecture</div>", unsafe_allow_html=True)
    st.markdown("""
    ```mermaid
    graph TD
        Start([START]) --> parse_brief[Event Brief Input]
        parse_brief --> goal_analysis[Goal Analysis]
        goal_analysis --> data_budget_agent[Data & Budget Agent]
        data_budget_agent --> creative_studio_agent[Creative Studio Agent]
        creative_studio_agent --> risk_compliance_agent[Risk & Compliance Agent]
        risk_compliance_agent --> route_by_risk{Risk Rating?}
        
        route_by_risk -- "LOW RISK" --> generate_final_report[Final Report]
        route_by_risk -- "MEDIUM / HIGH RISK" --> request_human_approval[Human Approval <br/><i>RequestInput</i>]
        
        request_human_approval --> process_approval_decision{Approved?}
        process_approval_decision -- "Yes" --> generate_final_report
        process_approval_decision -- "No (optimize)" --> adjust_brief[Adjust Brief & Reallocate]
        adjust_brief --> data_budget_agent
    ```
    """)
    
    # Halt execution here to avoid rendering empty charts/results below
    st.stop()

# Retrieve results from persistent session state
if st.session_state.generated:
    session = st.session_state.workflow_session
    db_result = session.state.get("data_budget_results", {})
    risk_result = session.state.get("risk_assessment_results", {})
    assets = session.state.get("creative_assets", {})

    allocations = db_result.get("allocations", [])
    summary = db_result.get("summary", {})

# DISPLAY DASHBOARD CONTENT
# Executive Summary section at the top
st.markdown("<div class='section-header'>📋 Campaign Executive Summary</div>", unsafe_allow_html=True)
st.write(
    f"The orchestrator workflow has finalized campaign planning for **{event_name}** ({event_type}). "
    f"Below is a strategic analysis of budgets, channels, asset copies, and compliance risk parameters."
)

st.divider()

# Section 1: Executive KPI Cards
st.markdown("<div class='section-header'>📊 Executive Campaign Metrics</div>", unsafe_allow_html=True)

# Render progress bar for confidence
conf_score = summary.get("confidence_score", 82.0)
conf_level = summary.get("forecast_confidence", {}).get("confidence_level", "High")
conf_interval = summary.get("confidence_interval", {"lower_bound": 0, "upper_bound": 0})
st.markdown(
    f"**Forecast Confidence Level**: `{conf_level}` ({conf_score}% score)  \n"
    f"**Forecast Confidence Interval (90% - 110%)**: `[{conf_interval.get('lower_bound')} to {conf_interval.get('upper_bound')}] registrations`"
)
st.progress(int(conf_score))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metric-card' style='border-left-color: #1a73e8;'>
        <div class='metric-label'>Marketing Budget</div>
        <div class='metric-value'>${summary['total_budget']:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    regs_display = f"{summary['total_estimated_registrations']} / {summary['registration_goal']}"
    color = "#137333" if summary['registration_gap'] == 0 else "#c5221f"
    st.markdown(f"""
    <div class='metric-card' style='border-left-color: {color};'>
        <div class='metric-label'>Forecasted / Goal Registrations</div>
        <div class='metric-value'>{regs_display}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card' style='border-left-color: #f29900;'>
        <div class='metric-label'>Avg Cost Per Registration</div>
        <div class='metric-value'>${summary['average_cost_per_registration']:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    risk_score = risk_result.get("risk_score", 0.0)
    risk_color = "#137333" if risk_score <= 10.0 else ("#f29900" if risk_score <= 35.0 else "#c5221f")
    st.markdown(f"""
    <div class='metric-card' style='border-left-color: {risk_color};'>
        <div class='metric-label'>Numerical Risk Score</div>
        <div class='metric-value' style='color: {risk_color};'>{risk_score} / 100</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Main Grid: Charts & Recommendations
grid_col1, grid_col2 = st.columns([1, 1])

with grid_col1:
    st.markdown("<div class='section-header'>📈 Budget Allocation & Performance</div>", unsafe_allow_html=True)
    
    # Format allocations for chart
    df_alloc = pd.DataFrame(allocations)
    
    # Pie chart for budget split
    fig_pie = px.pie(
        df_alloc, 
        values='budget', 
        names='channel', 
        title='Marketing Budget Split by Channel ($)',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

with grid_col2:
    st.markdown("<div class='section-header'>🎯 Registration Forecast breakdown</div>", unsafe_allow_html=True)
    
    # Bar chart for forecasted registrations
    fig_bar = px.bar(
        df_alloc,
        x='channel',
        y='estimated_registrations',
        text='estimated_registrations',
        title='Forecasted Registrations by Channel',
        labels={'channel': 'Channel', 'estimated_registrations': 'Registrations'},
        color='channel'
    )
    fig_bar.update_layout(margin=dict(t=40, b=20, l=0, r=0), height=300, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Panels: Channel Recommendations & Risk Audits
panel_col1, panel_col2 = st.columns([3, 2])

with panel_col1:
    st.markdown("<div class='section-header'>📢 Recommended Channels Details</div>", unsafe_allow_html=True)
    for a in allocations:
        st.markdown(
            f"**{a['channel']}** (Allocation Ratio: {round(a['allocation_ratio']*100)}% | Budget: **${a['budget']:,.2f}**)\n"
            f"- *CPA Baseline*: ${a['cost_per_registration']:.2f} per registration\n"
            f"- *Target registrations*: **{a['estimated_registrations']}** sign-ups\n"
        )
        with st.expander(f"🔍 View selection rationale for {a['channel']}", expanded=False):
            st.write(a.get("selection_rationale", a.get("description", "Selected based on audience targets.")))

with panel_col2:
    st.markdown("<div class='section-header'>⚠️ Risk Assessment & Warnings</div>", unsafe_allow_html=True)
    
    # Risk banner and alerts
    risk_score = risk_result.get("risk_score", 0.0)
    risk_cat = risk_result.get("risk_category", "LOW RISK")
    risk_conf = risk_result.get("risk_score_confidence", 95.0)
    if risk_score <= 10.0:
        st.success(f"🟢 **LOW RISK** (Score: {risk_score}/100 | Confidence: {risk_conf}%): {risk_result['explanation']}")
    elif risk_score <= 35.0:
        st.warning(f"🟡 **MEDIUM RISK** (Score: {risk_score}/100 | Confidence: {risk_conf}%): {risk_result['explanation']}")
    else:
        st.error(f"🔴 **HIGH RISK** (Score: {risk_score}/100 | Confidence: {risk_conf}%): {risk_result['explanation']}")
        
    if risk_result.get('risk_factors'):
        with st.expander("🔍 Explanatory Risk Factors", expanded=True):
            for factor in risk_result['risk_factors']:
                st.markdown(f"- ⚠️ *{factor}*")
            
    # Shortfall calculation and display
    gap_analysis = summary.get("registration_gap_analysis", {})
    st.metric(
        label="Registration shortfalls (%)",
        value=f"{gap_analysis.get('gap_percentage', risk_result['shortfall_percentage'])}%",
        delta=f"{summary['registration_gap']} registrations gap" if summary['registration_gap'] > 0 else None,
        delta_color="inverse"
    )

st.divider()

# Section: Generated Creative Assets
st.markdown("<div class='section-header'>🎨 Generated Campaign Assets (Creative Studio)</div>", unsafe_allow_html=True)
creative_conf = assets.get("messaging_alignment_confidence", 90.0)
st.markdown(f"**Messaging Audience Alignment Confidence**: **{creative_conf}%**")
st.progress(int(creative_conf))
tab1, tab2, tab3, tab4 = st.tabs(["📧 Email Copy", "🔗 LinkedIn Posts", "📸 Instagram Captions", "💡 Ad Headlines"])

with tab1:
    st.markdown("**Email Invitation Draft**")
    st.markdown(f"<div class='asset-box'>{assets.get('email_invitation', assets.get('email_copy', ''))}</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("**LinkedIn Posts**")
    for i, post in enumerate(assets.get('linkedin_posts', [assets.get('linkedin_post', '')])):
        st.markdown(f"*Post Option {i+1}*")
        st.markdown(f"<div class='asset-box'>{post}</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("**Instagram Captions**")
    for i, caption in enumerate(assets.get('instagram_captions', [assets.get('instagram_caption', '')])):
        st.markdown(f"*Caption Option {i+1}*")
        st.markdown(f"<div class='asset-box'>{caption}</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("**Ad Headlines & Call to Actions**")
    col_ad1, col_ad2 = st.columns(2)
    with col_ad1:
        st.markdown("*Recommended Headlines:*")
        for h in assets.get('ad_headlines', [{"channel": "Google Search Ads", "headline": assets.get("google_ads_headline", "")}]):
            st.markdown(f"- **{h['channel']}**: `{h['headline']}`")
    with col_ad2:
        st.markdown("*Call-to-Action Suggestions:*")
        for cta in assets.get('call_to_action', []):
            st.markdown(f"- `{cta}`")
        st.markdown(f"*Recommended Hashtags*: {', '.join(assets.get('hashtags', []))}")
# Section: Approval Workflow
st.markdown("<div class='section-header'>🔐 Campaign Approval Workflow</div>", unsafe_allow_html=True)

if st.session_state.approved:
    st.markdown("<div class='section-header'>📄 Campaign Executive Summary</div>", unsafe_allow_html=True)
    
    # Executive KPI Cards
    exec_col1, exec_col2, exec_col3, exec_col4 = st.columns(4)
    with exec_col1:
        st.metric("Event Name", event_name)
    with exec_col2:
        st.metric("Confidence Score", f"{summary.get('confidence_score', 82)}%")
        conf_interval = summary.get("confidence_interval", {"lower_bound": 0, "upper_bound": 0})
        st.caption(f"Interval: {conf_interval.get('lower_bound')}-{conf_interval.get('upper_bound')} regs")
    with exec_col3:
        st.metric("Risk Score", f"{risk_result.get('risk_score', 0)}/100")
        st.caption(f"Risk confidence: {risk_result.get('risk_score_confidence', 95.0)}%")
    with exec_col4:
        st.metric("Approval Status", "APPROVED")
        st.caption(f"Creative fit alignment: {assets.get('messaging_alignment_confidence', 90.0)}%")

    # Campaign Objective & Details
    st.markdown("### 🎯 Campaign Objective & Profile")
    st.markdown(
        f"**Theme**: {theme}  \n"
        f"**Target Audience**: {target_audience}  \n"
        f"**Location**: {location} | **Event Type**: {event_type}"
    )

    # Allocations and Forecast Table
    st.markdown("### 📊 Recommended Channels, Budgets & Forecasts")
    import pandas as pd
    alloc_data = []
    for a in allocations:
        alloc_data.append({
            "Channel": a["channel"],
            "Allocation Ratio": f"{round(a['allocation_ratio']*100)}%",
            "Budget": f"${a['budget']:,.2f}",
            "CPA Baseline": f"${a['cost_per_registration']:.2f}",
            "Forecasted Registrations": a["estimated_registrations"],
            "Selection Rationale": a.get("selection_rationale", a.get("description", ""))
        })
    st.table(pd.DataFrame(alloc_data))

    # Creative Summary
    st.markdown("### 🎨 Campaign Creative Strategy")
    
    def render_strategic_rec(val):
        if isinstance(val, dict):
            return f"**Recommendation**: {val.get('recommendation')}  \n**Reasoning**: *{val.get('reasoning')}*"
        return str(val)

    st.markdown(f"**Campaign Theme**  \n{render_strategic_rec(assets.get('campaign_theme', 'N/A'))}")
    st.markdown(f"**Messaging Strategy**  \n{render_strategic_rec(assets.get('messaging_strategy', 'N/A'))}")
    st.markdown(f"**Audience Positioning**  \n{render_strategic_rec(assets.get('audience_positioning', 'N/A'))}")
    
    # Final Recommendation
    st.markdown("### 📝 Final Strategic Recommendation")
    st.info(
        f"**Feasibility**: {summary.get('feasibility_message', '')}  \n"
        f"**Optimization Instruction**: {summary.get('optimization_recommendation', '')}  \n"
        f"**Director Decision**: {risk_result.get('explanation', '')}"
    )

    opt_history = summary.get("optimization_history", [])
    if opt_history:
        with st.expander("📊 View Iterative Optimization Steps & ROI Improvements", expanded=True):
            st.markdown("#### Iterative Reallocation Log")
            opt_rows = []
            for item in opt_history:
                step_num = item.get("iteration") if isinstance(item, dict) else item.iteration
                ch_from = item.get("channel_from") if isinstance(item, dict) else item.channel_from
                ch_to = item.get("channel_to") if isinstance(item, dict) else item.channel_to
                amount = item.get("shifted_amount") if isinstance(item, dict) else item.shifted_amount
                gain = item.get("forecast_improvement") if isinstance(item, dict) else item.forecast_improvement
                roi_pct = item.get("roi_improvement_percentage") if isinstance(item, dict) else item.roi_improvement_percentage
                expl = item.get("explanation") if isinstance(item, dict) else item.explanation

                opt_rows.append({
                    "Step": f"Iteration {step_num}",
                    "Source Channel": ch_from,
                    "Target Channel": ch_to,
                    "Shift Amount": f"${amount:,.2f}",
                    "Forecast Gain": f"+{gain} sign-ups",
                    "ROI Gain": f"+{roi_pct:.1f}%",
                    "Rationale": expl
                })
            st.table(pd.DataFrame(opt_rows))

    # Raw JSON data expander
    with st.expander("🔍 View Raw JSON Report Data", expanded=False):
        st.json({
            "status": "APPROVED",
            "campaign_summary": {
                "event_name": event_name,
                "event_type": event_type,
                "location": location,
                "target_audience": target_audience,
                "budget_details": summary,
                "allocations": allocations
            },
            "creative_assets": assets,
            "risk_assessment": risk_result,
            "system_confidence": f"{summary.get('confidence_score', 82)}%"
        })

    if st.button("Reset Approval State", use_container_width=True):
        st.session_state.approved = False
        st.rerun()

else:
    if risk_result['is_approved']:
        st.success("✅ **Low-Risk Plan Detected**: The campaign meets the target criteria and is automatically approved by the orchestrator workflow.")
        if st.button("Generate Final Report"):
            st.session_state.approved = True
            st.rerun()
            
    else:
        st.warning("⚠️ **Approval Required**: The Risk Rating is Medium or High. Manager review is required before this plan can be finalized.")
        
        # Display the prompt
        st.markdown("### Approve Marketing Plan? (Approve / Reject)")
        
        # Display optimization tips in the approval box
        if summary.get("optimization_recommendation"):
            st.info(f"💡 **Optimization recommendation from Data & Budget Agent:**\n{summary['optimization_recommendation']}")
            
        app_col1, app_col2, app_col3 = st.columns(3)
        
        with app_col1:
            if st.button("👍 Approve Plan", use_container_width=True):
                # Extract last event interrupt ID
                session = st.session_state.workflow_session
                last_ev = session.events[-1]
                interrupt_id = None
                if last_ev.content and last_ev.content.parts:
                    for part in last_ev.content.parts:
                        if part.function_call and part.function_call.name == "adk_request_input":
                            interrupt_id = part.function_call.id
                            break
                if interrupt_id:
                    response_event = Event(
                        author="user",
                        invocation_id=last_ev.invocation_id,
                        content={
                            "role": "user",
                            "parts": [
                                {
                                    "function_response": {
                                        "name": "adk_request_input",
                                        "id": interrupt_id,
                                        "response": {
                                            "result": json.dumps({"decision": "approve"})
                                        }
                                    }
                                }
                            ]
                        }
                    )
                    with st.status("Event Marketing Director: Processing approval...", expanded=True) as status:
                        asyncio.run(run_workflow_stream(brief_payload, response_event))
                        status.update(label="Campaign Plan Approved!", state="complete", expanded=False)
                    st.session_state.approved = True
                    st.rerun()
                
        with app_col2:
            if st.button("⚙️ Apply Optimization & Reallocate", use_container_width=True):
                session = st.session_state.workflow_session
                last_ev = session.events[-1]
                interrupt_id = None
                if last_ev.content and last_ev.content.parts:
                    for part in last_ev.content.parts:
                        if part.function_call and part.function_call.name == "adk_request_input":
                            interrupt_id = part.function_call.id
                            break
                if interrupt_id:
                    response_event = Event(
                        author="user",
                        invocation_id=last_ev.invocation_id,
                        content={
                            "role": "user",
                            "parts": [
                                {
                                    "function_response": {
                                        "name": "adk_request_input",
                                        "id": interrupt_id,
                                        "response": {
                                            "result": json.dumps({"decision": "reject", "feedback": "reallocate"})
                                        }
                                    }
                                }
                            ]
                        }
                    )
                    with st.status("Event Marketing Director: Re-routing workflow...", expanded=True) as status:
                        asyncio.run(run_workflow_stream(brief_payload, response_event))
                        status.update(label="Campaign Plan Reallocated with Optimization!", state="complete", expanded=False)
                    st.session_state.optimized = True
                    st.rerun()
                
        with app_col3:
            if st.button("👎 Reject & Cancel Campaign", use_container_width=True):
                st.error("Campaign plan rejected. Please modify details in the Event Brief sidebar to recalculate.")
