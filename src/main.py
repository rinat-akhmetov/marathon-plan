import os
from typing import Any, Dict, List, Optional

from src.parse_strava_fit import parse_fit
from src.parse_strava_gpx import parse_gpx
from src.utils import CsvRowData, GpxData, write_csv


def main():
    # Get the directory of the current script
    # current_directory = os.path.dirname(os.path.abspath(__file__))
    current_directory = "export_137365229/activities"

    print(f"Scanning files in: {current_directory}")

    all_run_data: List[CsvRowData] = []

    for filename in os.listdir(current_directory):
        file_path = os.path.join(current_directory, filename)

        if not os.path.isfile(file_path):
            continue

        print(f"Found file: {filename}")

        run_name = ""
        if filename.endswith(".fit.gz"):
            run_name = filename[: -len(".fit.gz")]
        elif filename.endswith(".fit"):
            run_name = filename[: -len(".fit")]
        elif filename.endswith(".gpx"):
            run_name = filename[: -len(".gpx")]
        else:
            print(f"Skipping file with unrecognized extension: {filename}")
            continue

        parsed_data_object: Optional[GpxData] = None
        if filename.endswith(".fit") or filename.endswith(".fit.gz"):
            print(f"Parsing FIT file: {filename}")
            try:
                parsed_data_object = parse_fit(file_path)
            except Exception as e:
                print(f"Error parsing FIT file {filename}: {e}")
        elif filename.endswith(".gpx"):
            print(f"Parsing GPX file: {filename}")
            try:
                parsed_data_object = parse_gpx(file_path)
            except Exception as e:
                print(f"Error parsing GPX file {filename}: {e}")

        if parsed_data_object:
            if parsed_data_object.track_points:
                print(f"Successfully parsed {filename}. Number of records: {len(parsed_data_object.track_points)}")
                try:
                    current_run_points_as_dicts: List[Dict[str, Any]] = []
                    for tp in parsed_data_object.track_points:
                        point_dict = tp.model_dump(exclude_none=False)
                        point_dict["run"] = run_name
                        point_dict["activity_type"] = parsed_data_object.activity_type
                        current_run_points_as_dicts.append(point_dict)

                    # enrich_metrics(current_run_points_as_dicts)

                    current_run_points_as_pydantic: List[CsvRowData] = []
                    for enriched_dict in current_run_points_as_dicts:
                        try:
                            csv_row = CsvRowData(**enriched_dict)
                            current_run_points_as_pydantic.append(csv_row)
                        except Exception as p_exc:
                            print(
                                f"Error converting dict to CsvRowData for {run_name} (file: {filename}): {p_exc}. Dict: {enriched_dict}"
                            )

                    all_run_data.extend(current_run_points_as_pydantic)

                except ValueError as ve:
                    print(f"Skipping enrichment/conversion for {filename} due to ValueError: {ve}")
                except Exception as e:
                    print(f"Error processing or converting data for {filename}: {e}")
            else:
                print(f"Parsed {filename}, but it contained no track points.")
        else:
            print(f"Parsing {filename} did not yield a data object (it might have failed silently or returned None).")

    if all_run_data:
        output_csv_filename = "consolidated_activity_data.csv"
        try:
            print(f"\nWriting consolidated data for {len(all_run_data)} track points to {output_csv_filename}...")
            write_csv(all_run_data, output_csv_filename)
            print(f"\n💾 Consolidated data for all runs written to {output_csv_filename}")
        except Exception as e:
            print(f"\n❌ Error writing consolidated CSV {output_csv_filename}: {e}")
    else:
        print("\nNo data processed to write to CSV.")


if __name__ == "__main__":
    main()
