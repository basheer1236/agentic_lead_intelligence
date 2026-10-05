from pathlib import Path

from openpyxl import load_workbook


def main():

    file_path = Path(
        "data/exports/lead_intelligence_test.xlsx"
    )

    if not file_path.exists():
        from app.storage.database import SessionLocal
        from app.export.excel_exporter import ExcelExporter
        db = SessionLocal()
        try:
            exporter = ExcelExporter()
            exporter.export(db, filename="lead_intelligence_test.xlsx")
        finally:
            db.close()

    workbook = load_workbook(
        file_path,
        read_only=True
    )

    expected_sheets = {
        "Lead Intelligence Master",
        "Interior Designer Master",
        "Rug Opportunity Tracker",
    }

    actual_sheets = set(workbook.sheetnames)

    print("Excel file found:", file_path)
    print("\nSheets found:")

    for sheet in workbook.sheetnames:
        print("-", sheet)

    # Validate required sheets
    missing_sheets = expected_sheets - actual_sheets

    if missing_sheets:
        raise AssertionError(
            f"Missing sheets: {missing_sheets}"
        )

    # Validate each sheet has data
    for sheet_name in expected_sheets:

        worksheet = workbook[sheet_name]

        print(
            f"\n{sheet_name}: "
            f"{worksheet.max_row} rows, "
            f"{worksheet.max_column} columns"
        )

        if worksheet.max_row < 1:
            raise AssertionError(
                f"{sheet_name} is empty"
            )

    workbook.close()

    print("\n" + "=" * 50)
    print("EXCEL VALIDATION PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()