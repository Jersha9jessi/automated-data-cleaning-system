
import pandas as pd
import sqlite3
import re
import json
from pathlib import Path
from datetime import datetime


def load_file(file_path):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("File not found.")

    extension = path.suffix.lower()

    if extension == ".csv":
        try:
            return pd.read_csv(path)
        except UnicodeDecodeError:
            return pd.read_csv(path, encoding="latin-1")

    elif extension == ".xlsx":
        return pd.read_excel(path)

    else:
        raise ValueError("Only CSV and XLSX files are supported.")


def clean_column_names(df):
    new_columns = []

    for column in df.columns:
        name = str(column).strip().lower()
        name = re.sub(r"[^a-z0-9]+", "_", name)
        name = name.strip("_")

        if not name:
            name = "column"

        new_columns.append(name)

    # Make duplicate column names unique
    counts = {}
    unique_columns = []

    for name in new_columns:
        counts[name] = counts.get(name, 0) + 1

        if counts[name] > 1:
            unique_columns.append(
                f"{name}_{counts[name]}"
            )
        else:
            unique_columns.append(name)

    df.columns = unique_columns
    return df


def get_quality_report(df):
    report = []

    for column in df.columns:
        report.append({
            "Column": column,
            "Data Type": str(df[column].dtype),
            "Total Rows": len(df),
            "Missing Values": int(df[column].isna().sum()),
            "Missing Percentage": round(
                df[column].isna().mean() * 100, 2
            ),
            "Unique Values": int(df[column].nunique())
        })

    return pd.DataFrame(report)

def clean_dates(df):
    date_columns = []

    for column in df.columns:
        if "date" in column or "time" in column:
            parsed = pd.to_datetime(
                df[column], errors="coerce"
            )

            valid_count = parsed.notna().sum()

            if valid_count > 0:
                df[column] = parsed.dt.strftime(
                    "%Y-%m-%d"
                )
                date_columns.append(column)

    return df, date_columns


def validate_emails(df):
    email_pattern = (
        r"^[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    invalid_records = []

    for column in df.columns:
        if "email" in column:
            values = df[column].fillna("").astype(str)

            for index, value in values.items():
                value = value.strip()

                if value and not re.match(
                    email_pattern, value
                ):
                    invalid_records.append({
                        "Row": int(index) + 2,
                        "Column": column,
                        "Invalid Email": value
                    })

    return pd.DataFrame(
        invalid_records,
        columns=["Row", "Column", "Invalid Email"]
    )


def fill_missing_values(df):
    df = df.copy()

    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            median = df[column].median()

            if pd.notna(median):
                df[column] = df[column].fillna(median)

        elif (
            pd.api.types.is_object_dtype(df[column])
            or pd.api.types.is_string_dtype(df[column])
        ):
            df[column] = df[column].fillna("Unknown")

    return df

def clean_data(file_path):
    original = load_file(file_path)

    if original.empty:
        raise ValueError("The input file has no data.")

    original_rows = len(original)
    original_columns = len(original.columns)

    before_report = get_quality_report(original)

    df = original.copy()

    # Clean column names
    df = clean_column_names(df)

    # Remove extra spaces in text
    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:
        df[column] = df[column].map(
            lambda value: value.strip()
            if isinstance(value, str) else value
        )

    # Remove duplicate rows
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates()

    # Standardize date columns
    df, date_columns = clean_dates(df)

    # Validate email columns
    invalid_emails = validate_emails(df)

    # Fill missing values
    df = fill_missing_values(df)

    after_report = get_quality_report(df)

    # Before and after comparison
    comparison = pd.DataFrame([
        {"Metric": "Rows", "Before": original_rows,
         "After": len(df)},
        {"Metric": "Columns", "Before": original_columns,
         "After": len(df.columns)},
        {"Metric": "Duplicate Rows", "Before": duplicate_count,
         "After": 0},
        {"Metric": "Missing Cells",
         "Before": int(original.isna().sum().sum()),
         "After": int(df.isna().sum().sum())}
    ])

    # Output file names
    source = Path(file_path)
    output_excel = source.with_name(
        source.stem + "_cleaned.xlsx"
    )
    output_db = source.with_name(
        source.stem + "_cleaned.db"
    )
    output_json = source.with_name(
        source.stem + "_report.json"
    )

    # Save Excel report
    with pd.ExcelWriter(
        output_excel, engine="openpyxl"
    ) as writer:
        df.to_excel(
            writer, sheet_name="Cleaned Data",
            index=False
        )
        before_report.to_excel(
            writer, sheet_name="Before Quality",
            index=False
        )
        after_report.to_excel(
            writer, sheet_name="After Quality",
            index=False
        )
        comparison.to_excel(
            writer, sheet_name="Comparison",
            index=False
        )
        invalid_emails.to_excel(
            writer, sheet_name="Invalid Emails",
            index=False
        )

    # Save SQLite database
    with sqlite3.connect(output_db) as connection:
        df.to_sql(
            "cleaned_data",
            connection,
            if_exists="replace",
            index=False
        )

    # Save JSON summary
    summary = {
        "source_file": str(source),
        "processed_at": datetime.now().isoformat(),
        "original_rows": original_rows,
        "cleaned_rows": len(df),
        "original_columns": original_columns,
        "cleaned_columns": len(df.columns),
        "duplicates_removed": duplicate_count,
        "invalid_emails": len(invalid_emails),
        "date_columns_cleaned": date_columns,
        "missing_values_before": int(
            original.isna().sum().sum()
        ),
        "missing_values_after": int(
            df.isna().sum().sum()
        ),
        "unresolved_missing_columns": {
            column: int(count)
            for column, count in df.isna().sum().items()
            if count > 0
        }
    }

    with open(output_json, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)
    print("\n========== CLEANING COMPLETED ==========")
    print("Original rows:", original_rows)
    print("Cleaned rows:", len(df))
    print("Duplicates removed:", duplicate_count)
    print("Invalid emails:", len(invalid_emails))
    print("Date columns cleaned:", date_columns)
    print("\nGenerated files:")
    print("Excel:", output_excel)
    print("Database:", output_db)
    print("JSON report:", output_json)
    print("========================================")


def main():
    print("\nAUTOMATED DATA CLEANING SYSTEM")
    print("--------------------------------")

    file_path = input(
        "Enter CSV or XLSX file path: "
    ).strip().strip('"')

    try:
        clean_data(file_path)

    except Exception as error:
        print("\nERROR:", error)


if __name__ == "__main__":
    main()
