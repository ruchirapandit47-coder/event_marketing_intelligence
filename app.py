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

# Import our tools directly to run them locally in the UI
from event_marketing_agent.tools.budget_tools import recommend_channels_and_allocate_budget
from event_marketing_agent.tools.compliance_tools import evaluate_campaign_risks

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

# Run the simulation workflow when triggered
if generate_clicked or st.session_state.reallocated:
    with st.status("Event Marketing Director: Orchestrating agent workflow...", expanded=True) as status:
        st.write("🔍 **[Director] Analyzing event brief goals...**")
        time.sleep(0.5)
        
        st.write("📊 **[Data & Budget Agent] Recommending channels and calculating budget allocation...**")
        time.sleep(0.6)
        db_res = recommend_channels_and_allocate_budget(
            event_type=event_type,
            target_audience=target_audience,
            marketing_budget=marketing_budget,
            registration_goal=registration_goal,
            apply_optimization=st.session_state.optimized
        )
        allocations_res = db_res["allocations"]
        summary_res = db_res["summary"]
        
        st.write("🎨 **[Creative Studio Agent] Crafting campaign headlines and copywriting copy assets...**")
        time.sleep(0.6)
        channels_res = [a["channel"] for a in allocations_res]
        assets_res = mock_asset_generation(event_name, event_type, theme, target_audience, channels_res)
        
        st.write("⚠️ **[Risk & Compliance Agent] Auditing plans for budget and shortfall compliance...**")
        time.sleep(0.6)
        risk_res = evaluate_campaign_risks(
            event_name=event_name,
            event_type=event_type,
            target_audience=target_audience,
            marketing_budget=marketing_budget,
            registration_goal=registration_goal,
            allocations=allocations_res,
            summary=summary_res
        )
        
        # Save results to session state
        st.session_state.db_result = db_res
        st.session_state.risk_result = risk_res
        st.session_state.assets = assets_res
        st.session_state.generated = True
        st.session_state.reallocated = False
        
        status.update(label="Campaign Plan Generated successfully!", state="complete", expanded=False)

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

# Retrieve results from state for rendering
db_result = st.session_state.db_result
risk_result = st.session_state.risk_result
assets = st.session_state.assets

allocations = db_result["allocations"]
summary = db_result["summary"]

# DISPLAY DASHBOARD CONTENT
# Section 1: Executive KPI Cards
st.markdown("<div class='section-header'>📊 Executive Campaign Metrics</div>", unsafe_allow_html=True)
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
    # Color check for target met
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
    risk_color = "#137333" if risk_result['risk_category'] == "LOW RISK" else ("#f29900" if risk_result['risk_category'] == "MEDIUM RISK" else "#c5221f")
    st.markdown(f"""
    <div class='metric-card' style='border-left-color: {risk_color};'>
        <div class='metric-label'>Campaign Risk Rating</div>
        <div class='metric-value' style='color: {risk_color};'>{risk_result['risk_category']}</div>
    </div>
    """, unsafe_allow_html=True)

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

# Panels: Channel Recommendations & Risk Audits
panel_col1, panel_col2 = st.columns([3, 2])

with panel_col1:
    st.markdown("<div class='section-header'>📢 Recommended Channels Details</div>", unsafe_allow_html=True)
    for a in allocations:
        st.markdown(
            f"**{a['channel']}** (Allocation Ratio: {round(a['allocation_ratio']*100)}% | Budget: **${a['budget']:,.2f}**)\n"
            f"- *CPA Baseline*: ${a['cost_per_registration']:.2f} per registration\n"
            f"- *Target registrations*: **{a['estimated_registrations']}** sign-ups\n"
            f"- *Role*: {a['description']}\n"
        )

with panel_col2:
    st.markdown("<div class='section-header'>⚠️ Risk Assessment & Warnings</div>", unsafe_allow_html=True)
    
    # Risk banner and alerts
    if risk_result['risk_category'] == "LOW RISK":
        st.success(f"🟢 **LOW RISK**: {risk_result['explanation']}")
    elif risk_result['risk_category'] == "MEDIUM RISK":
        st.warning(f"🟡 **MEDIUM RISK**: {risk_result['explanation']}")
    else:
        st.error(f"🔴 **HIGH RISK**: {risk_result['explanation']}")
        
    if risk_result['warnings']:
        st.markdown("**Compliance Warnings Issued:**")
        for warning in risk_result['warnings']:
            st.markdown(f"- ⚠️ *{warning}*")
            
    # Shortfall calculation and display
    st.metric(
        label="Registration shortfalls (%)",
        value=f"{risk_result['shortfall_percentage']}%",
        delta=f"{summary['registration_gap']} registrations gap" if summary['registration_gap'] > 0 else None,
        delta_color="inverse"
    )

# Section: Generated Creative Assets
st.markdown("<div class='section-header'>🎨 Generated Campaign Assets (Creative Studio)</div>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs(["📧 Email Copy", "🔗 LinkedIn Posts", "📸 Instagram Captions", "💡 Ad Headlines"])

with tab1:
    st.markdown("**Email Invitation Draft**")
    st.markdown(f"<div class='asset-box'>{assets['email_invitation']}</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("**LinkedIn Posts**")
    for i, post in enumerate(assets['linkedin_posts']):
        st.markdown(f"*Post Option {i+1}*")
        st.markdown(f"<div class='asset-box'>{post}</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("**Instagram Captions**")
    for i, caption in enumerate(assets['instagram_captions']):
        st.markdown(f"*Caption Option {i+1}*")
        st.markdown(f"<div class='asset-box'>{caption}</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("**Ad Headlines & Call to Actions**")
    col_ad1, col_ad2 = st.columns(2)
    with col_ad1:
        st.markdown("*Recommended Headlines:*")
        for h in assets['ad_headlines']:
            st.markdown(f"- **{h['channel']}**: `{h['headline']}`")
    with col_ad2:
        st.markdown("*Call-to-Action Suggestions:*")
        for cta in assets['call_to_action']:
            st.markdown(f"- `{cta}`")
        st.markdown(f"*Recommended Hashtags*: {', '.join(assets['hashtags'])}")

# Section: Approval Workflow
st.markdown("<div class='section-header'>🔐 Campaign Approval Workflow</div>", unsafe_allow_html=True)

if st.session_state.approved:
    st.success("🎉 **Campaign Approved!** The Event Marketing Director has completed the workflow. The final report is ready to print.")
    
    # Final Report Output
    with st.expander("📄 View Final Approved Report", expanded=True):
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
            "creative_assets": {
                "email_copy": assets['email_invitation'],
                "linkedin_posts": assets['linkedin_posts'],
                "ad_headlines": assets['ad_headlines']
            },
            "risk_assessment": risk_result,
            "system_confidence": f"{summary['confidence_score']}%"
        })
    if st.button("Reset Approval State"):
        st.session_state.approved = False
        st.rerun()

else:
    # If the workflow is LOW RISK, it bypasses human approval
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
                st.session_state.approved = True
                st.rerun()
                
        with app_col2:
            if st.button("⚙️ Apply Optimization & Reallocate", use_container_width=True):
                st.session_state.optimized = True
                st.session_state.reallocated = True
                st.rerun()
                
        with app_col3:
            if st.button("👎 Reject & Cancel Campaign", use_container_width=True):
                st.error("Campaign plan rejected. Please modify details in the Event Brief sidebar to recalculate.")
                
        if st.session_state.reallocated:
            st.info("🔄 Optimized allocation settings applied! The budget has been dynamically reallocated to maximize registration forecast.")
