Service account setup for Google Sheets
=====================================

1. Open Google Cloud Console and create (or select) a project.
2. Enable the "Google Sheets API" for the project.
3. Create a Service Account under IAM & Admin -> Service Accounts.
4. Create a JSON key for the service account and download it.
5. Share the Google Sheet with the service account email (client_email in the JSON).
6. Place the JSON file in the project root and name it `credentials.json`, or set `GOOGLE_APPLICATION_CREDENTIALS` in your `.env` to its path.
7. Make sure `.env` contains the correct `SPREADSHEET_ID` and `SHEET_NAME` (the exact sheet tab name).

Troubleshooting `invalid_scope` error
-------------------------------------
- The `invalid_scope` error often appears when using an OAuth client JSON (web/installed) instead of a service account JSON.
- Confirm that `credentials.json` contains "type": "service_account" near the top.
- If not, create a service account key as described above and replace the credentials file.

Usage in this project
---------------------
- The app reads `GOOGLE_APPLICATION_CREDENTIALS` (or uses `credentials.json` in the project root).
- The code now explicitly loads service account credentials with the required scopes:
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive`

If you want, I can add a short checklist to the main `README.md` as well.
