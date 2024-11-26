This project is a Flask-based web application designed to demonstrate a Docker-in-Docker (DinD) setup. It enables deployment and management of insecure apps within nested Docker containers for testing and experimentation purposes. Here's a concise breakdown:
Purpose:

    Showcase a DinD architecture: running Docker containers inside an outer Docker container.
    Provide a system to deploy potentially insecure apps in isolated environments safely.
    Manage containers (list, stop, delete) via a simple web interface.

Key Features:

    Outer and Inner Docker Containers:
        The outer container is a privileged Docker container running Docker itself (Docker-in-Docker).
        The inner container hosts the insecure app and is managed by the outer container.

    Deployment Process:
        Accepts a username/repo from the user.
        Creates an outer container (DinD setup) and maps its port 80 to the host system.
        Installs Docker inside the outer container to allow further containerization.
        Launches an inner container to deploy the specified app.

    Container Management:
        List Containers: Displays running containers (outer and inner) with their details.
        Stop Containers: Terminates a specified container.
        Delete Containers: Permanently removes a specified container.

    Flask API Endpoints:
        /: Renders an HTML homepage.
        /deploy (POST): Deploys a specified app in a nested container.
        /load_containers (GET): Lists all running containers (inner and outer).
        /stop_container (POST): Stops a specified container.
        /delete_container (POST): Deletes a specified container.

Technologies:

    Flask: Web framework for routing and managing APIs.
    Docker: For containerization and nested container orchestration.
    Subprocess Module: Executes Docker CLI commands for container operations.

Security Note:

This project is inherently insecure and should only be used in controlled environments. Running Docker containers in privileged mode and deploying untrusted apps pose risks. Use for testing purposes only.
