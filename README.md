# 📄 Doc2Txt: Document Processing Web Application

## 🔍 Overview

Doc2Txt is a web application that allows users to upload documents and extract text content. It leverages two different backend processing engines: Apache Tika for comprehensive document format support and MarkItDown for Markdown file processing. The frontend is built with Reflex, providing a reactive and user-friendly interface.

## ✨ Features

- **📁 Easy Document Upload:** Simple drag-and-drop or file selection for uploading documents.
- **🔄 Versatile Backend Processing:**
  - **🔧 Apache Tika:** Supports a wide range of document formats (PDF, DOC, DOCX, PPT, etc.).
  - **📝 MarkItDown:** Specifically designed for processing Markdown (`.md`) files.
- **📊 Base64 File Handling:** Accepts file content as a base64 encoded string from the frontend.
- **⏱️ Real-time Processing Status:** Provides feedback on the upload and processing status.
- **📋 Extracted Text Output:** Displays the extracted text in a clear and readable format.
- **📋 Copy to Clipboard:** Easily copy the extracted text to your clipboard.
- **🔘 Option to Use MarkItDown:** Users can choose to specifically process their file using the MarkItDown library.
- **💓 Health Check Endpoint:** Backend provides a `/health` endpoint to check the status of the application and its dependencies (Tika).
- **🐳 Dockerized Application:** Both frontend and backend are containerized for easy deployment and setup.

## 🛠️ Technology Stack

- **🖥️ Frontend:** [Reflex](https://reflex.dev/) (Python-based reactive web framework)
- **⚙️ Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python web framework)
- **📑 Document Parsing (General):** [Apache Tika](https://tika.apache.org/)
- **📝 Markdown Parsing:** [MarkItDown](https://github.com/bartdag/markitdown)
- **🔄 Asynchronous HTTP Client:** [httpx](https://www.python-httpx.org/)
- **🐳 Containerization:** [Docker](https://www.docker.com/)
- **📦 Dependency Management:** [UV](https://pypi.org/project/uv/)
- **🔐 Base64 Encoding/Decoding:** Python's built-in `base64` module

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Docker](https://www.docker.com/get-started/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🚀 Getting Started with Docker Compose

This project is set up to run seamlessly using Docker Compose. Follow these steps to get the application up and running:

1. **📥 Clone the Repository:**

   ```bash
   git clone <your_repository_url>
   cd <your_project_directory>
   ```

2. **🏗️ Build and Start the Containers:**
   The provided `docker-compose.yml` file defines the services for the backend and frontend. To build the Docker images and start the containers, run the following command in the root of your project directory:

   ```bash
   docker-compose up -d --build
   ```

   - `docker-compose up`: This command creates and starts the services defined in your `docker-compose.yml` file.
   - `-d`: This flag runs the containers in detached mode (in the background).
   - `--build`: This flag ensures that the Docker images are built (or rebuilt if necessary) before the containers are started.

3. **⏳ Wait for the Services to Start:**
   Docker Compose will pull or build the necessary images and start the containers. You can check the status of the containers using the following command:

   ```bash
   docker-compose ps
   ```

   Make sure both the `backend` and `frontend` services show a status of `Up`. The frontend service depends on the backend being healthy, so it might take a few moments for all services to be fully operational.

4. **🌐 Access the Application:**
   Once the containers are running, you can access the Doc2Txt web application in your browser at the following URL:

   ```
   http://localhost:3005
   ```

   - The backend will be accessible (for health checks, etc.) at `http://localhost:8005`.

## 📝 Usage

1. **🌐 Open the Application:** Navigate to `http://localhost:3005` in your web browser.
2. **📁 Upload a File:** You will see an upload area where you can either drag and drop a document file or click to browse your file system.
3. **✅ Select MarkItDown (Optional):** If you are uploading a Markdown (`.md`) file and want to use the MarkItDown processor, check the "Use Markitdown" checkbox before uploading.
4. **⚙️ Process the File:** Once you select a file, it will be automatically uploaded and sent to the backend for processing.
5. **👁️ View the Output:** After processing is complete, the extracted text content will be displayed in the "Output" section below the upload area.
6. **📋 Copy the Text:** You can click the "Copy" button next to the "Output" heading to copy the extracted text to your clipboard.
7. **🔄 Reset the App:** Click the "Reset" button in the header to clear the output and upload status, allowing you to process another file.

## 🐳 Docker Compose Details

The `docker-compose.yml` file sets up the following services:

- **`backend`:**
  - Builds the Docker image from the `./backend/Dockerfile`.
  - Maps port `8005` on your host machine to port `8005` in the container (where the FastAPI application runs).
  - Sets the environment variable `TIKA_PATH` (although the current Dockerfile uses the TIKA_SERVER_ENDPOINT environment variable).
  - Defines a health check that pings the `/health` endpoint of the backend.

- **`frontend`:**
  - Builds the Docker image from the `./frontend/Dockerfile`.
  - Maps port `3005` and `8000` on your host machine to the corresponding ports in the container (Reflex uses both).
  - Specifies a dependency on the `backend` service, ensuring the backend is healthy before the frontend starts.
  - Defines a health check that pings the root (`/`) of the frontend application (typically running on port 3005).

## 👥 Contributing

Contributions to this project are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## 📜 License

This project is licensed under the [MIT License](LICENSE).