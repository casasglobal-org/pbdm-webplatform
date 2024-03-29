# Project Setup Instructions

## Prerequisites

Before you begin, ensure you have the following software installed on your system:

- **Docker**: Docker is required for creating and managing your application containers. You can find the installation instructions for Docker at [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/).
- **Docker Compose**: Docker Compose is necessary for running multi-container Docker applications. Installation instructions are available at [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/).

## Configuration

1. Inside the `env.config` file, define the values for the inserted environment variables. Set the volume's value relative to the directory that needs to contain:
   - TXT files inside the `txtfiles/` folder.
   - The `punti.dat` file, containing a list of points.

## Running the Application

Once the prerequisites are installed and the environment variables are configured, launch the application by executing the following command in your terminal:

```bash
sudo sh run.sh
