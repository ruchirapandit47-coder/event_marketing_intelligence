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

"""Tools for marketing channel recommendations, budget allocations, and registration forecasting."""

from typing import Dict, Any, List

import os
import json

# Dynamically load benchmarks and default weights from channels.json
current_dir = os.path.dirname(os.path.abspath(__file__))
channels_json_path = os.path.join(current_dir, "..", "channels.json")

with open(channels_json_path, "r", encoding="utf-8") as f:
    CHANNELS_CONFIG = json.load(f)

CHANNEL_BENCHMARKS = CHANNELS_CONFIG["channels"]
BUDGET_WEIGHTS = CHANNELS_CONFIG["default_budget_weights"]


def recommend_channels_and_allocate_budget(
    event_type: str,
    target_audience: str,
    marketing_budget: float,
    registration_goal: int,
    apply_optimization: bool = False,
) -> Dict[str, Any]:
    """Analyze event attributes to recommend marketing channels, allocate budget, and forecast registrations.

    Args:
        event_type: Type of event, e.g., 'B2B', 'Developer', 'Consumer', 'Academic', 'Community'.
        target_audience: Target demographic, e.g., 'Software Engineers', 'Marketing Professionals', 'College Students'.
        marketing_budget: Total marketing budget in USD.
        registration_goal: Target number of registrations.
        apply_optimization: If True, applies budget shift optimizations directly.

    Returns:
        A dictionary containing channel allocations, campaign summary, optimization, and confidence score.
    """
    event_type_lower = event_type.lower()
    audience_lower = target_audience.lower()

    # Step 1: Channel selection based on event type and audience
    if "developer" in event_type_lower or "software" in audience_lower or "tech" in event_type_lower:
        strategy_weights = BUDGET_WEIGHTS["developer"]
    elif "b2b" in event_type_lower or "corporate" in event_type_lower or "professional" in audience_lower:
        strategy_weights = BUDGET_WEIGHTS["b2b"]
    elif "consumer" in event_type_lower or "b2c" in event_type_lower or "student" in audience_lower or "youth" in audience_lower:
        strategy_weights = BUDGET_WEIGHTS["consumer"]
    else:
        strategy_weights = BUDGET_WEIGHTS["default"]

    # Convert weights dict to selected_channels list of tuples
    selected_channels = list(strategy_weights.items())

    # Step 2 & 3: Allocate budget, forecast registrations, and calculate cost per registration
    allocations = []
    total_forecasted_registrations = 0.0

    for channel_name, ratio in selected_channels:
        channel_budget = marketing_budget * ratio
        cpr = CHANNEL_BENCHMARKS[channel_name]["cpr"]
        forecasted_regs = int(channel_budget / cpr)

        allocations.append({
            "channel": channel_name,
            "allocation_ratio": channel_budget / marketing_budget,
            "budget": round(channel_budget, 2),
            "cost_per_registration": cpr,
            "estimated_registrations": forecasted_regs,
            "description": CHANNEL_BENCHMARKS[channel_name]["description"],
            "selection_rationale": CHANNEL_BENCHMARKS[channel_name]["description"]
        })
        total_forecasted_registrations += forecasted_regs

    # Step 4: Feasibility & Gap analysis (Initial state)
    total_forecasted_registrations = int(total_forecasted_registrations)
    initial_forecast = total_forecasted_registrations
    registration_gap = registration_goal - total_forecasted_registrations
    is_feasible = total_forecasted_registrations >= registration_goal

    # Iterative Optimization Loop (up to 3 steps) if shortfall exists
    optimization_history = []
    optimization_recommendation = ""
    reallocation_recommendations = []
    improvement_estimate = {}

    # If shortfall exists, simulate or apply iterative optimization
    if not is_feasible:
        current_forecast = total_forecasted_registrations
        temp_allocs = [dict(a) for a in allocations]

        for iteration in range(1, 4):
            gap = registration_goal - current_forecast
            if gap <= 0:
                break

            # Find active channel with the highest CPR
            active_highest = [a for a in temp_allocs if a["budget"] > 0]
            if not active_highest:
                break
            sorted_highest = sorted(active_highest, key=lambda x: x["cost_per_registration"], reverse=True)
            highest_channel = sorted_highest[0]

            # Find active channel with the lowest CPR
            sorted_lowest = sorted(temp_allocs, key=lambda x: x["cost_per_registration"])
            lowest_channel = sorted_lowest[0]

            if highest_channel["channel"] == lowest_channel["channel"]:
                break

            # Shift $500 or remainder of budget
            shift_amount = min(highest_channel["budget"], 500.0)
            if shift_amount <= 0:
                break

            prev_regs = current_forecast
            highest_channel["budget"] = round(highest_channel["budget"] - shift_amount, 2)
            highest_channel["estimated_registrations"] = int(highest_channel["budget"] / highest_channel["cost_per_registration"])
            highest_channel["allocation_ratio"] = highest_channel["budget"] / marketing_budget

            lowest_channel["budget"] = round(lowest_channel["budget"] + shift_amount, 2)
            lowest_channel["estimated_registrations"] = int(lowest_channel["budget"] / lowest_channel["cost_per_registration"])
            lowest_channel["allocation_ratio"] = lowest_channel["budget"] / marketing_budget

            current_forecast = sum(a["estimated_registrations"] for a in temp_allocs)
            forecast_gain = current_forecast - prev_regs
            roi_gain_pct = round((forecast_gain / prev_regs) * 100, 2) if prev_regs > 0 else 0.0

            reason = (
                f"Shifted ${shift_amount:,.0f} from {highest_channel['channel']} to {lowest_channel['channel']} "
                f"to leverage lower Cost-Per-Registration (${lowest_channel['cost_per_registration']:.2f} vs ${highest_channel['cost_per_registration']:.2f})."
            )

            optimization_history.append({
                "iteration": iteration,
                "channel_from": highest_channel["channel"],
                "channel_to": lowest_channel["channel"],
                "shifted_amount": shift_amount,
                "forecast_improvement": forecast_gain,
                "roi_improvement_percentage": roi_gain_pct,
                "explanation": reason
            })

        if optimization_history:
            total_gain = current_forecast - initial_forecast
            optimization_recommendation = (
                f"Move budget from high-CPR to low-CPR channels over {len(optimization_history)} steps. "
                f"Expected registrations: {initial_forecast} -> {current_forecast}."
            )
            reallocation_recommendations = [
                {
                    "source_channel": step["channel_from"],
                    "target_channel": step["channel_to"],
                    "amount": step["shifted_amount"],
                    "reason": step["explanation"]
                }
                for step in optimization_history
            ]
            improvement_estimate = {
                "additional_registrations": total_gain,
                "new_forecasted_total": current_forecast,
                "new_registration_gap": max(0, registration_goal - current_forecast),
                "new_feasibility_status": "FEASIBLE" if current_forecast >= registration_goal else "RISKY"
            }

            # Apply optimized allocations if requested
            if apply_optimization:
                allocations = temp_allocs
                total_forecasted_registrations = current_forecast
                registration_gap = registration_goal - total_forecasted_registrations
                is_feasible = total_forecasted_registrations >= registration_goal

    else:
        optimization_recommendation = "Current allocation is optimized. No budget shift required."
        reallocation_recommendations = []
        improvement_estimate = {
            "additional_registrations": 0,
            "new_forecasted_total": total_forecasted_registrations,
            "new_registration_gap": 0,
            "new_feasibility_status": "FEASIBLE"
        }

    # Final calculations after possible optimization application
    overall_cpr = marketing_budget / total_forecasted_registrations if total_forecasted_registrations > 0 else 0.0
    feasibility_status = "FEASIBLE" if is_feasible else "RISKY"
    feasibility_message = (
        f"The campaign is projected to reach {total_forecasted_registrations} registrations, "
        f"meeting the goal of {registration_goal}."
        if is_feasible else
        f"The campaign is projected to reach {total_forecasted_registrations} registrations, "
        f"leaving a gap of {registration_gap} registrations from the target goal of {registration_goal}."
    )

    confidence_score = 82.0 if is_feasible else 65.0

    return {
        "event_brief": {
            "event_type": event_type,
            "target_audience": target_audience,
            "marketing_budget": marketing_budget,
            "registration_goal": registration_goal
        },
        "allocations": allocations,
        "summary": {
            "total_budget": marketing_budget,
            "total_estimated_registrations": total_forecasted_registrations,
            "average_cost_per_registration": round(overall_cpr, 2),
            "registration_goal": registration_goal,
            "registration_gap": max(0, registration_gap),
            "feasibility_status": feasibility_status,
            "feasibility_message": feasibility_message,
            "confidence_score": confidence_score,
            "optimization_recommendation": optimization_recommendation,
            "confidence_interval": {
                "lower_bound": int(total_forecasted_registrations * 0.90),
                "upper_bound": int(total_forecasted_registrations * 1.10)
            },
            
            # Enterprise Decision Support System extensions
            "forecast_confidence": {
                "score": confidence_score,
                "confidence_level": "High" if confidence_score >= 80 else ("Medium" if confidence_score >= 50 else "Low"),
                "rationales": [
                    "Sufficient budget allocated to high-performing baseline channels.",
                    "Low registration gap ensures high likelihood of campaign success." if registration_gap <= 0 else "Shortfall present; recommend applying reallocation optimization."
                ]
            },
            "registration_gap_analysis": {
                "gap_count": max(0, registration_gap),
                "gap_percentage": round((max(0, registration_gap) / registration_goal) * 100, 2) if registration_goal > 0 else 0.0,
                "is_gap_present": registration_gap > 0
            },
            "reallocation_recommendations": reallocation_recommendations,
            "improvement_estimate": improvement_estimate,
            "optimization_history": optimization_history
        }
    }
