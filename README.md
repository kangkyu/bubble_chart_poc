# bubble_chart_poc

A Streamlit bubble chart of video performance: views across, average view
duration up, total watch time as bubble area.

Data comes from the [slide-gen-reports](../slide-gen-reports) API
(`POST /v1/traffic_source/videos`, the IDs in the request body), over the
latest 7 report dates. Enter one video ID per line in the **Video IDs** box
and press **Show**; the new list replaces the previous one. The chart stays
empty until there are IDs, and **Clear** empties the box and the chart.

## Running locally

1. **Install Python 3.11 or newer** (developed on 3.13):

   ```sh
   python3 --version
   ```

2. **Create a virtual environment** in the project folder:

   ```sh
   cd bubble_chart_poc
   python3 -m venv .venv
   ```

3. **Install the dependencies:**

   ```sh
   .venv/bin/pip install -r requirements.txt
   ```

4. **Run the app** with the API's base URL and token:

   ```sh
   REPORTS_API_URL=https://<slide-gen-reports host> \
   REPORTS_API_TOKEN=<API token> \
   .venv/bin/streamlit run app.py
   ```

   - `REPORTS_API_URL` is the service's base URL only, without `/v1/...`;
     the app adds the path. For the Cloud Run service, it is
     `terraform output api_url` in slide-gen-reports' `terraform/`. For that
     API running locally, it is `http://localhost:8000`.
   - `REPORTS_API_TOKEN` is the API's `API_TOKEN`.

5. **Open the app.** Streamlit prints a URL, usually
   <http://localhost:8501>, and opens it in your browser.

6. **Stop the app** with `Ctrl+C` in the terminal.

## Troubleshooting

- **"Couldn't load the report: REPORTS_API_URL is not set"**: set it when
  running the app (step 4).
- **"Couldn't load the report: 401 … Unauthorized"**: `REPORTS_API_TOKEN`
  is wrong or missing.
- **"Couldn't load the report: 404 …"**: `REPORTS_API_URL` probably includes
  a path; set it to the base URL only.
- **"No views in the period for any of these videos"**: none of the IDs had
  views in the latest 7 report dates, or the API has no report dates loaded.
- **"Not video IDs"**: a video ID is 11 letters, digits, `-` or `_`, e.g.
  `ffZz5vM6BZ0`, not a full YouTube URL.
- **"No views in the period for: …"**: those videos had no views in the
  latest 7 report dates, so the API left them out.
- **Stale numbers**: API responses are cached for 10 minutes. Press `C` in
  the app (or use the ⋮ menu > *Clear cache*), then `R` to rerun.

## Files

| | |
|---|---|
| `app.py` | Streamlit page: filters, chart, size key, table view |
| `chart.py` | Plotly bubble chart and number formatting |
| `data.py` | API request and the column contract (`Columns`) |
| `theme.py` | Light and dark palettes |
