import argparse
import subprocess
import os
import ast
import re

def check_docker_installation():
    try:
        subprocess.run(['docker', '-v'], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        print("Error: Docker is not installed. Please install Docker to use this tool.")
        return False

def get_python_version(requested_version):
    """Map user's Python version request to a full version string."""
    version_map = {
        "3.14": "3.14.0a3-slim-bullseye",
        "3.13": "3.13.1-slim-bookworm",
        "3.12": "3.12.8-slim-bookworm",
        "3.11": "3.11.11-slim-bookworm",
        "3.10": "3.10.16-slim-bookworm",
        "3.9": "3.9.21-slim-bookworm"
    }
    
    # If exact version is provided, use it
    for full_version in version_map.values():
        if requested_version == full_version:
            return requested_version
    
    # If major.minor is provided (e.g., "3.12"), use mapped version
    if requested_version in version_map:
        return version_map[requested_version]
    
    # Default to 3.13 if version not found
    print(f"Warning: Python version '{requested_version}' not found. Using 3.13.1-slim-bookworm")
    return version_map["3.13"]

def generate_python_dockerfile(entrypoint_script, requirements_file, directory, python_version="3.13"):
    # Get the full version string
    full_version = get_python_version(python_version)
    
    dockerfile_content = f"""
FROM python:{full_version}

WORKDIR /app
{f'COPY {requirements_file} ./' if requirements_file else ''}
{f'RUN pip install --no-cache-dir -r {requirements_file}' if requirements_file else ''}
COPY . .
CMD ["python", "{entrypoint_script}"]
"""
    dockerfile_path = os.path.join(directory, 'Dockerfile')
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)
    return dockerfile_path

def detect_project_type(directory):
    requirements_file = None
    entrypoint_script = None
    python_scripts = []
    for file in os.listdir(directory):
        if file == "requirements.txt":
            requirements_file = file
        elif file.endswith(".py"):
            python_scripts.append(file)
    if python_scripts:
        if len(python_scripts) == 1:
            entrypoint_script = python_scripts[0]
        else:
            entrypoint_script = input(f"Multiple python files detected: {', '.join(python_scripts)}. Please specify which file should be run in CMD: ")
            if entrypoint_script not in python_scripts:
                print("Invalid entrypoint script specified. Please try again.")
                return None, None
        return requirements_file, entrypoint_script
    return None, None

def is_plausible_path(p: str) -> bool:
    # Strict patterns
    windows_drive_path = re.compile(r'^[A-Za-z]:[\\/].+')
    windows_unc_path = re.compile(r'^\\\\[^\\]+\\.+')
    unix_abs_path = re.compile(r'^/[^/].+')

    # Check if it matches one of these patterns
    if windows_drive_path.match(p):
        return True
    if windows_unc_path.match(p):
        return True
    if unix_abs_path.match(p):
        return True
    return False

def find_file_strings(directory, python_files):
    potential_files = set()

    for file in python_files:
        file_path = os.path.join(directory, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
            tree = ast.parse(source, filename=file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    string_value = node.value.strip()

                    # Check if this string seems like a plausible file path
                    if is_plausible_path(string_value):
                        print(f"Found potential external path at line {node.lineno}: {string_value}")
                        normalized_path = os.path.normpath(string_value)
                        parent_dir = os.path.dirname(os.path.abspath(normalized_path))
                        potential_files.add(parent_dir)

    if not potential_files:
        print("No potential external file paths found.")
        return None

    try:
        if len(potential_files) == 1:
            return potential_files.pop()
        common_dir = os.path.commonpath(list(potential_files))
        if common_dir and len(common_dir) > 1:
            print(f"Common directory found: {common_dir}")
            return common_dir
        return None
    except ValueError:
        # This happens if paths are on different drives or invalid
        print("Paths are on different drives or invalid. Cannot find a common directory.")
        return None

def build_docker_image(image_name, directory):
    try:
        subprocess.run(['docker', 'build', '-t', image_name, '.'], check=True, cwd=directory)
        print(f"Successfully built Docker image: {image_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building image: {e}")
        return False

def create_docker_container(container_name, image_name, ports, directory):
    try:
        port_mapping = " ".join([f"-p {port}" for port in ports])
        command = ['docker', 'create', '--name', container_name, ]
        if port_mapping:
          command.extend(port_mapping.split())
        command.extend([image_name])
        subprocess.run(command, check=True, cwd=directory)
        print(f"Successfully created Docker container: {container_name} from {image_name}")
        return True
    except subprocess.CalledProcessError as e:
         print(f"Error creating container: {e}")
         return False

def detect_venv(directory):
    # Check if either venv or .venv directories exist
    possible_venvs = [os.path.join(directory, 'venv'), os.path.join(directory, '.venv')]
    for v in possible_venvs:
        if os.path.isdir(v):
            return v
    return None

def run_pip_freeze(venv_path, directory):
    # Assume Windows for simplicity, adjust paths as needed for other OS.
    if os.name == 'nt':
        pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
    else:
        pip_path = os.path.join(venv_path, 'bin', 'pip')

    if not os.path.exists(pip_path):
        print("Could not locate pip in the virtual environment. Please ensure the venv is correctly set up.")
        return False

    requirements_file = os.path.join(directory, 'requirements.txt')
    with open(requirements_file, 'w', encoding='utf-8') as rf:
        proc = subprocess.run([pip_path, 'freeze'], stdout=rf)
    return proc.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="A simple Docker workflow tool.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # 'create' command
    create_parser = subparsers.add_parser('create', help='Create Docker image and container')
    create_parser.add_argument("--image", help="Docker image name", required=True)
    create_parser.add_argument("--container", help="Docker container name")
    create_parser.add_argument("-p", "--ports", help="Port mappings (e.g., 8080:80, 5432:5432). Can be multiple ports separated by spaces.", nargs='+', default=[])
    create_parser.add_argument("--python", help="Python version to use (e.g., 3.12, 3.13)", default="3.13")

    args = parser.parse_args()

    if not check_docker_installation():
        return

    directory = os.getcwd()
    dockerfile_path = os.path.join(directory, 'Dockerfile')
    python_files = [file for file in os.listdir(directory) if file.endswith(".py")]

    if args.command == 'create':
        common_dir = find_file_strings(directory, python_files)
        
        # If requirements.txt doesn't exist, try to generate from a virtual environment
        if not os.path.exists(os.path.join(directory, 'requirements.txt')):
            venv_path = detect_venv(directory)
            if venv_path:
                if run_pip_freeze(venv_path, directory):
                    print("requirements.txt generated using pip freeze.")
                else:
                    print("Failed to generate requirements.txt with pip freeze. Please create it manually.")
            else:
                print("Cannot find virtual environment to generate requirements.txt. Please add requirements manually.")

        requirements_file, entrypoint_script = detect_project_type(directory)

        if entrypoint_script:
            if os.path.exists(dockerfile_path):
                os.remove(dockerfile_path)

            dockerfile_path = generate_python_dockerfile(
                entrypoint_script, 
                requirements_file, 
                directory,
                args.python
            )
            print(f"Dockerfile generated at {dockerfile_path}")
        else:
            print("Could not detect project type, no Dockerfile created.")
            return

        if build_docker_image(args.image, directory) == False:
            return

        if args.container:
            if create_docker_container(args.container, args.image, args.ports, directory) == False:
                return

        # Print volume mounting suggestion after successful container creation
        if common_dir:
            print(f"\nDocker run suggestion:")
            print(f"docker run --rm -v {common_dir}:/data {args.image}")

if __name__ == "__main__":
    main()
