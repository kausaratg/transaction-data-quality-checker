from django.shortcuts import render

import base64

import pandas as pd

from .transaction_checker import check_transactions


from pathlib import Path

from django.conf import settings
from django.http import FileResponse


def encode_csv(dataframe):
    csv_text = dataframe.to_csv(index=False)

    # Include a UTF-8 BOM so Excel can recognise the encoding.
    csv_bytes = csv_text.encode("utf-8-sig")

    return base64.b64encode(csv_bytes).decode("ascii")


def upload_transactions(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("transaction_file")

        if uploaded_file is None:
            return render(
                request,
                "checker/upload.html",
                {"error": "Please select a CSV file."},
            )

        # Keep this first version suitable for small files.
        if uploaded_file.size > 2 * 1024 * 1024:
            return render(
                request,
                "checker/upload.html",
                {"error": "Please upload a file smaller than 2 MB."},
            )

        try:
           all_data, summary = check_transactions(uploaded_file)
        except (
            ValueError,
            UnicodeDecodeError,
            pd.errors.ParserError,
        ):
            return render(
                request,
                "checker/upload.html",
                {
                    "error": (
                        "Could not read the file. Upload a UTF-8 CSV "
                        "with transaction_id, amount, "
                        "transaction_date, and status columns."
                    )
                },
            )

        # Select flagged rows only for display in the report.
        review_data = all_data.loc[
            all_data["validation_status"].eq("Needs review")
        ]

        context = {
            "filename": uploaded_file.name,
            "summary": summary,
            "review_columns": review_data.columns.tolist(),
            "review_rows": review_data.values.tolist(),
            "all_csv": encode_csv(all_data),
        }

        return render(request, "checker/report.html", context)

    return render(request, "checker/upload.html")

def download_sample(request):
    file_path = (
        Path(settings.BASE_DIR)
        / "sample_data"
        / "transactions.csv"
    )

    return FileResponse(
        file_path.open("rb"),
        as_attachment=True,
        filename="sample_transactions.csv",
        content_type="text/csv",
    )