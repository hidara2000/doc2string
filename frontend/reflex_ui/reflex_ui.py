import base64
from typing import List, Dict, Any

import httpx
import reflex as rx


class State(rx.State):
    """The app state."""
    text: str = ""              # The extracted text from the processed file.
    processing: bool = False    # Whether a file is currently being processed.
    upload_status: str = ""     # The status message related to file upload and processing.
    show_output: bool = False   # Whether to display the output text.
    use_markitdown: bool = False# Whether to use the MarkItDown processor.

    @rx.var
    def is_file_uploaded(self) -> bool:
        """Checks if a file has been uploaded successfully."""
        return self.upload_status != ""

    @rx.event
    async def handle_upload(self, files: List[rx.UploadFile]):
        """Handle the upload of file(s).

        Reads the content of the first file in the list, encodes it to base64,
        and sends it to the backend for processing. Updates the UI based on the
        processing status and the response from the backend.

        Args:
            files: A list of uploaded files.
        """
        if not files:
            return

        self.processing = True
        try:
            self.show_output = True
            current_file = files[0]
            upload_data = await current_file.read()
            self.upload_status = f"Processing {current_file.name}..."

            # Convert bytes to base64 string for JSON serialization
            base64_data = base64.b64encode(upload_data).decode('utf-8')

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://backend:8005/process",
                    json={
                        "filename": current_file.name,
                        "file": base64_data,
                        "use_markitdown": self.use_markitdown
                    }
                )
                self.text = response.json()["text"]

            self.upload_status = f"File uploaded: {current_file.name}"
        except Exception as e:
            self.text = f"Error processing file: {str(e)}"
            self.upload_status = "Upload failed. Please try again."
        finally:
            self.processing = False

    @rx.event
    async def reset_app(self):
        """Reset the app to its initial state.

        Clears the extracted text, resets processing flags, and clears the
        upload status.
        """
        self.text = ""
        self.processing = False
        self.upload_status = ""
        self.show_output = False
        self.use_markitdown = False


def get_styles() -> Dict[str, Dict[str, Any]]:
    """Define the styles for the components in the app.

    Returns:
        A dictionary containing style definitions for various UI elements.
    """
    return {
        "container": {
            "width": "100%",
            "max_width": "800px",
            "padding": "1.5em",
            "border_radius": "xl",
            "box_shadow": "xl",
            "background": "gray.900",
            "margin_top": "2em",
        },
        "text": {
            "color": "white",
        },
        "heading": {
            "color": "white",
            "size": "3",
        },
        "heading_large": {
            "color": "white",
            "size": "2",
            "margin_bottom": "0",
        },
        "icon": {
            "color": "cyan.300",
            "font_size": "1.5em",
            "margin_right": "0.5em",
        },
        "icon_large": {
            "color": "cyan.300",
            "font_size": "2em",
            "margin_right": "0.5em",
        },
        "success_icon": {
            "color": "cyan.900",
            "font_size": "1.5em",
            "margin_right": "0.5em",
        },
        "copy_button": {
            "variant": "outline",
            "color_scheme": "cyan",
            "border_width": "2px",
            "size": "2",
            "border_radius": "md",
        },
        "reset_button": {
            "variant": "outline",
            "color_scheme": "red",
            "border_width": "2px",
            "size": "2",
            "border_radius": "md",
        },
        "upload": {
            "border": "3px dashed",
            "border_color": "cyan.300",
            "background": "rgba(255, 255, 255, 0.05)",
            "border_radius": "xl",
            "padding": "2.5em",
            "width": "100%",
            "_hover": {
                "border_color": "cyan.400",
                "background": "rgba(255, 255, 255, 0.1)",
                "transform": "scale(1.01)",
            },
            "color_scheme": "cyan",
        },
        "layout": {
            "width": "100%",
            "spacing": "4",
            "align_items": "center",
        },
        "background": {
            "background": "rgb(15, 15, 20)",
            "min_height": "100vh",
            "padding": "2em",
            "display": "flex",
            "justify_content": "center",
            "align_items": "center",
        },
        "status_indicator": {
            "background": "rgba(30, 30, 40, 0.7)",
            "padding": "0.75em",
            "border_radius": "md",
            "border": "1px solid rgba(0, 255, 255, 0.2)",
            "width": "100%",
            "color_scheme": "cyan",
        },
        "processing": {
            "width": "100%",
            "padding": "2em",
            "align": "center",
        },
        "markdown": {
            "background": "gray.800",
            "padding": "1.5em",
            "border_radius": "md",
            "width": "100%",
            "color": "white",
            "overflow": "auto",
            "max_height": "500px",
            "css": {
                "pre": {
                    "background": "gray.700",
                    "padding": "0.5em",
                    "border_radius": "md"
                },
                "code": {
                    "color": "cyan.300",
                }
            },
        },
        "header": {
            "padding": "1em",
            "padding_bottom": "0",
            "width": "100%",
            "max_width": "800px",
        },
        "description": {
            "color": "white",
            "font_size": "lg",
            "font_weight": "medium",
            "mt": "1",
        },
        "divider": {
            "border_color": "gray.700",
        },
        "spinner": {
            "color": "blue.400",
            "size": "3",
        },
        "checkbox": {
            "color_scheme": "cyan",
        }
    }


