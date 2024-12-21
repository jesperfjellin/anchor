# ⚓ Anchor

Anchor is a small command-line tool that helps simplify the setup of a Python project for Docker. It scans your code for external file paths, generates a requirements.txt from your virtual environment, creates a Dockerfile, and then builds the Docker image. Finally, it provides a suggested docker run command with a suitable volume mount. It doesn’t run containers itself—only builds them to get you closer to a working Dockerized environment.

## Usage

![Demo](images/demo.png)

