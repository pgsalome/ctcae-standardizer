#!/usr/bin/env python3
"""
Set up local development environment for CTCAE standardizer.
"""
import os
import sys
import subprocess
import platform
from pathlib import Path


def setup_venv():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("venv")

    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True

    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating virtual environment: {e}")
        return False


def install_requirements():
    """Install requirements into the virtual environment."""
    # Determine pip command based on platform
    if platform.system() == "Windows":
        pip_cmd = os.path.join("venv", "Scripts", "pip")
    else:
        pip_cmd = os.path.join("venv", "bin", "pip")

    print("Installing dependencies...")
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
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
            f.write("IRIS_HOSTNAME=localhost\n")
            f.write("IRIS_PORT=1973\n")  # Mapped port in docker-compose
            f.write("IRIS_NAMESPACE=USER\n")
            f.write("IRIS_USERNAME=_SYSTEM\n")
            f.write("IRIS_PASSWORD=SYS\n")

        print("✓ Created minimal .env file")
        return True


def start_iris_docker():
    """Start only the IRIS container for local development."""
    print("Starting IRIS Docker container...")
    try:
        # Check if Docker is installed
        subprocess.run(["docker", "--version"], check=True, capture_output=True)

        # Start IRIS container
        subprocess.run(["docker", "compose", "up", "-d", "iris"], check=True)
        print("✓ IRIS container started successfully")
        return True
    except FileNotFoundError:
        print("✗ Docker not found. Please install Docker to run IRIS.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"✗ Error starting IRIS container: {e}")
        return False


def main():
    print("Setting up local development environment for CTCAE standardizer...")

    # Step 1: Set up virtual environment
    if not setup_venv():
        return 1

    # Step 2: Install requirements
    if not install_requirements():
        return 1

    # Step 3: Set up .env file
    if not setup_env_file():
        return 1

    # Step 4: Start IRIS Docker container
    if not start_iris_docker():
        print("Warning: IRIS container could not be started.")
        print("You can start it manually with: docker compose up -d iris")

    # Show activation instructions
    print("\n✓ Local development environment setup complete!")
    if platform.system() == "Windows":
        print("\nTo activate the virtual environment, run:")
        print("  venv\\Scripts\\activate")
    else:
        print("\nTo activate the virtual environment, run:")
        print("  source venv/bin/activate")

    print("\nNext steps:")
    print("1. Activate the virtual environment")
    print("2. Run: python scripts/download_ctcae.py")
    print("3. Run: python scripts/process_ctcae.py")
    print("4. Run: python scripts/create_vector_store.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())