from flask import Flask, request, jsonify, render_template
import subprocess
import socket
import uuid
import time
from datetime import timedelta

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set timeout for requests (in seconds)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(minutes=5)  # 5 minutes
app.config['TIMEOUT'] = 600  # Custom timeout


# Get the hostname to identify the internal host machine
host_name = socket.gethostname()

# Docker image to be used for the outer container
DOCKER_IMAGE = "docker:latest"  # Use appropriate Docker image for Docker-in-Docker

@app.route('/')
def index():
    # Render the HTML template from the 'templates' folder
    return render_template('index.html')

@app.route('/deploy', methods=['POST'])
def deploy():
    data = request.json
    username_repo = data.get('username_repo')

    if not username_repo:
        return jsonify({"error": "username/repo is required"}), 400

    # Create the outer Docker container with Docker-in-Docker and expose port 80
    outer_container_id = create_outer_container()
    if not outer_container_id:
        return jsonify({"error": "Failed to create outer container"}), 500

    # Create the inner Docker container and deploy the repo
    inner_container_id = deploy_repo(outer_container_id, username_repo)
    if not inner_container_id:
        return jsonify({"error": "Failed to deploy repository"}), 500

    # Construct the URL for accessing the application
    url = f"http://localhost:80"  # Expose port 80 on the outer container
    return jsonify({"url": url}), 200

def create_outer_container():
    """Creates the outer Docker container with Docker-in-Docker enabled and a unique name"""
    try:
        container_name = f"docker_outer_{str(uuid.uuid4())}"  # Unique name with UUID
        result = subprocess.run(
            ["docker", "run", "-d", "--privileged", "--name", container_name, "-p", "80:80", DOCKER_IMAGE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode('utf-8').strip()  # Return the container ID
    except subprocess.CalledProcessError as e:
        print(f"Error creating outer container: {e.stderr.decode('utf-8')}")
        return None

def deploy_repo(outer_container_id, username_repo):
    """Deploys the repository inside the inner container running inside the outer container"""
    try:
        # Install Docker inside the outer container (DIND setup)
        subprocess.run(
            ["docker", "exec", outer_container_id, "apk", "add", "--no-cache", "docker"],
            check=True
        )

        # Run the inner container and deploy the repo, mapping inner 5000 to outer 80
        inner_container_name = f"docker_inner_{str(uuid.uuid4())}"  # Unique name for inner container
        inner_container_id = subprocess.run(
            ["docker", "exec", outer_container_id, "docker", "run", "-d", "-p", "80:5000", "--name", inner_container_name, username_repo],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return inner_container_id.stdout.decode('utf-8').strip()  # Return the inner container ID
    except subprocess.CalledProcessError as e:
        print(f"Error deploying repo: {e.stderr.decode('utf-8')}")
        return None

@app.route('/load_containers', methods=['GET'])
def load_containers():
    try:
        # Run 'docker ps' to list running containers (both internal and external)
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.ID}} {{.Image}} {{.Status}} {{.Names}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        containers = []
        for line in result.stdout.decode('utf-8').splitlines():
            container_id, image, status, name = line.split(" ", 3)
            
            # Determine if the container is internal or external based on image/repository
            container_type = "External" if image != "internal-image" else "Internal"  # Example check for internal
            
            containers.append({
                "id": container_id,
                "repo": image,  # Assuming image name as the repo
                "status": status,
                "name": name,
                "type": container_type
            })

        return jsonify({"containers": containers})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to load containers", "message": e.stderr.decode('utf-8')}), 500

@app.route('/stop_container', methods=['POST'])
def stop_container():
    data = request.json
    container_id = data.get('container_id')

    if not container_id:
        return jsonify({"error": "container_id is required"}), 400

    try:
        # Run 'docker kill' to stop the container
        subprocess.run(["docker", "kill", container_id], check=True)
        return jsonify({"message": f"Container {container_id} stopped successfully."}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to stop container", "message": e.stderr.decode('utf-8')}), 500

@app.route('/delete_container', methods=['POST'])
def delete_container():
    data = request.json
    container_id = data.get('container_id')

    if not container_id:
        return jsonify({"error": "container_id is required"}), 400

    try:
        # Run 'docker rm' to delete the container
        subprocess.run(["docker", "rm", container_id], check=True)
        return jsonify({"message": f"Container {container_id} deleted successfully."}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to delete container", "message": e.stderr.decode('utf-8')}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)

