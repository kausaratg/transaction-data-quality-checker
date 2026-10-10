import pandas as pd
import numpy as np

def check_transactions(file):
    # Read values as text to preserve IDs and original entries.
    df = pd.read_csv(file, dtype=str, keep_default_na=False)

    required_columns = [
        "transaction_id",
        "amount",
        "transaction_date",
        "status",
    ]


    # KEEP A LIST OF ISSUES
    issues = [[] for _ in range(len(df))]


    # CHECK FOR EMPTY COLUMNS IN EACH ROW
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    for column in required_columns:
        missing = df[column].str.strip().eq("")

        for row_index in df.index[missing]:
            issues[row_index].append(f"Missing {column}")


    # CHECK FOR VALID DATE
    date_values = df["transaction_date"].str.strip()
    # Accept day/month/year, including single-digit days or months.
    correct_format = date_values.str.fullmatch(
        r"\d{1,2}/\d{1,2}/\d{4}"
    )

    parsed_dates = pd.to_datetime(
        date_values.where(correct_format),
        format="%d/%m/%Y",
        errors="coerce",
    )

    # Flag invalid dates, excluding empty values already marked missing.
    invalid_dates = date_values.ne("") & parsed_dates.isna()

    for row_index in df.index[invalid_dates]:
        issues[row_index].append("Invalid transaction_date")

        # Convert valid dates to DD/MM/YYYY.
    valid_dates = parsed_dates.notna()

    df.loc[valid_dates, "transaction_date"] = (
        parsed_dates.loc[valid_dates].dt.strftime("%d/%m/%Y")
    )


    # CHECK FOR DUPLICATES RECORDS
    # Remove surrounding spaces when comparing IDs.
    transaction_ids = df["transaction_id"].str.strip()

    # Find every occurrence of repeated IDs, excluding empty IDs.
    duplicate_ids = (
        transaction_ids.ne("")
        & transaction_ids.duplicated(keep=False)
    )

    for row_index in df.index[duplicate_ids]:
        issues[row_index].append("Duplicate transaction_id")


    # CHECK FOR INVALID TRANSACTION AMOUNT
    amount_values = df["amount"].str.strip()

    # Convert numeric text to numbers; unreadable values become NaN.
    numeric_amounts = pd.to_numeric(
        amount_values,
        errors="coerce",
    )

    # Empty amounts already have a "Missing amount" issue.
    invalid_amounts = (
        amount_values.ne("")
        & (
            numeric_amounts.isna()
            | ~np.isfinite(numeric_amounts)
            | numeric_amounts.le(0)
        )
    )
    # Remove surrounding spaces and convert to lowercase for matching.
    status_values = df["status"].str.strip().str.lower()

    status_mapping = {
        "success": "Success",
        "successful": "Success",
        "failed": "Failed",
        "pending": "Pending",
    }

    standardised_statuses = status_values.map(status_mapping)

    # Flag unknown statuses; empty values already have a missing issue.
    invalid_statuses = (
        status_values.ne("")
        & standardised_statuses.isna()
    )

    for row_index in df.index[invalid_statuses]:
        issues[row_index].append("Invalid status")

    # Replace recognised statuses, preserving unknown values for review.
    valid_statuses = standardised_statuses.notna()

    df.loc[valid_statuses, "status"] = (
        standardised_statuses.loc[valid_statuses]
    )

    for row_index in df.index[invalid_amounts]:
        issues[row_index].append("Invalid amount")

    df["issues"] = [
        "; ".join(row_issues)
        for row_issues in issues
    ]

    passed = df["issues"].eq("")

    df["validation_status"] = passed.map({
        True: "Passed",
        False: "Needs review",
    })

    issue_counts = {}

    for row_issues in issues:
        for issue in row_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

    summary = {
        "total_records": len(df),
        "passed_records": int(passed.sum()),
        "review_records": int((~passed).sum()),
        "issue_counts": issue_counts,
    }

    return df, summary