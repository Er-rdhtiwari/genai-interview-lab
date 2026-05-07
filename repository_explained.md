# JOI Delivery Repository Explained

## What this project is
This repository is a small FastAPI application for a grocery delivery platform.

Think of it as a beginner-friendly backend service that answers HTTP requests such as:
- add a product to a user's cart
- view a user's cart
- check system health
- check inventory health for a store

It is not a full production app yet. It is a simplified codebase meant for exercises, interviews, and learning.

## What problem this app is solving
A delivery platform needs some core backend behavior:
- know which users exist
- know which stores exist
- know which products belong to which store
- let a user add a product to a cart
- return cart details back through an API

This project gives you a small version of that.

## Big picture architecture
At a high level, the app follows this flow:

1. A client sends an HTTP request.
2. A FastAPI controller receives it.
3. The controller calls a service.
4. The service works with in-memory data.
5. The result is returned as JSON.

There is no real database here.
Instead, the app uses seeded sample data loaded at startup.

## Folder structure
Here is the repo structure at a high level:

```text
app.py
README.md
LICENSE.txt
pyproject.toml
poetry.lock
shell.nix
.gitignore
guide.md
repository_explained.md
src/
  joi_delivery/
    __init__.py
    main.py
    router.py
    dependencies.py
    controller/
    service/
    domain/
    generator/
    system/
tests/
  __init__.py
  controller/
```

## Beginner-friendly mental model
If you are new to backend code, think of the repo like this:

- `domain/` = nouns
  - user, cart, store, product
- `service/` = verbs
  - fetch user, fetch product, add to cart
- `controller/` = doors into the system
  - HTTP endpoints
- `generator/` = fake data factory
- `main.py` = startup and wiring
- `tests/` = proof that behavior works

This is a good beginner architecture because responsibilities are separated.

## How a request flows through the app
Let us use `POST /cart/product` as an example.

### Step 1: request enters FastAPI
A client sends JSON like this:

```json
{
  "user_id": "user101",
  "product_id": "product101",
  "outlet_id": "store101"
}
```

### Step 2: controller validates input
`cart_controller.py` uses `AddProductRequest` to validate the body.

If the JSON is missing a required field, FastAPI rejects it.

### Step 3: dependency injection provides the service
FastAPI calls `get_cart_service()` from `dependencies.py`.
That returns the shared cart service from `app.state`.

### Step 4: service performs business logic
`CartService.add_product_to_cart_for_user()`:
- finds the user
- gets the cart
- gets the product
- adds the product to the cart

### Step 5: response is serialized to JSON
The cart and product objects are converted using `to_json()` methods.
Then the API returns the result.

## Main runtime components

### `src/joi_delivery/main.py`
This is the real application entry point.
It does the following:
- creates the FastAPI app
- includes all routers
- loads seed data
- creates service objects
- stores those services on `app.state`
- defines a custom validation error handler

This file is important because it wires the whole app together.

### `src/joi_delivery/router.py`
This file collects routers from different parts of the app and combines them into one main router.

It includes:
- cart routes
- inventory routes
- system routes

Think of this as the central traffic manager for endpoints.

### `src/joi_delivery/dependencies.py`
FastAPI supports dependency injection.
This file provides helper functions that let controllers access app-level services.

For example:
- `get_user_service()`
- `get_product_service()`
- `get_cart_service()`

Why this matters:
- controllers do not create services themselves
- services are shared through the application state
- this keeps the code cleaner and easier to test

## The controller layer
Controllers define API endpoints.
They are the first application code that handles incoming requests.

### `src/joi_delivery/controller/cart_controller.py`
This file has two endpoints:

#### `POST /cart/product`
Purpose:
- add a product to a user's cart

Input:
- `user_id`
- `product_id`
- `outlet_id`

What happens:
- request body is validated using Pydantic
- controller calls `CartService.add_product_to_cart_for_user()`
- response is returned to the client

#### `GET /cart/view?user_id=...`
Purpose:
- fetch the cart for a given user

What happens:
- controller reads `user_id` from query params
- controller calls `CartService.get_cart_for_user()`
- cart object is returned as JSON

### `src/joi_delivery/controller/inventory_controller.py`
This file currently defines:
- `GET /inventory/health?store_id=...`

But right now it is unfinished.
It returns HTTP 200 with no useful JSON body.

This is one of the clearest incomplete parts of the repo.

### `src/joi_delivery/controller/models.py`
This file contains request and response models for controller use.

It has:
- `AddProductRequest`
- `CartProductInfo`

Why this matters:
- request bodies are validated automatically
- response shape becomes more explicit
- the API is easier to understand

### `src/joi_delivery/controller/__init__.py`
This file only contains a short package comment.

Purpose:
- marks `controller` as a Python package
- gives a small description of what the package is for

It has no runtime business logic.

## The service layer
Services contain business logic.
Controllers should stay thin, while services do the actual work.

### `src/joi_delivery/service/cart_service.py`
This is the main service for cart behavior.