def index() -> rx.Component:
    """The main view of the file processing app.

    Returns:
        A Reflex component representing the user interface.
    """
    styles = get_styles()

    return rx.box(
        rx.vstack(
            # Header
            rx.box(
                rx.hstack(
                    rx.icon("file-code", **styles["icon_large"]),
                    rx.heading("File Processor", **styles["heading_large"]),
                    rx.spacer(),
                    rx.button(
                        rx.hstack(
                            rx.icon("refresh_ccw", color="red.300", font_size="1.2em"),
                            rx.text("Reset", color="white"),
                        ),
                        **styles["reset_button"],
                        on_click=State.reset_app,
                    ),
                    width="100%",
                ),
                rx.text(
                    "Upload a file to process automatically",
                    **styles["description"],
                ),
                **styles["header"],
            ),

            # Upload Area
            rx.box(
                rx.vstack(
                    rx.cond(
                        State.processing,
                        rx.vstack(
                            rx.spinner(**styles["spinner"]),
                            rx.text("Processing your file...", **styles["text"]),
                            **styles["processing"],
                        ),
                        rx.upload(
                            rx.flex(
                                rx.icon("upload", **styles["icon"]),
                                rx.text("Drop your file here or click to browse", **styles["text"]),
                                direction="row",
                                align="center",
                            ),
                            **styles["upload"],
                            multiple=False,
                            on_drop=State.handle_upload(rx.upload_files(upload_id="file-upload")),
                            id="file-upload",
                        ),

                    ),
                    rx.checkbox(
                        "Use Markitdown",
                        is_checked=State.use_markitdown,
                        on_change=State.set_use_markitdown,
                        **styles["checkbox"],
                    ),
                    rx.cond(
                        State.is_file_uploaded,
                        rx.hstack(
                            rx.icon("circle-check", **styles["success_icon"]),
                            rx.text(State.upload_status, **styles["text"]),
                            **styles["status_indicator"],
                        ),
                    ),


                    **styles["layout"],
                ),
                **styles["container"],
            ),

            # Output Display
            rx.cond(
                State.show_output,
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Output", **styles["heading"]),
                            rx.spacer(),
                            rx.button(
                                rx.icon("copy", **styles["icon"]),
                                **styles["copy_button"],
                                on_click=rx.set_clipboard(State.text),
                            ),
                            width="100%",
                        ),
                        rx.divider(**styles["divider"]),
                        rx.markdown(State.text, **styles["markdown"]),
                        **styles["layout"],
                    ),
                    **styles["container"],
                ),
            ),
            
            # Set spacing and width for the vstack
            spacing="6",
            max_width="1200px",
            margin_y="2em",
            # Removed duplicate align_items here
        ),
        **styles["background"],
    )

# Create and configure the app
app = rx.App(
    style={
        "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
        "color": "#FFFFFF",
    },
    stylesheets=["https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"],
)

app.add_page(index)