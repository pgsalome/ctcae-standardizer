#!/usr/bin/env python3
"""
Set up Docker environment for the CTCAE standardizer.
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


def check_env_file():
    """Check if .env file exists and create it if not."""
    env_path = Path(".env")

    if env_path.exists():
        print("Found existing .env file")
        return True

    # Create .env file from example
    example_path = Path(".env.example")
    if example_path.exists():
        with open(example_path, 'r') as f:
            example_content = f.read()

        # Get OpenAI API key
        openai_key = input("Enter your OpenAI API key: ")

        # Replace placeholder in content
        content = example_content.replace("your_openai_api_key_here", openai_key)

        # Write to .env file
        with open(env_path, 'w') as f:
            f.write(content)

        print("Created .env file with your API key")
        return True
    else:
        # Create minimal .env file
        openai_key = input("Enter your OpenAI API key: ")

        with open(env_path, 'w') as f:
            f.write(f"OPENAI_API_KEY={openai_key}\n")
            f.write("IRIS_HOSTNAME=iris\n")
            f.write("IRIS_PORT=1972\n")
            f.write("IRIS_NAMESPACE=USER\n")
            f.write("IRIS_USERNAME=_SYSTEM\n")
            f.write("IRIS_PASSWORD=SYS\n")

        print("Created minimal .env file")
        return True


def run_docker_compose():
    """Run docker-compose commands to set up the Docker containers."""
    print("Starting Docker containers...")
    try:
        subprocess.run(["docker", "compose", "build"], check=True)
        subprocess.run(["docker", "compose", "up", "-d"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Docker Compose: {e}")
        return False


def download_ctcae_data():
    """Run the download_ctcae.py script in the Docker container."""
    print("Downloading CTCAE data...")
    try:
        subprocess.run(
            ["docker", "compose", "exec", "app", "python", "scripts/download_ctcae.py"],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading CTCAE data: {e}")
        return False


def process_ctcae_data():
    """Run the process_ctcae.py script in the Docker container."""
    print("Processing CTCAE data...")
    try:
        subprocess.run(
            ["docker", "compose", "exec", "app", "python", "scripts/process_ctcae.py"],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error processing CTCAE data: {e}")
        return False


def create_vector_store():
    """Run the create_vector_store.py script in the Docker container."""
    print("Creating vector store...")
    try:
        subprocess.run(
            ["docker", "compose", "exec", "app", "python", "scripts/create_vector_store.py"],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating vector store: {e}")
        return False


def main():
    print("Setting up CTCAE Standardizer Docker environment...")

    # Check if Docker is installed
    if not check_docker_installed():
        print("Error: Docker is not installed or not in PATH")
        print("Please install Docker and try again")
        return 1

    # Check .env file
    if not check_env_file():
        print("Error: Failed to create .env file")
        return 1

    # Run Docker Compose
    if not run_docker_compose():
        print("Error: Failed to start Docker containers")
        return 1

    print("Docker containers started successfully!")

    # Download CTCAE data
    if not download_ctcae_data():
        print("Warning: Failed to download CTCAE data")
        print("You can manually run: docker compose exec app python scripts/download_ctcae.py")

    # Process CTCAE data
    if not process_ctcae_data():
        print("Warning: Failed to process CTCAE data")
        print("You can manually run: docker compose exec app python scripts/process_ctcae.py")

    # Create vector store
    if not create_vector_store():
        print("Warning: Failed to create vector store")
        print("You can manually run: docker compose exec app python scripts/create_vector_store.py")

    print("\nSetup complete!")
    print("\nServices:")
    print("- API: http://localhost:8000")
    print("- Jupyter Notebook: http://localhost:8888")
    print("- IRIS Management Portal: http://localhost:5274/csp/sys/UtilHome.csp")
    print("\nTry the symptom matcher:")
    print(
        'curl -X POST "http://localhost:8000/match" -H "Content-Type: application/json" -d \'{"symptom": "severe headache with nausea", "details": "occurs daily, pain level 8/10"}\'')

    return 0


if __name__ == "__main__":
    sys.exit(main())