It depends on:
- `UserService`
- `ProductService`
- a dictionary of carts keyed by user

Important methods:
- `add_product_to_cart_for_user()`
- `get_cart_for_user()`
- `fetch_cart_for_user()`

What `add_product_to_cart_for_user()` does:
1. find the user
2. find that user's cart
3. find the requested product
4. append the product to the cart's product list
5. return cart + product info

This is the heart of the current business logic.

### `src/joi_delivery/service/product_service.py`
This service stores products and can find a product by:
- product ID
- outlet ID

Main method:
- `get_product(product_id, outlet_id)`

Why both values are used:
- product IDs may need to be matched to a specific store
- this avoids returning a product from the wrong outlet

### `src/joi_delivery/service/user_service.py`
This service is very simple.
It stores a list of users and can find a user by ID.

Main method:
- `fetch_user_by_id(user_id)`

### `src/joi_delivery/service/__init__.py`
This file only contains a short package comment.

Purpose:
- marks `service` as a Python package
- documents that this folder is the service layer

It has no business logic.

## The domain layer
The `domain/` folder contains the core business objects.
These are mostly Python dataclasses.

That means they are plain objects representing things in the business domain.

### `src/joi_delivery/domain/product.py`
Abstract base class for products.
Contains shared product fields:
- `product_id`
- `product_name`
- `mrp`

It also has a small `to_json()` helper for serialization.

### `src/joi_delivery/domain/food_product.py`
This class extends `Product`.
Right now it adds no new fields or behavior.

What that tells you:
- the design probably intended to support restaurant food items in addition to grocery items
- that feature has not been developed yet

### `src/joi_delivery/domain/grocery_product.py`
Represents a grocery item.
Adds fields like:
- `weight`
- `threshold`
- `available_stock`
- `store`
- `selling_price`
- `expiry_date`
- `discount`

This model is important for the inventory use case.
The `threshold` and `available_stock` values are likely meant to support low-stock logic.

### `src/joi_delivery/domain/outlet.py`
Represents a store-like entity.

Fields:
- `name`
- `outlet_id`
- `description`

This is a base class for places that sell products.

### `src/joi_delivery/domain/grocery_store.py`
Extends `Outlet`.
Adds:
- `inventory`

This suggests each store should know which products it has.
But in the current seed setup, that inventory is not really populated in a complete way.

### `src/joi_delivery/domain/restaurant.py`
This class extends `Outlet`.
Right now it adds no new fields or behavior.

What that tells you:
- the design probably planned support for restaurant outlets
- that part is currently only a placeholder

### `src/joi_delivery/domain/user.py`
Represents a user.

Fields include:
- `user_id`
- `first_name`
- `last_name`
- `email`
- `phone_number`
- `cart`
- `username`

### `src/joi_delivery/domain/cart.py`
Represents a shopping cart.

Fields:
- `cart_id`
- `outlet`
- `products`
- `user`

This object is returned by the cart API.

### `src/joi_delivery/domain/__init__.py`
This file re-exports the main domain models.

Why that exists:
- other code can import from `joi_delivery.domain` more easily
- `__all__` makes the intended public exports explicit

It is a convenience file, not business logic.

## Seed data and initialization

### `src/joi_delivery/generator/app_initializer.py`
This file creates fake in-memory data when the app starts.

It creates:
- stores
- users
- carts
- grocery products

Current seeded data includes:
- store `store101` = Fresh Picks
- store `store102` = Natural Choice
- user `user101` = John Doe
- products `product101`, `product102`, `product103`

Why this file matters:
- it replaces a real database
- it gives the app something to work with immediately
- it is the source of truth for demo and test data

Important limitation:
- data only exists in memory
- if the app restarts, everything resets

Also note:
- it creates product objects that point to stores
- but it does not fully build out store inventory behavior in a way the inventory endpoint currently uses

### `src/joi_delivery/generator/__init__.py`
This file only contains a short package comment.

Purpose:
- marks `generator` as a Python package
- documents that the folder contains generator utilities

## System routes

### `src/joi_delivery/system/routes.py`
This file contains basic utility endpoints.

#### `GET /health`
Returns a simple health response.
Used to confirm the app is running.

#### `GET /`
Returns:
- welcome message
- app description
- version
- a list of endpoints

This is useful for beginners because it shows what the app exposes.

### `src/joi_delivery/system/__init__.py`
This file only contains a short package comment.

Purpose:
- marks `system` as a Python package
- labels the folder as system routes/utilities

## Package root files

### `src/joi_delivery/__init__.py`
This file is only a short package description.

Purpose:
- marks `joi_delivery` as a Python package
- gives a one-line explanation of the package

It contains no logic.

## Tests
The tests are in `tests/controller/`.

### `tests/controller/test_cart_controller.py`
This file tests the cart endpoints.

It uses:
- `pytest`
- `TestClient` from FastAPI
- `unittest.mock.patch`

Why patching is used:
- the test wants to isolate the controller behavior
- instead of running real service logic, it mocks service methods

What it tests:
- adding a product returns HTTP 200
- viewing a cart returns HTTP 200 and expected fields

