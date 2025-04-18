import os
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from fasthtml.common import *
from fasthtml.components import Head, Style
from loguru import logger
from starlette.requests import Request

from src.core.analysis import WhatsAppGroupAnalysis
from src.core.utils import chat_to_df

# Configure logger
logger.add("whatsapp_analyzer.log", rotation="1 MB", level="INFO")

# Initialize FastHTML app with debug mode
app = FastHTML(debug=True)

# Load CSS from file
with open(Path(__file__).parent / "static" / "styles.css") as f:
    FULL_CSS = f.read()


@rt("/")
def get():
    """Render the main page with the analysis form."""
    return html(
        head(
            title("WhatsApp Group Analysis"),
            meta(charset="utf-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1"),
            Style(FULL_CSS),
        ),
        body(
            div(
                h1("WhatsApp Group Analysis"),
                p("Upload a WhatsApp chat export to analyze group activity and identify inactive users."),
                form(
                    div(
                        label("Chat Export File"),
                        input(type="file", name="file", accept=".txt", required=True),
                        class_="form-group",
                    ),
                    div(
                        label("Window Days"),
                        input(type="number", name="window_days", value="60", min="1", max="365", required=True),
                        class_="form-group",
                    ),
                    div(
                        label("Exclude Contacts"),
                        input(type="checkbox", name="exclude_contacts"),
                        class_="form-group",
                    ),
                    div(
                        button("Analyze", type="submit"),
                        class_="button-group",
                    ),
                    action="/analyze",
                    method="post",
                    enctype="multipart/form-data",
                ),
                class_="container",
            )
        ),
    )


def create_table_rows(results):
    """Create HTML table rows from analysis results."""
    rows = []
    for _, row in results.iterrows():
        cells = []
        for col in results.columns:
            if col == "Most_Recent_Message_Date":
                value = row[col].strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(row[col]) else "Never"
            elif col == "Joining_Date":
                value = row[col].strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(row[col]) else "Unknown"
            else:
                value = row[col]
            cells.append(td(str(value)))
        rows.append(tr(*cells))
    return rows


@rt("/analyze", methods=["POST"])
async def analyze(req):
    """Handle the analysis form submission."""
    try:
        form = await req.form()
        file = form["file"]
        window_days = int(form["window_days"])
        exclude_contacts = "exclude_contacts" in form

        # Save uploaded file
        with NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        # Analyze the chat
        df = chat_to_df(temp_path)
        analysis = WhatsAppGroupAnalysis(df)
        inactive_users = analysis.get_inactive_users(exclude_contacts=exclude_contacts)
        message_counts = analysis.get_message_count_in_window(window_days=window_days)
        result = pd.merge(inactive_users, message_counts, on="User", how="left")

        # Clean up temp file
        os.unlink(temp_path)

        # Create download file
        download_path = Path("temp") / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        download_path.parent.mkdir(exist_ok=True)
        result.to_csv(download_path, sep="|", index=False)

        return html(
            head(
                title("Analysis Results"),
                meta(charset="utf-8"),
                meta(name="viewport", content="width=device-width, initial-scale=1"),
                Style(FULL_CSS),
            ),
            body(
                div(
                    h1("Analysis Results"),
                    p(f"Found {len(result)} inactive users in the chat."),
                    div(
                        table(
                            thead(
                                tr(
                                    *[th(col.replace("_", " ").title()) for col in result.columns]
                                )
                            ),
                            tbody(*create_table_rows(result)),
                            class_="table",
                        ),
                        class_="table-container",
                    ),
                    div(
                        a(
                            span("⬇️", class_="button-icon"),
                            span("Download Results", class_="button-text"),
                            href="/downloadfile",
                            class_="button-secondary download-button",
                        ),
                        a(
                            span("←", class_="button-icon"),
                            span("Back", class_="button-text"),
                            href="/",
                            class_="button-secondary back-button",
                        ),
                        class_="button-group",
                    ),
                    class_="container",
                )
            ),
        )
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return error_response(str(e))


@rt("/downloadfile", methods=["GET"])
async def get(req: Request):
    """Handle file downloads."""
    try:
        download_path = Path("temp") / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if not download_path.exists():
            return error_response("File not found", 404)
        return FileResponse(download_path)
    except Exception as e:
        logger.error(f"Error during file download: {str(e)}")
        return error_response(str(e))


def error_response(message: str, status_code: int = 500):
    """Return an error response page."""
    return html(
        head(
            title("Error"),
            meta(charset="utf-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1"),
            Style(FULL_CSS),
        ),
        body(
            div(
                h1("Error"),
                div(message, class_="error"),
                div(
                    a(
                        span("←", class_="button-icon"),
                        span("Back", class_="button-text"),
                        href="/",
                        class_="button-secondary back-button",
                    ),
                    class_="button-group",
                ),
                class_="container",
            )
        ),
        status_code=status_code,
    ) 