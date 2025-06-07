# AI Agent Development Framework

This project provides a containerized development environment for building and testing AI agents. It uses Docker to ensure a consistent and reproducible setup, and comes pre-configured with support for various LLM backends like LM Studio, Ollama, and cloud APIs.

## Prerequisites

- Docker & Docker Compose
- Git

## 🚀 Quick Start

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd AgentBuildingFramework
    ```

2.  **Configure your environment:**
    Copy the template and edit the `.env` file to select your LLM provider.
    ```bash
    cp .env.template .env
    nano .env
    ```
    For example, to use a local LM Studio instance, your `.env` should look like this:
    ```dotenv
    LLM_PROVIDER=lm_studio
    LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1
    ```

3.  **Build and run the development container:**
    ```bash
    docker compose up -d
    ```
    This command starts the `adk-dev` service.

4.  **Test the sample agent:**
    Execute the sample agent inside the container to verify your LLM connection.
    ```bash
    docker compose exec adk-dev python src/agents/sample_agent.py
    ```

## Development Workflow

-   **Access the container shell:** `docker compose exec adk-dev bash`
-   **Run your code:** `docker compose exec adk-dev python src/your_script.py`
-   **Run tests:** `docker compose exec adk-dev pytest`
-   **Live Reload:** Your local `./src` directory is mounted into the container. Any changes you make on your host machine are immediately reflected.

## Using Other Services (Profiles)

This project uses Docker Compose profiles to manage optional services like Ollama and a database.

-   **Run with Ollama:**
    ```bash
    docker compose --profile ollama up -d
    ```

-   **Run the complete environment (dev container, Ollama, database):**
    ```bash
    docker compose --profile full-dev up -d
    ```

## Troubleshooting

-   **Container not starting?** Check the logs: `docker compose logs adk-dev`
-   **Need to force a fresh build?** If you change `requirements.txt` or the `Dockerfile`, rebuild with no cache:
    ```bash
    docker compose build --no-cache
    ```
-   **Health check failing?** Run the health check script manually for detailed output:
    ```bash
    docker compose exec adk-dev python health_check.py
    ```

## Project Structure

-   `Dockerfile`: Defines the Python development environment.
-   `docker-compose.yml`: Orchestrates the services (`adk-dev`, `ollama`, `database`).
-   `requirements.txt`: Python dependencies.
-   `health_check.py`: Internal container health validation script.
-   `.env.template`: Template for environment variables.
-   `/src`: Your Python source code.
-   `/logs`, `/data`, `/config`: Mounted directories for persistence.