# Marathon Training Plan Analyzer

This project provides tools to analyze marathon training data exported from Strava, helping runners gain insights into their training progress and performance.

## Business Requirements

- To offer runners a way to perform a detailed analysis of their Strava training data beyond the standard features available on the platform.
- To enable users to track key metrics, understand their effort distribution (e.g., heart rate zones), and monitor progress over a training cycle.
- To provide actionable insights that can help in adjusting training plans for better performance and injury prevention.

## Functional Requirements

The system shall be able to:
1.  Parse and process activity data exported from Strava (FIT and GPX file formats).
2.  Consolidate data from multiple activities into a structured format.
3.  Perform analysis on the consolidated data, including:
    *   Summarizing key statistics (distance, time, pace, heart rate).
    *   Visualizing data, such as heart rate distribution across zones.
4.  Allow users to execute the processing and analysis steps through provided Python scripts.

## Workflow / Usage

The primary workflow for using this toolset is as follows:

1.  **Export Data from Strava**:
    *   Obtain your activity data export from Strava. This typically includes `.fit` or `.gpx` files.
    *   Place these exported files in a directory accessible by the scripts (e.g., within the project or a specified input path).

2.  **Initial Data Processing (`main.py`)**:
    *   Run the `main.py` script. This script is responsible for:
        *   Parsing the raw Strava export files (e.g., from a directory containing FIT/GPX files).
        *   Consolidating the relevant data points from these files.
        *   Generating an intermediate processed data file (e.g., `consolidated_activity_data.csv` or `output.csv`).

3.  **Data Analysis (`analyze.py`)**:
    *   Once the initial processing is complete and the intermediate data file is generated, run the `analyze.py` script.
    *   This script takes the processed data as input and performs further analysis, such as:
        *   Generating summary statistics (e.g., `summary.csv`).
        *   Creating visualizations (e.g., `hr_zones.png` showing heart rate distribution).

## Key Files

*   `main.py`: Script for initial parsing and consolidation of Strava export data.
*   `analyze.py`: Script for performing detailed analysis on the processed data.
*   `parse_strava_fit.py`: Utility script likely used by `main.py` to handle FIT file parsing.
*   `parse_strava_gpx.py`: Utility script likely used by `main.py` to handle GPX file parsing.
*   `utils.py`: Contains common utility functions used by other scripts.
*   `consolidated_activity_data.csv` / `output.csv`: Example or typical output file from `main.py`, serving as input for `analyze.py`.
*   `summary.csv`: Example or typical output file from `analyze.py`, containing summary statistics.
*   `hr_zones.png`: Example visualization output from `analyze.py`.

## Setup and Dependencies

(To be filled in with details about setting up the Python environment, installing dependencies from `pyproject.toml` or a `requirements.txt` if available, etc.)

Please ensure you have Python installed and the necessary libraries as defined in the project's dependency files.
