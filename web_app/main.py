import os  # Import os for path validation
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from fasthtml.common import *
from fasthtml.components import Head, Style
from loguru import logger
from starlette.requests import Request  # Import Request

from whatsapp_analyzer import WhatsAppGroupAnalysis, chat_to_df

# Configure logger
logger.add("whatsapp_analyzer.log", rotation="1 MB", level="INFO")  # Set level to INFO

# Initialize FastHTML app with debug mode, injecting Style within Head via hdrs
FULL_CSS = """
/* Reset and Base Styles */
body {
    background-color: #1a1e24 !important;
    color: #e9ecef !important;
    padding: 2rem !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

.container { 
    max-width: 1200px !important;
    margin: 2rem auto !important;
    padding: 2rem !important;
    background-color: #242931 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}

/* Form Styles */
.form-group { 
    margin-bottom: 1.5rem !important;
}

.form-group label { 
    display: block !important;
    margin-bottom: 0.75rem !important;
    font-weight: 500 !important;
    color: #e9ecef !important;
}

.form-group input[type="file"],
.form-group input[type="number"],
.form-group select { 
    display: block !important;
    width: 100% !important;
    padding: 0.75rem !important;
    border: 2px solid #3a4149 !important;
    border-radius: 8px !important;
    background-color: #2a303c !important;
    color: #e9ecef !important;
    transition: all 0.2s ease !important;
}

.form-group input[type="file"]:focus,
.form-group input[type="number"]:focus,
.form-group select:focus {
    border-color: #3498db !important;
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2) !important;
}

.form-group input[type="checkbox"] {
    margin-top: 0.5rem !important;
    transform: scale(1.2) !important;
    accent-color: #3498db !important;
}

/* Button Styles - Modern & Consistent */
.button-primary,
button[type="submit"],
a.button-secondary { 
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.75rem !important;
    padding: 0.875rem 1.75rem !important;
    border: none !important;
    border-radius: 10px !important;
    cursor: pointer !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    letter-spacing: 0.025em !important;
}

/* Style for the main form submit button */
.button-primary,
button[type="submit"] {
    background: linear-gradient(135deg, #3498db, #2980b9) !important;
    color: white !important;
}

/* Base style for secondary buttons (anchor tags) */
a.button-secondary {
    background: linear-gradient(135deg, #4a5568, #2d3748) !important;
    color: white !important;
}

/* Specific background colors for download/back buttons */
a.download-button {
    background: linear-gradient(135deg, #2ecc71, #27ae60) !important;
    color: white !important;
}

a.back-button {
    background: linear-gradient(135deg, #f1c40f, #f39c12) !important;
    color: #2c3e50 !important;
}

/* Hover states with scale and glow effect */
.button-primary:hover,
button[type="submit"]:hover,
a.button-secondary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15) !important;
}

.button-primary:hover,
button[type="submit"]:hover {
    background: linear-gradient(135deg, #2980b9, #2472a4) !important;
}

a.button-secondary:hover {
    background: linear-gradient(135deg, #2d3748, #1a202c) !important;
}

a.download-button:hover {
    background: linear-gradient(135deg, #27ae60, #219a52) !important;
}

a.back-button:hover {
    background: linear-gradient(135deg, #f39c12, #e67e22) !important;
}

/* Active/pressed state */
.button-primary:active,
button[type="submit"]:active,
a.button-secondary:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

/* Styles for icons and text within buttons */
.button-icon {
    font-size: 1.25rem !important;
    line-height: 1 !important;
}

.button-text {
    font-size: 1rem !important;
    line-height: 1 !important;
    font-weight: 600 !important;
}

.button-group {
    margin: 1.5rem 0 !important;
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
    gap: 1.25rem !important;
    flex-wrap: wrap !important;
}

/* Table Styles */
.table-container {
    overflow-x: auto !important;
    margin: 1.5rem 0 !important;
    border: 1px solid #3a4149 !important;
    border-radius: 8px !important;
    background-color: #2a303c !important;
}

.table { 
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 0 !important;
}

.table th, 
.table td { 
    padding: 1rem !important;
    border: 1px solid #3a4149 !important;
    text-align: left !important;
    font-size: 0.95rem !important;
    color: #e9ecef !important;
}

.table th { 
    background: #3a4149 !important;
    font-weight: 600 !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 1 !important;
    white-space: nowrap !important;
}

.table tbody tr:nth-child(even) {
    background-color: #2f353e !important;
}

.table tbody tr:hover {
    background-color: #3a4149 !important;
}

/* Error Styles */
.error { 
    color: #f8d7da !important;
    background-color: #dc3545 !important;
    border: 1px solid #f5c6cb !important;
    padding: 1rem !important;
    border-radius: 8px !important;
    margin-bottom: 1rem !important;
}

/* Analysis Results Styles */
.container h1,
.container h2 {
    color: #e9ecef !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1.5rem !important;
}

.container p {
    color: #e9ecef !important;
    margin-bottom: 1.5rem !important;
    font-size: 1.1rem !important;
}

/* Fix for file input */
input[type="file"]::file-selector-button {
    background-color: #3498db !important;
    color: white !important;
    padding: 0.5rem 1rem !important;
    border: none !important;
    border-radius: 4px !important;
    cursor: pointer !important;
    margin-right: 1rem !important;
}

input[type="file"]::file-selector-button:hover {
    background-color: #2980b9 !important;
}

/* Select dropdown styling */
select {
    appearance: none !important;
    -webkit-appearance: none !important;
    -moz-appearance: none !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23e9ecef' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: right 0.75rem center !important;
    background-size: 1em !important;
    padding-right: 2.5rem !important;
}
"""

