# Event Marketing Intelligence Agent

This project is a graph-based multi-agent system built using **ADK 2.0 (Agent Development Kit)**. It is designed to assist event organizers in planning campaigns, allocating marketing budgets, forecasting registrations, and generating creative assets.

## Project Structure

- `event_marketing_agent/agent.py`: Orchestrates the graph-based workflow.
- `event_marketing_agent/config.py`: Centralized configuration.
- `event_marketing_agent/tools/budget_tools.py`: Contains marketing allocation and registration forecasting tools.
- `event_marketing_agent/sub_agents/`: Sub-agents for specific tasks.
  - `data_budget`: Recommends channels, allocates budget, and forecasts registrations.
  - `creative_studio`: Generates channel-specific advertising copy.
  - `risk_compliance`: Audits the budget allocations and copywriting content for potential compliance risks.

## Setup & Running

1. **Install Poetry**:
   Ensure you have Poetry installed, then run:
   ```bash
   poetry install
   ```

2. **Configure environment**:
   Copy `.env.example` to `.env` and fill in your API Key or Google Cloud credentials:
   ```bash
   cp .env.example .env
   ```

3. **Run the agent locally**:
   ```bash
   poetry run adk run .
   ```
