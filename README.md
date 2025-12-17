Veracode Bulk Upload UI

A lightweight internal web UI built with Flask to perform bulk Veracode API operations using CSV input.
The tool runs as a Docker container and provides live log streaming during execution.

Features
- Upload CSV files to trigger Veracode API actions
- Supports US and EU regions
- Uses Veracode HMAC authentication
- Executes uploads in a background thread
- Live log updates in the browser
- Download execution logs as a text file
- Single page dashboard UI
- Designed for internal shared usage

Architecture Overview

Browser (Dashboard UI)
    |
    | POST /upload
    v
Flask App (Docker)
    |
    | Background Thread
    v
Veracode APIs

Jobs are tracked in memory using a JOB_STORE.
Logs are streamed to the UI via polling using /get_logs/session_id.
No Flask sessions are used for job state.

Project Structure

.
|-- app.py
|-- templates
|   |-- dashboard.html
|-- uploads
|-- csv_in.py
|-- new_api.py
|-- Dockerfile
|-- README.md

Requirements
- Python 3.10 or newer
- Docker
- Veracode API credentials (ID and Secret)

Running with Docker

Build the image
docker build -t veracode-bulkupload .

Run the container
docker run -d -p 2000:2000 -v ~/veracode_uploads:/app/uploads --name veracode-bulkupload --restart unless-stopped veracode-bulkupload

Open in browser
http://host:2000/dashboard

Running Locally

pip install -r requirements.txt
python app.py

Then open
http://localhost:2000/dashboard

CSV Format

Each row represents a Veracode API call.

Example CSV
rownum,apiaction,app_name,sandbox_name
1,createapplication,MyApp,
2,createsandbox,MyApp,Dev

The apiaction column maps to a Veracode API endpoint.
Remaining columns are passed as parameters.

API Endpoints

GET  /dashboard
POST /upload
GET  /get_logs/session_id
GET  /download_logs/session_id

Security Notes
- Intended for internal use only
- API secrets are not stored
- No authentication enabled by default
- Do not expose publicly without access controls

Maintainers
Internal DevSecOps or AppSec team

License
Internal use only