app, rt = fast_app(debug=True, hdrs=(Head(Style(FULL_CSS)),))

# Define TEMP_DIR relative to the script's location for robustness
# Convert to absolute path to avoid ambiguity
# TEMP_DIR = Path(__file__).parent / "temp"
# Using relative path as before, assuming script runs from web_app dir
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
logger.info(f"Temporary directory set to: {TEMP_DIR.resolve()}")

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


@rt("/")
def get():
    """Render the main page with file upload form."""
    return Container(
        H1("WhatsApp Chat Analyzer"),
        P("Upload your WhatsApp chat export file (.txt) to analyze inactive users and participation patterns."),
        Form(
            Div(
                Label("Upload WhatsApp Chat Export (txt file)"),
                Input(type="file", name="chat_file", accept=".txt", required=True),
                class_="form-group",
            ),
            Div(
                Label("Analysis Type"),
                Select(
                    Option("single", "Single Group Analysis"),
                    Option("multiple", "Multiple Groups Analysis"),
                    Option("score", "Score Inactive Users"),
                    name="analysis_type",
                    required=True,
                ),
                class_="form-group",
            ),
            Div(
                Label("Window Days"),
                Input(
                    type="number",
                    name="window_days",
                    value="60",
                    min="1",
                    required=True,
                ),
                class_="form-group",
            ),
            Div(
                Label("Exclude Contacts"),
                Input(type="checkbox", name="exclude_contacts", value="true"),
                class_="form-group",
            ),
            Div(
                Label("Decay Days (for scoring)"),
                Input(type="number", name="decay_days", value="90", min="1"),
                class_="form-group",
            ),
            Div(
                Label("Reference Messages (for scoring)"),
                Input(type="number", name="reference_messages", value="5", min="1"),
                class_="form-group",
            ),
            Button("Analyze Chat", type="submit", class_="button-primary"),
            action="/analyze",
            method="POST",
            enctype="multipart/form-data",
        ),
        class_="container",
    )


def create_table_rows(results):
    """Create table rows from results DataFrame."""
    # Create header row
    header_row = Tr(*[Th(col) for col in results.columns])

    # Create data rows
    data_rows = []
    for _, row in results.iterrows():
        data_rows.append(Tr(*[Td(str(cell)) for cell in row]))

    return header_row, data_rows


@rt("/analyze", methods=["POST"])
async def analyze(req):
    """Handle file upload and analysis."""
    upload_temp_file = None
    try:
        form = await req.form()

        # Get form data
        chat_file = form.get("chat_file")
        if not chat_file:
            return error_response("No file uploaded")

        # Validate file size
        file_size = 0
        upload_temp_file = NamedTemporaryFile(delete=False, dir=TEMP_DIR, suffix=".txt")

        try:
            # Save uploaded file
            with open(upload_temp_file.name, "wb") as f:
                while chunk := await chat_file.read(8192):
                    file_size += len(chunk)
                    if file_size > MAX_FILE_SIZE:
                        return error_response("File too large (max 10MB)")
                    f.write(chunk)

            # Get analysis parameters
            analysis_type = form.get("analysis_type", "single")
            window_days = int(form.get("window_days", 60))
            exclude_contacts = form.get("exclude_contacts") == "true"
            decay_days = int(form.get("decay_days", 90))
            reference_messages = int(form.get("reference_messages", 5))

            # Process the chat file
            df = chat_to_df(upload_temp_file.name)
            if df.empty:
                return error_response(
                    "Could not parse any messages from the uploaded file. Please check the file format."
                )
            analysis = WhatsAppGroupAnalysis(df)

            # Get results based on analysis type
            if analysis_type == "score":
                inactive_users = analysis.get_inactive_users(exclude_contacts=exclude_contacts)
                results = analysis.calculate_activity_score(
                    inactive_users,
                    decay_days=decay_days,
                    reference_messages=reference_messages,
                )
            else:
                results = analysis.get_inactive_users(exclude_contacts=exclude_contacts)

            if results.empty:
                return error_response("Analysis complete, but no users matched the criteria.")

            # Save results to a temporary CSV file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"whatsapp_analysis_{timestamp}.csv"
            try:
                # Ensure the filename is safe (redundant check, but good practice)
                if "/" in csv_filename or ".." in csv_filename:
                    raise ValueError("Invalid characters in generated filename")

                # Resolve the full path *before* saving for consistency
                csv_path = (TEMP_DIR / csv_filename).resolve()
                logger.info(f"Attempting to save analysis results to (resolved path): {csv_path}")
                results.to_csv(csv_path, index=False)
                logger.info(f"Successfully saved analysis results to: {csv_path}")
            except Exception as csv_ex:
                logger.exception(f"Failed to save analysis results to CSV: {csv_ex}")
                return error_response("Failed to save analysis results to a file.")

            # Create table using FastHTML components
            header_row, data_rows = create_table_rows(results)

            return Container(
                H2("Analysis Results"),
                P(f"Found {len(results)} users to analyze."),
                Div(
                    A(
                        Span("⬇️", class_="button-icon"),
                        Span("Download CSV", class_="button-text"),
                        href=f"/downloadfile?filename={csv_filename}",
                        class_="button-secondary download-button",
                        download=csv_filename,
                    ),
                    class_="button-group",
                ),
                Div(
                    Table(Thead(header_row), Tbody(*data_rows), class_="table"),
                    class_="table-container",
                ),
                class_="container",
            )

        finally:
            # Only clean up the uploaded file, NOT the CSV file
            if upload_temp_file and Path(upload_temp_file.name).exists():
                Path(upload_temp_file.name).unlink()
                logger.info(f"Cleaned up temporary upload file: {upload_temp_file.name}")

    except Exception as e:
        logger.exception("Error processing file")
        return error_response(f"Error processing file: {str(e)}")


