<div align="center">

# ⚓ Anchor

**Simplify Python Project Dockerization**

[![GitHub license](https://img.shields.io/github/license/jesperfjellin/anchor.svg)](https://github.com/jesperfjellin/anchor/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/jesperfjellin/anchor.svg)](https://github.com/jesperfjellin/anchor/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/jesperfjellin/anchor.svg)](https://github.com/jesperfjellin/anchor/issues)
[![GitHub release](https://img.shields.io/github/release/jesperfjellin/anchor.svg)](https://github.com/jesperfjellin/anchor/releases)

</div>

## 🚀 Introduction

Anchor is a powerful command-line tool designed to streamline the process of setting up Python projects for Docker. It automates several crucial steps in the Dockerization process, making it easier for developers to containerize their Python applications.

## ✨ Features

- 🔍 Scans your code for external file paths
- 📄 Generates `requirements.txt` from your virtual environment
- 🐳 Creates a Dockerfile tailored to your project
- 🏗️ Builds the Docker image
- 🚀 Provides a suggested `docker run` command with appropriate volume mounts

## 🎥 Demo

![Demo](images/demo.png)

## 🛠️ Installation

```bash
pip install anchor-terminal
```

## 🏳️ Flags

Flag                | Description                                               | Required | Default                       |
|---------------------|-----------------------------------------------------------|----------|-------------------------------|
| `--image`           | **Docker Image Name.** Specifies the name for the image.  | Yes      | N/A                           |
| `--container`       | **Docker Container Name.** Sets a custom container name.  | No       | Automatically assigned        |
| `--ports`           | **Port Mappings.** Maps host ports to container ports.          | No       | No ports mapped               |
| `--python`          | **Python Version.** Chooses the Python version (e.g., 3.13). | No    | `3.13`                        |
| `--debug`           | **Enable Debug Logging.** Activates detailed logs.        | No       | `False`                       |

