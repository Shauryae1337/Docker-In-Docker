from setuptools import setup, find_packages
import sys

def check_docker():
    """Check if Docker is installed on the system."""
    try:
        import subprocess
        subprocess.run(['docker', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False

# Check if Docker is installed (for user convenience)
if not check_docker():
    print("WARNING: Docker is not installed. Please install Docker before running this application.")
    if sys.platform.startswith('linux'):
        print("For Linux, you can install Docker using: sudo apt-get install docker.io")
    elif sys.platform == "darwin":
        print("For macOS, you can install Docker via Homebrew: brew install --cask docker")
    elif sys.platform == "win32":
        print("For Windows, download Docker Desktop from https://www.docker.com/products/docker-desktop")
    sys.exit(1)

setup(
    name='flask-docker-app',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'Flask>=2.0.0',             # Flask framework
        'flask-cors>=3.1.0',        # Flask CORS support
        'docker>=6.0.0',            # Python Docker SDK for Docker interactions
        'requests>=2.25.0',         # Requests for HTTP calls (if needed for external services)
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',          # Testing framework
            'black>=22.0',          # Code formatting tool
            'flake8>=3.8',          # Linter for code quality
        ]
    },
    entry_points={
        'console_scripts': [
            'flask-docker-app = app:main',  # Assuming the main app entry is in 'app.py'
        ],
    },
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
)