### `tests/controller/test_inventory_controller.py`
This file exists, but it is incomplete.
It only checks that the inventory endpoint returns 200.

This matches the codebase state: inventory support is not finished yet.

### `tests/__init__.py`
This file only contains a short package comment.

Purpose:
- marks `tests` as a Python package
- provides a simple package label

### `tests/controller/__init__.py`
This file only contains a short package comment.

Purpose:
- marks the controller test folder as a Python package
- documents that this folder contains controller tests

## Root-level scripts and support files

### `app.py`
This is a small startup script.
It imports the FastAPI app and runs it with Uvicorn.

Why it exists when `main.py` already exists:
- it gives a short script at the repo root
- some developers prefer running a top-level file directly

### `README.md`
This is the project introduction.
It explains:
- what JOI Delivery is
- the sample business story
- setup steps
- how to run the app
- example API requests

This is the first file a new developer should read.

### `guide.md`
This is the interview-prep guide created for this repo.
It explains how to approach likely interview tasks such as:
- fixing inventory
- building two agents

This is a support document, not part of the app itself.

### `repository_explained.md`
This file is the beginner-friendly documentation you are reading now.
Its job is to explain the repo structure and behavior in plain language.

### `pyproject.toml`
This is the main project configuration file.
It defines:
- package name
- Python version
- dependencies
- dev dependencies
- linting configuration
- Poetry script entrypoint

Important dependencies in this project:
- `fastapi` for the web API
- `uvicorn` for running the server
- `httpx` for HTTP-related support
- `pytest` for tests
- `pytest-cov` for coverage
- `ruff` for linting
- `loguru` for logging

### `poetry.lock`
This file locks exact dependency versions.

Why it matters:
- two developers can install the same dependency versions
- builds become more reproducible

Usually you do not edit this by hand.
Poetry updates it automatically when dependencies change.

### `shell.nix`
This file helps developers who use Nix.
It creates a development shell with tools like:
- `git`
- `jujutsu`
- `pre-commit`
- `poetry`

It also tries to:
- create a local virtual environment if needed
- install dependencies
- activate the virtual environment

Beginner translation:
- this file helps standardize the development environment on machines that use Nix

### `.gitignore`
This file tells Git which files not to track.

Examples of ignored files:
- Python cache files
- virtual environments
- test coverage outputs
- IDE folders
- operating system junk files

Why it matters:
- keeps the repository clean
- avoids committing machine-specific or generated files

### `LICENSE.txt`
This file contains the project license.

Why it matters:
- it defines the legal usage terms for the code
- in interview or learning contexts, it is usually informational unless you plan to distribute the code

## Why there are `to_json()` methods
The domain classes are dataclasses, not Pydantic models.
So the code uses `to_json()` methods to manually convert objects to dictionaries.

This works, but it is a basic approach.
In a larger FastAPI project, you might instead use Pydantic response models more consistently.

## What is good about this repo
- small and easy to read
- clear FastAPI structure
- simple dependency injection pattern
- domain objects are understandable
- seeded data makes local development easy
- enough code to practice API work without too much complexity

## What is incomplete or weak
This repo is useful, but not complete.
Here are the main gaps.

### 1. Inventory endpoint is unfinished
`src/joi_delivery/controller/inventory_controller.py` returns only a status code.
There is no real inventory health logic yet.

### 2. No database
All data is in memory.
That is fine for a coding exercise, but not enough for a real application.

### 3. Error handling is minimal
For example:
- what if the user does not exist?
- what if the cart does not exist?
- what if the product is not found?

Some service methods return `None`, but the controller logic does not robustly handle every case.

### 4. Response models are mixed
Some parts use Pydantic models, but domain objects are also returned directly.
This works in small demos, but it can become messy in larger systems.

### 5. Placeholder domain types exist but are unused
`FoodProduct` and `Restaurant` exist, but they currently do nothing.
That suggests future expansion, not current functionality.

### 6. Business logic is very simple
There is no support for:
- quantities
- checkout
- order history
- pricing rules
- delivery tracking
- authentication

## If you want to improve this project
A good improvement order would be:

1. finish the inventory endpoint
2. add proper 404 handling for missing users, carts, stores, and products
3. add response models for inventory
4. add more tests for failure paths
5. move from in-memory seed data to a database
6. add authentication
7. add AI agent endpoints only after the core API is stable

## If you are using this repo for an interview
The strongest areas to understand are:
- how `main.py` wires services
- how controllers use dependencies
- how `CartService` performs core logic
- why the inventory endpoint is clearly incomplete
- how to add tests before changing behavior
- which files are placeholders versus real runtime code

## Quick summary
This repository is a small FastAPI backend for a grocery delivery app.
It already supports:
- viewing cart data
- adding products to a cart
- basic system endpoints

It uses:
- seed data instead of a database
- services for business logic
- controllers for HTTP APIs
- dataclasses for domain models

The biggest unfinished area is inventory.
That is why it is a good candidate for an interview exercise or extension task.
