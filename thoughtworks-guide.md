# JOI Delivery Interview Guide

## Goal
Prepare this FastAPI codebase so you can quickly handle an interview prompt such as:
- fix the `inventory` endpoint
- build two AI agents using a local Ollama model

## What the codebase already has
- FastAPI app entrypoint: `src/joi_delivery/main.py`
- Routers: `src/joi_delivery/router.py`
- Cart endpoints: `src/joi_delivery/controller/cart_controller.py`
- Inventory endpoint stub: `src/joi_delivery/controller/inventory_controller.py`
- Seed data: `src/joi_delivery/generator/app_initializer.py`
- Product lookup service: `src/joi_delivery/service/product_service.py`
- Inventory test placeholder: `tests/controller/test_inventory_controller.py`

## Immediate setup checklist
1. Install dependencies.
   - `poetry install --with dev`
2. Run the API locally.
   - `poetry run python -m uvicorn joi_delivery.main:app --reload --port 8020`
3. Verify system health.
   - open `http://localhost:8020/health`
   - open `http://localhost:8020/docs`
4. Install Ollama.
   - `ollama pull llama3.2`
   - `ollama run llama3.2 "hello"`
5. Install one agent framework.
   - Recommended: LangGraph
6. Prove local LLM wiring with a minimal script.
   - one `llm.invoke("hello")` call against local Ollama

## Read the codebase in this order
1. `README.md`
   - understand the exposed APIs and sample payloads
2. `src/joi_delivery/main.py`
   - see how services are registered on `app.state`
3. `src/joi_delivery/generator/app_initializer.py`
   - learn the seed users, stores, carts, and products
4. `src/joi_delivery/controller/*.py`
   - see current API style
5. `src/joi_delivery/service/*.py`
   - find where business logic belongs
6. `tests/controller/*.py`
   - infer expected behavior from test patterns

## What is likely broken right now
### Inventory endpoint
Current state:
- `src/joi_delivery/controller/inventory_controller.py` only returns HTTP 200 with no body
- `tests/controller/test_inventory_controller.py` only checks status code and still contains `# add required mocking.`
- stores are seeded without inventory attached, even though products reference stores

That means an interview task like "fix the inventory endpoint" probably expects you to:
1. define what inventory health response should look like
2. add service logic to compute it
3. wire the controller to use that service
4. update seed/setup if needed so stores know their products
5. write or finish tests

## Suggested implementation plan for the inventory task
1. Inspect how inventory health should be inferred.
   - likely from `grocery_products` grouped by `store.outlet_id`
   - fields may include store id, total products, low-stock count, out-of-stock count, and product details
2. Add an inventory-focused service.
   - example file: `src/joi_delivery/service/inventory_service.py`
3. Register the service in `src/joi_delivery/main.py`.
4. Expose it through a dependency helper in `src/joi_delivery/dependencies.py`.
5. Replace the stub in `src/joi_delivery/controller/inventory_controller.py`.
6. Return JSON, not an empty `Response`.
7. Handle bad `store_id` cleanly.
   - either `404` or an empty result; choose one and keep it consistent in tests
8. Write controller tests first if time allows.
   - success case for `store101`
   - missing store case
   - if applicable, low-stock / out-of-stock classification case

## Likely inventory response shape
Use something simple and defensible, for example:
```json
{
  "store_id": "store101",
  "store_name": "Fresh Picks",
  "total_products": 3,
  "in_stock": 3,
  "low_stock": 0,
  "out_of_stock": 0,
  "products": [
    {
      "product_id": "product101",
      "product_name": "Wheat Bread",
      "available_stock": 30,
      "threshold": 10,
      "status": "healthy"
    }
  ]
}
```

## Two-agent task: what they are likely testing
They are usually not testing fancy agent marketing. They are testing whether you can:
- choose a clean agent boundary
- integrate a local LLM
- keep deterministic business logic outside the LLM
- connect agents to existing APIs or services
- explain tradeoffs clearly

## Recommended two-agent design
Use LangGraph with two focused agents.

### Agent 1: Customer Intent Agent
Responsibility:
- interpret user request
- classify intent
- extract entities such as `user_id`, `store_id`, `product_id`
- decide whether the request is about cart, inventory, or general help

Inputs:
- raw user message

Outputs:
- structured task object
- example: `{ "intent": "inventory_health", "store_id": "store101" }`

### Agent 2: Operations Agent
Responsibility:
- call deterministic tools or service functions
- fetch inventory/cart/product data
- produce final answer grounded in system data

Inputs:
- structured task from Agent 1

Outputs:
- final response for the user

## Why this split works
- intent interpretation uses the LLM where it adds value
- data retrieval and business rules stay deterministic
- debugging is easier because planning and execution are separated
- it is small enough to build in an interview

## Minimal implementation path for the agents
1. Create a small `agents/` package.
2. Add Ollama client wiring.
3. Add a schema for the intent agent output.
4. Implement Agent 1 prompt for intent classification and entity extraction.
5. Implement Agent 2 tool functions that call existing services or HTTP endpoints.
6. Build a simple LangGraph flow:
   - input node
   - intent node
   - route by intent
   - execute tool node
   - respond node
7. Add one thin API endpoint for agent interaction.
   - example: `POST /ai/query`
8. Demo with 2-3 prompts only.
   - "Show inventory health for store101"
   - "Add product101 from store101 to user101's cart"
   - "What is in user101's cart?"

## Keep the agent scope tight
Do not try to build a general autonomous system.
For the interview, keep it to:
- a small state object
- a couple of tools
- explicit routing
- predictable outputs

## Tooling boundaries you should state during the interview
- LLM decides intent and extracts entities
- Python services enforce business rules
- FastAPI remains the integration surface
- tests validate behavior without depending on live LLM output where possible

## Practical interview sequence
1. Start by running the current tests.
2. Open the broken controller and test.
3. Fix the inventory endpoint first.
4. Add or repair tests.
5. Only then start agent scaffolding.
6. Wire Ollama with the smallest possible successful path.
7. Build the second agent only after the first end-to-end path works.
8. Keep a fallback demo path using direct service calls in case the LLM prompt needs tuning.

## What to say if asked about framework choice
Recommended answer:
- "I would use LangGraph because this task is a small, stateful workflow with explicit routing between intent parsing and deterministic tool execution. That gives me enough control to keep behavior testable while still using the LLM where it helps."

## What to prepare before the interview day
- have the app running on `localhost:8020`
- have Ollama working locally with `llama3.2`
- have one script that proves local model invocation
- know the seed entities by memory: `user101`, `store101`, `product101`
- know where to edit controller, service, dependency, and test files
- decide your inventory response contract before coding
- have a minimal LangGraph skeleton ready in your head

## Strong execution strategy during the interview
- clarify response shape before implementing the inventory fix
- code the simplest correct path first
- keep business logic in services, not controllers
- write at least one meaningful test for every change
- avoid overengineering the agent system
- optimize for a working demo over a broad design

## If they ask for extensions after the basic solution
Reasonable follow-ups:
1. add store not found handling
2. add inventory status categories such as `healthy`, `low`, `out_of_stock`
3. let the agent call the cart flow as another tool
4. add prompt/response logging for debugging
5. add contract tests for the AI endpoint

## Suggested first commands on the day
```bash
poetry install --with dev
poetry run pytest
poetry run python -m uvicorn joi_delivery.main:app --reload --port 8020
ollama run llama3.2 "hello"
```

## Bottom line
Your highest-value path is:
1. understand the seed data and service wiring
2. fix `inventory` properly with tests
3. build two narrowly scoped agents on top of existing services
4. keep the demo deterministic and explain your boundaries clearly