@rt("/downloadfile", methods=["GET"])
async def get(req: Request):
    """Handle CSV file download via query parameter."""

    # Extract filename from query parameters
    filename = req.query_params.get("filename")
    if not filename:
        logger.warning("Download attempt failed: Missing 'filename' query parameter.")
        return error_response("Missing filename parameter.", status_code=400)

    # --- Add log entry point ---
    logger.info(f"*** DOWNLOAD FUNCTION ENTERED for filename (query param): {filename} ***")
    logger.info(f"Received download request for filename: {filename}")

    # --- Restore Original Code ---
    # --- Security Check ---
    if "/" in filename or ".." in filename or filename.startswith("."):
        logger.warning(f"Download attempt rejected: Invalid filename pattern - {filename}")
        return error_response("Invalid filename.", status_code=400)

    try:
        # Resolve relative TEMP_DIR path and combine with filename
        resolved_temp_dir = TEMP_DIR.resolve()
        file_path = resolved_temp_dir / filename
        logger.info(f"Resolved TEMP_DIR: {resolved_temp_dir}")
        logger.info(f"Constructed absolute file path for download: {file_path}")

        # --- Existence and Permission Check ---
        logger.info(f"Checking existence of file at: {file_path}")
        if not file_path.exists():
            logger.error(f"Download failed: File does not exist at path - {file_path}")
            # Check if the parent directory matches the expected TEMP_DIR
            if not file_path.parent == resolved_temp_dir:
                logger.warning(
                    f"Download failed check: File path {file_path} parent {file_path.parent} is not the expected temp directory {resolved_temp_dir}"
                )
                return error_response("Invalid file location.", status_code=403)
            # Log directory contents for debugging
            try:
                temp_contents = list(resolved_temp_dir.iterdir())
                logger.info(f"Contents of TEMP_DIR ({resolved_temp_dir}): {temp_contents}")
            except Exception as list_ex:
                logger.warning(f"Could not list contents of TEMP_DIR {resolved_temp_dir}: {list_ex}")
            return error_response(
                "File not found. It might have been temporary and already cleaned up, or could not be accessed.",
                status_code=404,
            )

        logger.info(f"File exists at {file_path}. Checking permissions.")
        if not os.access(file_path, os.R_OK):
            logger.error(f"Download failed: No read permissions for file - {file_path}")
            return error_response("Server configuration error: Cannot read file.", status_code=500)

        logger.info(f"File exists and is readable. Preparing FileResponse for {file_path}")
        # Use FileResponse for efficient file serving
        return FileResponse(
            path=str(file_path),  # Pass path as string
            filename=filename,
            media_type="text/csv",
            content_disposition_type="attachment",
        )

    except Exception:
        # Catch any unexpected errors during file serving attempt
        logger.exception(f"Unexpected error during download attempt for {filename}")
        return error_response("Server error during download attempt.", status_code=500)


def error_response(message: str, status_code: int = 500):
    """Return an error page with a specific status code."""
    # Note: FastHTML doesn't directly expose setting status codes on HTML responses easily.
    # In a real FastAPI app, we'd return JSONResponse or HTMLResponse with status_code.
    # For this example, we log the intended code and show the user a generic page.
    logger.info(f"Returning error response with intended status {status_code}: {message}")
    return Container(
        H1(f"Error {status_code}"),
        P(message, class_="error"),
        A("⬅️ Back to Upload", href="/"),
        class_="container",
    )


if __name__ == "__main__":
    serve()
