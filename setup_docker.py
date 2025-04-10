#!/usr/bin/env python3
"""
Set up Docker environment for CTCAE standardizer.
"""
import os
import sys
import subprocess
from pathlib import Path


def check_docker_installed():
    """Check if Docker is installed."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def setup_env_file():
    """Set up .env file if it doesn't exist."""
    env_path = Path(".env")
    example_path = Path(".env.example")

    if env_path.exists():
        print("✓ Found existing .env file")
        return True

    if example_path.exists():
        # Create from example
        with open(example_path, 'r') as f:
            content = f.read()

        # Get API key
        openai_key = input("Enter your OpenAI API key: ")
        content = content.replace("your_openai_api_key_here", openai_key)

        # Write to .env file
        with open(env_path, 'w') as f:
            f.write(content)

        print("✓ Created .env file from template")
        return True
    else:
        # Create minimal file
        openai_key = input("Enter your OpenAI API key: ")

        with open(env_path, 'w') as f:
            f.write(f"OPENAI_API_KEY={openai_key}\n")
            f.write("IRIS_HOSTNAME=iris\n")  # Container name
            f.write("IRIS_PORT=1972\n")  # Internal port
            f.write("IRIS_NAMESPACE=USER\n")
            f.write("IRIS_USERNAME=_SYSTEM\n")
            f.write("IRIS_PASSWORD=SYS\n")

        print("✓ Created minimal .env file")
        return True


def run_docker_compose():
    """Build and start all Docker containers."""
    print("Building and starting Docker containers...")
    try:
        subprocess.run(["docker", "compose", "build"], check=True)
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error with Docker Compose: {e}")
        return False


def run_in_docker(command):
    """Run a command in the Docker app container."""
    try:
        result = subprocess.run(
            ["docker", "compose", "exec", "app"] + command,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running command in Docker: {e}")
        return False


def main():
    print("Setting up Docker environment for CTCAE standardizer...")

    # Check if Docker is installed
    if not check_docker_installed():
        print("✗ Docker is not installed or not in PATH.")
        print("Please install Docker and try again.")
        return 1

    # Set up .env file
    if not setup_env_file():
        print("✗ Failed to create .env file.")
        return 1

    # Build and start Docker containers
    if not run_docker_compose():
        print("✗ Failed to start Docker containers.")
        return 1

    print("✓ Docker containers started successfully!")

    # Run setup steps in containers
    print("\nSetting up CTCAE data in Docker...")
    run_in_docker(["python", "scripts/download_ctcae.py"])
    run_in_docker(["python", "scripts/process_ctcae.py"])
    run_in_docker(["python", "scripts/create_vector_store.py"])

    print("\n✓ Docker setup complete!")
    print("\nAvailable services:")
    print("- API: http://localhost:8000")
    print("- Jupyter Notebook: http://localhost:8888")
    print("- IRIS Management Portal: http://localhost:5274/csp/sys/UtilHome.csp")

    print("\nUseful commands:")
    print("- View logs: docker compose logs -f")
    print("- Stop containers: docker compose down")
    print("- Restart containers: docker compose restart")

    return 0


if __name__ == "__main__":
    sys.exit(main())