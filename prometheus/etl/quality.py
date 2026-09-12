
import json
from pathlib import Path

from pydantic import ValidationError

from schemas import FlightRecord


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "normalised_data.json"
VALID_FILE = BASE_DIR / "data" / "validated_data.json"
INVALID_FILE = BASE_DIR / "data" / "invalid_data.json"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_data():
    """
    Load normalised flight data from normalised_data.json.
    """

    print("Looking for input file:")
    print(INPUT_FILE)

    if not INPUT_FILE.exists():
        print("\nData folder contents:")

        data_folder = INPUT_FILE.parent

        if data_folder.exists():
            for file in data_folder.iterdir():
                print(f"  - {file.name}")
        else:
            print("  Data folder does not exist.")

        raise FileNotFoundError(
            f"\nInput file not found:\n{INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Input data must be a JSON list of flight records."
        )

    return data


# ---------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------

def save_json(data, file_path):
    """
    Save data to a JSON file.
    """

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ---------------------------------------------------------
# VALIDATE ONE RECORD
# ---------------------------------------------------------

def validate_record(record, index):
    """
    Validate one flight record using the Pydantic schema.
    """

    try:

        # Validate the record
        validated_record = FlightRecord.model_validate(record)

        return {
            "valid": True,
            "data": validated_record.model_dump(mode="json")
        }

    except ValidationError as error:

        errors = []

        # Convert Pydantic errors into simple strings
        for err in error.errors():

            field = ".".join(
                str(location)
                for location in err["loc"]
            )

            message = err["msg"]

            errors.append(
                f"{field}: {message}"
            )

        return {
            "valid": False,
            "data": record,
            "errors": errors,
            "record_number": index + 1
        }


# ---------------------------------------------------------
# RUN QUALITY CHECK
# ---------------------------------------------------------

def run_quality_check(data):
    """
    Validate every flight record.
    """

    valid_records = []
    invalid_records = []

    print(f"\nTotal records received: {len(data)}")
    print("\nValidating records...\n")

    for index, record in enumerate(data):

        result = validate_record(record, index)

        if result["valid"]:

            valid_records.append(
                result["data"]
            )

        else:

            invalid_records.append({
                "record_number": result["record_number"],
                "data": result["data"],
                "errors": result["errors"]
            })

    return valid_records, invalid_records


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("\n======================================")
    print("       DATA QUALITY VALIDATION")
    print("======================================")

    # Load normalised data
    data = load_data()

    # Validate records
    valid_records, invalid_records = run_quality_check(data)

    # Save valid records
    save_json(
        valid_records,
        VALID_FILE
    )

    # Save invalid records
    save_json(
        invalid_records,
        INVALID_FILE
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print("\n======================================")
    print("       DATA QUALITY SUMMARY")
    print("======================================")

    print(f"Total records   : {len(data)}")
    print(f"Valid records   : {len(valid_records)}")
    print(f"Invalid records : {len(invalid_records)}")

    print("\n--------------------------------------")

    print(
        f"Validated data saved at:\n"
        f"{VALID_FILE}"
    )

    print(
        f"\nInvalid data saved at:\n"
        f"{INVALID_FILE}"
    )

    print("--------------------------------------")

    # -----------------------------------------------------
    # SHOW INVALID RECORDS
    # -----------------------------------------------------

    if invalid_records:

        print("\nInvalid record details:")

        for item in invalid_records:

            print(
                f"\nRecord {item['record_number']}:"
            )

            for error in item["errors"]:

                print(f"  - {error}")

    else:

        print(
            "\nAll records passed "
            "quality validation! ✅"
        )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    main()

