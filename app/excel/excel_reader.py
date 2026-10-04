from pathlib import Path

import pandas as pd


class ExcelReader:
    REQUIRED_COLUMNS = {
        "TestCaseID",
        "TestCaseName",
        "Description",
        "StepNo",
        "Action",
        "TestData",
        "ExpectedResult",
    }

    def read(self, file_path: str) -> pd.DataFrame:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Excel file not found: {file_path}"
            )

        if path.suffix.lower() not in [".xlsx", ".xls"]:
            raise ValueError(
                "Input file must be an Excel file (.xlsx or .xls)"
            )

        dataframe = pd.read_excel(
            path,
            sheet_name="TestCases",
            engine="openpyxl",
        )

        dataframe.columns = [
            str(column).strip()
            for column in dataframe.columns
        ]

        missing_columns = (
            self.REQUIRED_COLUMNS - set(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "Missing required Excel columns: "
                + ", ".join(sorted(missing_columns))
            )

        dataframe = dataframe.dropna(
            how="all"
        )

        return dataframe