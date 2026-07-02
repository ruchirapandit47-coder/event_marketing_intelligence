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

"""Test script for running the Event Marketing workflow async generator."""

import asyncio
import json
from google.adk import Context, Event
from google.adk.events import RequestInput
from event_marketing_agent.agent import root_agent
from typing import Dict, List, Any, Optional


class MockSession:
    def __init__(self):
        self.id = "test-session"
        self.state = {}
        self.events = []

    def model_copy(self, **kwargs):
        return self


class MockInvocationContext:
    def __init__(self):
        self.session = MockSession()
        self.invocation_id = "test-invocation"
        self.branch = None
        self.isolation_scope = None
        self._event_queue = asyncio.Queue()
        self.end_invocation = False

    def model_copy(self, **kwargs):
        return self

    async def _enqueue_event(self, event):
        self.session.events.append(event)


async def main():
    ctx = Context(MockInvocationContext())
    brief = {
        'event_name': 'Tech Agent Summit',
        'event_type': 'B2B',
        'location': 'Virtual',
        'target_audience': 'Developers',
        'marketing_budget': 10000.0,
        'registration_goal': 350,
        'theme': 'ADK 2.0 Integration'
    }
    
    print("--- Running Initial Workflow ---")
    async for ev in root_agent.run(ctx=ctx, node_input=brief):
        pass
        
    print(f"\nInitial run finished. Risk: {ctx.session.state.get('risk_assessment_results', {}).get('risk_category')}")
    print(f"Total events so far: {len(ctx.session.events)}")
    
    # Extract the interrupt ID from the last event
    last_ev = ctx.session.events[-1]
    interrupt_id = None
    if last_ev.content and last_ev.content.parts:
        for part in last_ev.content.parts:
            if part.function_call and part.function_call.name == "adk_request_input":
                interrupt_id = part.function_call.id
                break
                
    print("Extracted interrupt ID:", interrupt_id)
    
    # Build user response event
    decision_dict = {"decision": "reject", "feedback": "Optimize mix."}
    response_event = Event(
        author="user",
        invocation_id=ctx._invocation_context.invocation_id,
        content={
            "role": "user",
            "parts": [
                {
                    "function_response": {
                        "name": "adk_request_input",
                        "id": interrupt_id,
                        "response": {
                            "result": json.dumps(decision_dict)
                        }
                    }
                }
            ]
        }
    )
    
    # Append the response to session events
    ctx.session.events.append(response_event)
    
    print("\n--- Resuming Workflow with Reject/Reallocate Response ---")
    async for ev in root_agent.run(ctx=ctx, node_input=brief):
        pass
        
    print(f"\nResumed run finished.")
    print(f"Total events after resume: {len(ctx.session.events)}")
    
    # Print detail of events from 8 onwards
    for idx in range(8, len(ctx.session.events)):
        ev = ctx.session.events[idx]
        node_name = ev.node_info.path if ev.node_info else 'Unknown'
        print(f"\nEvent {idx}: path={node_name}")
        print(f"  Type: {type(ev)}")
        if ev.output:
            if hasattr(type(ev.output), "model_fields"):
                keys_list = list(type(ev.output).model_fields.keys())
            elif hasattr(ev.output, "keys"):
                keys_list = list(ev.output.keys())
            else:
                keys_list = []
            print(f"  Output keys: {keys_list}")
        else:
            print("  Output keys: None")
        if ev.content:
            print(f"  Content role: {ev.content.role}")
            print(f"  Content parts: {len(ev.content.parts)}")
            
    print(f"\nFinal State apply_optimization_directly: {ctx.session.state.get('apply_optimization_directly')}")
    print(f"Final State risk_category: {ctx.session.state.get('risk_assessment_results', {}).get('risk_category')}")


if __name__ == "__main__":
    asyncio.run(main())
