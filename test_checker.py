from checker.transaction_checker import check_transactions
from datetime import datetime
today = datetime.now().strftime('%d-%m-%Y, %H-%M-%S')
all_data, summary = check_transactions(
    "sample_data/transactions.csv"
)


print("SUMMARY")
print(f"Total records: {summary['total_records']}")
print(f"Passed records: {summary['passed_records']}")
print(f"Records needing review: {summary['review_records']}")

print("\nISSUES FOUND")
for issue, count in summary["issue_counts"].items():
    print(f"{issue}: {count}")

print(all_data.to_string(index=False))
print(summary)