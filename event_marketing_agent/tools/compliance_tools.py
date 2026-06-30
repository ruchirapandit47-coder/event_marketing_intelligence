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

"""Tools for campaign risk auditing and compliance evaluation."""

from typing import Dict, Any, List


def evaluate_campaign_risks(
    event_name: str,
    event_type: str,
    target_audience: str,
    marketing_budget: float,
    registration_goal: int,
    allocations: List[Dict[str, Any]],
    summary: Dict[str, Any]
) -> Dict[str, Any]:
    """Audit a marketing campaign plan to identify potential budget, channel, goal, and audience risks.

    Args:
        event_name: Name of the event.
        event_type: Type of the event.
        target_audience: Target audience description.
        marketing_budget: Marketing budget in USD.
        registration_goal: Target number of registrations.
        allocations: Calculated channel allocations.
        summary: Consolidated budget summary containing estimated registrations.

    Returns:
        A dictionary containing:
            - shortfall_percentage: Registration gap percentage.
            - risk_category: LOW RISK, MEDIUM RISK, or HIGH RISK.
            - warnings: List of warnings generated.
            - content_audits: Asset checks.
            - is_approved: True if Low Risk, False if Medium or High Risk.
            - explanation: Executive summary of risks.
    """
    warnings = []
    
    # 1. Budget Over-Allocation Check
    total_allocated = sum(item.get("budget", 0.0) for item in allocations)
    if total_allocated > marketing_budget + 0.01:
        warnings.append(
            f"Budget over-allocation detected: Total channel budget (${total_allocated:.2f}) "
            f"exceeds the overall campaign budget limit (${marketing_budget:.2f})."
        )

    # 2. Unrealistic Registration Targets Check
    # Calculate required cost-per-registration (CPA)
    required_cpa = marketing_budget / registration_goal if registration_goal > 0 else 0.0
    event_type_lower = event_type.lower()
    
    # B2B or Tech Developer events are high cost. Baselines are $50-$85.
    # If required CPA is under $20 for B2B/Tech, it's highly unrealistic.
    is_tech_b2b = any(k in event_type_lower for k in ["b2b", "dev", "tech", "software", "corp"])
    cpa_threshold = 20.0 if is_tech_b2b else 10.0
    
    if required_cpa < cpa_threshold and registration_goal > 0:
        warnings.append(
            f"Unrealistic registration target: The required Cost-Per-Registration (${required_cpa:.2f}) "
            f"is below the sustainable industry baseline (${cpa_threshold:.2f}) for {event_type} events."
        )

    # 3. Low-Performing Channel Combinations Check
    audience_lower = target_audience.lower()
    channels = [item.get("channel", "") for item in allocations]
    
    if is_tech_b2b:
        # Tech B2B campaigns should not rely heavily on TikTok or Local listings as primary channels
        low_perf_b2b = ["TikTok Ads", "Local Event Listings", "Meta Ads (FB/IG)"]
        overlapping_low = [c for c in channels if c in low_perf_b2b]
        
        # Check budget ratio of low performing channels
        low_perf_budget = sum(item.get("budget", 0.0) for item in allocations if item.get("channel") in low_perf_b2b)
        if low_perf_budget > marketing_budget * 0.35:
            warnings.append(
                f"Low-performing B2B channel combination: Allocating excessive budget ({round(low_perf_budget/marketing_budget*100)}%) "
                f"to low-performing channels {overlapping_low} for a professional B2B/Tech audience."
            )
    else:
        # Consumer/Youth events relying heavily on LinkedIn Ads
        if "LinkedIn Ads" in channels:
            li_budget = sum(item.get("budget", 0.0) for item in allocations if item.get("channel") == "LinkedIn Ads")
            if li_budget > marketing_budget * 0.30:
                warnings.append(
                    f"Low-performing Consumer channel combination: LinkedIn Ads budget (${li_budget:.2f}) "
                    f"is too high for a Consumer/Youth audience segment."
                )

    # 4. Missing Audience Information Check
    clean_audience = target_audience.strip()
    if not clean_audience or len(clean_audience) < 5 or any(word in clean_audience.lower() for word in ["everyone", "any", "all", "unknown", "n/a"]):
        warnings.append(
            "Missing or inadequate audience specification: Target audience demographics must be "
            "specifically defined for accurate campaign targeting."
        )

    # 5. Risk Categorization based on Shortfall
    # Shortfall % = (registration_gap / registration_goal) * 100
    registration_gap = summary.get("registration_gap", 0)
    shortfall_percentage = (registration_gap / registration_goal * 100.0) if registration_goal > 0 else 0.0
    
    # Categorize Risk
    # 0-5% shortfall = LOW RISK
    # 5-15% shortfall = MEDIUM RISK
    # 15%+ shortfall = HIGH RISK
    # If there are critical warnings, raise the risk level
    if shortfall_percentage <= 5.0:
        risk_category = "LOW RISK"
    elif shortfall_percentage <= 15.0:
        risk_category = "MEDIUM RISK"
    else:
        risk_category = "HIGH RISK"

    # Escalate risk if critical warnings exist
    if warnings and risk_category == "LOW RISK":
        # If there are serious warnings, escalate to at least Medium Risk
        risk_category = "MEDIUM RISK"

    # Require manager approval (is_approved = False) if risk is Medium or High
    is_approved = risk_category == "LOW RISK"

    # Expose audits structure
    content_audits = [
        {
            "item": "Budget Allocations",
            "status": "FAILED" if any("budget" in w.lower() or "channel" in w.lower() for w in warnings) else "PASSED",
            "issues": [w for w in warnings if "budget" in w.lower() or "channel" in w.lower()]
        },
        {
            "item": "Target Settings",
            "status": "FAILED" if any("target" in w.lower() or "audience" in w.lower() for w in warnings) else "PASSED",
            "issues": [w for w in warnings if "target" in w.lower() or "audience" in w.lower()]
        }
    ]

    explanation = (
        f"Campaign risk evaluated as {risk_category} based on a registration shortfall of "
        f"{shortfall_percentage:.1f}% ({registration_gap}/{registration_goal} registrations gap). "
    )
    if warnings:
        explanation += f"Identified {len(warnings)} compliance warnings."
    else:
        explanation += "No compliance or target warnings identified."

    return {
        "shortfall_percentage": round(shortfall_percentage, 2),
        "risk_category": risk_category,
        "warnings": warnings,
        "content_audits": content_audits,
        "is_approved": is_approved,
        "explanation": explanation
    }
