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

"""Verification script to test importability and structure of the event marketing agent."""

import sys

try:
    from event_marketing_agent import root_agent
    
    print("====================================================")
    print("Event Marketing Intelligence Agent Initialization")
    print("====================================================")
    print(f"Workflow Name: {root_agent.name}")
    print("\nWorkflow Graph Edges:")
    
    # Iterate through workflow edges and display transitions
    for edge in root_agent.edges:
        if isinstance(edge, tuple):
            if len(edge) == 2:
                src, dst = edge
                src_name = getattr(src, "name", src.__name__ if callable(src) else str(src))
                if isinstance(dst, dict):
                    dst_str = "{ " + ", ".join(f"'{k}': {getattr(v, 'name', v.__name__ if callable(v) else str(v))}" for k, v in dst.items()) + " }"
                else:
                    dst_str = getattr(dst, "name", dst.__name__ if callable(dst) else str(dst))
                print(f"  {src_name} ---> {dst_str}")
            elif len(edge) == 3:
                src, mid, dst = edge
                src_name = getattr(src, "name", src.__name__ if callable(src) else str(src))
                mid_name = getattr(mid, "name", mid.__name__ if callable(mid) else str(mid))
                dst_name = getattr(dst, "name", dst.__name__ if callable(dst) else str(dst))
                print(f"  {src_name} ---> {mid_name} ---> {dst_name}")
                
    print("\nSTATUS: SUCCESS")
    print("All agents, Pydantic schemas, math tools, and graph configurations loaded successfully.")
    print("====================================================")
    sys.exit(0)
    
except Exception as e:
    print("STATUS: FAILED", file=sys.stderr)
    print(f"Error during agent workflow initialization: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
