# Fast Boiler 🚀

**Generate FastAPI projects with a modern, scalable architecture in seconds.**

[![PyPI version](https://badge.fury.io/py/fast-boiler.svg)](https://pypi.org/project/fast-boiler/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
    
---

`fast-boiler` is a command-line tool that scaffolds a complete FastAPI application using the robust **Repository → Service → Controller** layering pattern. Stop writing boilerplate and start building features.

### Why Use Fast Boiler?

-   **Scalable by Default**: The generated structure cleanly separates database logic (Repositories), business logic (Services), and API endpoints (Controllers), making your project easy to maintain and grow.
-   **Best Practices Included**: Uses the latest, non-deprecated syntax for FastAPI, Pydantic V2, and SQLAlchemy 2.0.
-   **Blazing Fast Workflow**: Initialize a full project with one command and generate all the files for new resources (models, schemas, repos, services, controllers) with another.
-   **Asynchronous Ready**: Although the default is synchronous for simplicity, the structure is perfectly suited for easy conversion to async.

---

##  Prerequisites

Before you begin, you need to have **Python 3.8+** and **`pipx`** installed on your system.

`pipx` is a tool to install and run Python applications in isolated environments. It's the recommended way to install command-line tools like this one. If you don't have it, you can install it with:

```bash
pip install pipx
pipx ensurepath
```

*(You may need to restart your terminal after running `pipx ensurepath`.)*

---

## 📦 Installation

Installing `fast-boiler` is a one-line command:

```bash
pipx install fast-boiler
```

To verify the installation, run:

```bash
fast-boiler --help```

---

## 🚀 Quickstart: Create Your First Project

Let's build a new API in under a minute.

### 1. Initialize a New Project

This command creates a new directory with a complete FastAPI project structure, including a default `user` resource.

```bash
fast-boiler init myapi
```

This will create the following structure:
```
myapi/
├── .gitignore
├── requirements.txt
└── app/
    ├── database.py
    ├── main.py
    ├── controllers/
    │   └── user_controller.py
    ├── models/
    │   └── user_model.py
    # ... and so on
```

### 2. Run the API Server

Navigate into your new project, install its dependencies, and run the server.

```bash
# Navigate into the project
cd myapi

# (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dev server
uvicorn app.main:app --reload```

Your API is now live! Open your browser to **`http://127.0.0.1:8000/docs`** to see the interactive Swagger UI for the `/users` endpoint.

### 3. Generate a New Resource

Now for the fun part. Let's add endpoints for managing `products`.

Open a **new terminal**, navigate to your project's root directory (`myapi`), and run the `generate` command.

```bash
cd /path/to/myapi
fast-boiler generate product
```

This command automatically creates:
- `app/models/product_model.py`
- `app/schemas/product_schema.py`
- `app/repositories/product_repo.py`
- `app/services/product_service.py`
- `app/controllers/product_controller.py`

### 4. Activate the New Resource

The final step is to tell your main application about the new controller. Open `myapi/app/main.py` and include the new router:

```python
# In myapi/app/main.py

from fastapi import FastAPI
from app.database import Base, engine
# 👇 1. IMPORT THE NEW CONTROLLER
from app.controllers import user_controller, product_controller

Base.metadata.create_all(bind=engine)

app = FastAPI(...)

app.include_router(user_controller.router)
# 👇 2. INCLUDE THE NEW ROUTER
app.include_router(product_controller.router)

# ... rest of the file
```
When you save the file, the `uvicorn` server will automatically reload. Refresh your browser, and you'll see the new `/products` endpoints in the API documentation.

---

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.