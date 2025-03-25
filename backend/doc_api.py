from typing import Optional, Tuple, Dict, Any, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
from io import BytesIO
import os
import tika
from tika import parser
from markitdown import MarkItDown
import tempfile
import requests
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Tika to use server
tika_server_endpoint = os.environ.get('TIKA_SERVER_ENDPOINT', 'http://localhost:9998')
os.environ['TIKA_SERVER_ENDPOINT'] = tika_server_endpoint
logging.info(f"Using Tika server at: {tika_server_endpoint}")

app = FastAPI()

class RequestData(BaseModel):
    """
    Represents the data expected in the request body for document processing.
    """
    filename: str
    file: str
    use_markitdown: bool = False

@app.post("/process")
async def process_document(data: RequestData) -> Dict[str, Any]:
    """
    Processes a document using either Tika or MarkItDown based on the request.

    Args:
        data (RequestData): The request data containing the filename, file content (as base64 or bytes), and a flag to use MarkItDown.

    Returns:
        Dict[str, Any]: A dictionary containing the processing status, extracted text, metadata, filename, and the parser used.

    Raises:
        HTTPException (400): If the file string cannot be decoded as base64.
        HTTPException (500): If any error occurs during document processing.
    """
    try:
        # Check if file is already in bytes format or base64 string
        if isinstance(data.file, str):
            try:
                # Try to decode as base64
                file_data: bytes = base64.b64decode(data.file)
            except Exception as decode_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to decode base64 string: {str(decode_error)}"
                )
        elif isinstance(data.file, bytes):
            # If it's already bytes, use it directly
            file_data = data.file
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Expected base64 string or bytes."
            )

        # Determine which parser to use based on use_markitdown flag
        if data.use_markitdown:
            # Use the MarkItDown library
            text, metadata = process_with_markitdown(file_data, data.filename)
        else:
            # Use the Tika parser
            text, metadata = process_with_tika(file_data)

        return {
            "status": True,
            "text": text,
            "metadata": metadata,
            "filename": data.filename,
            "parser_used": "markitdown" if data.use_markitdown else "tika"
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Error processing document: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

def process_with_tika(file_data: bytes) -> Tuple[str, Dict[str, Any]]:
    """
    Processes file data using the Tika parser.

    Args:
        file_data (bytes): The file content as bytes.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing the extracted text and metadata.

    Raises:
        Exception: If content extraction using Tika fails.
    """
    # Create a BytesIO object to act as a buffer
    file_buffer = BytesIO(file_data)

    # Parse the file using Tika from the buffer
    try:
        parsed = parser.from_buffer(file_buffer)
    except tika.TikaException as e:
        logging.error(f"Tika error: {e}")
        raise Exception(f"Error during Tika parsing: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Tika server connection error: {e}")
        raise Exception(f"Error connecting to Tika server: {e}")

    # Check if content was extracted successfully
    if parsed is None or "content" not in parsed:
        raise Exception("Failed to extract content from file using Tika")

    text: Optional[str] = parsed.get("content")
    metadata: Dict[str, Any] = parsed.get("metadata", {})

    # Handle case where content is None
    if text is None:
        text = ""

    return text, metadata

def process_with_markitdown(file_data: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
    """
    Processes file data using the MarkItDown library.

    Args:
        file_data (bytes): The file content as bytes.
        filename (str): The original filename of the document.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing the extracted text and metadata.
    """
    # Create a temporary file to store the data
    temp_file_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(file_data)
            temp_file_path = temp_file.name

        # Initialize MarkItDown
        md = MarkItDown(enable_plugins=True)

        # Convert the file
        result = md.convert(temp_file_path)

        # Extract text content
        text: str = result.text_content

        # Create metadata dict (MarkItDown might have different metadata structure)
        metadata: Dict[str, Any] = {
            "markitdown_version": getattr(result, "version", "unknown"),
            "file_type": os.path.splitext(filename)[1],
        }

        return text, metadata
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Performs a health check for the application and its dependencies.

    Returns:
        Dict[str, str]: A dictionary containing the health status of the service, Tika server, and MarkItDown.
    """
    tika_status: str
    try:
        # Try to ping the Tika server
        response = requests.get(f"{tika_server_endpoint}/tika")
        tika_status = "available" if response.status_code == 200 else f"error ({response.status_code})"
    except requests.exceptions.RequestException as e:
        tika_status = f"error (connection error: {str(e)})"
    except Exception as e:
        tika_status = f"error ({str(e)})"

    markitdown_status: str
    try:
        md = MarkItDown(enable_plugins=False)
        markitdown_status = "available"
    except Exception as e:
        markitdown_status = f"error ({str(e)})"

    return {
        "status": "healthy",
        "service": "doc2txt-backend",
        "tika_server": tika_status,
        "markitdown": markitdown_status
    }

@app.get("/test")
async def test_endpoint() -> Dict[str, str]:
    """
    A simple test endpoint to check if the application is running.

    Returns:
        Dict[str, str]: A dictionary indicating the status and a message.
    """
    return {
        "status": "ok",
        "message": "Test endpoint is working!",
        "service": "doc2txt-backend",
        "tika_server": tika_server_endpoint
    }