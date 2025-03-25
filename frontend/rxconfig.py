import reflex as rx


config = rx.Config(
    app_name="reflex_ui",
    frontend_port=3005,  # Custom frontend port
    api_url="http://localhost:8000",  # Add this line
)
