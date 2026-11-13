import unittest
import pandas as pd

from app import (
    clean_column_names,
    fill_missing_values,
    validate_emails
)


class TestDataCleaning(unittest.TestCase):

    def test_clean_column_names(self):
        df = pd.DataFrame(
            [[1, 2, 3]],
            columns=["First Name", "Email Address", "First Name"]
        )

        result = clean_column_names(df)

        self.assertEqual(
            list(result.columns),
            ["first_name", "email_address", "first_name_2"]
        )

    def test_fill_numeric_missing_values(self):
        df = pd.DataFrame({
            "age": [20, None, 40]
        })

        result = fill_missing_values(df)

        self.assertEqual(result["age"].isna().sum(), 0)
        self.assertEqual(result["age"].iloc[1], 30)

    def test_fill_text_missing_values(self):
        df = pd.DataFrame({
            "name": ["Ravi", None, "Sita"]
        })

        result = fill_missing_values(df)

        self.assertEqual(result["name"].iloc[1], "Unknown")

    def test_all_null_numeric_column(self):
        df = pd.DataFrame({
"score": pd.Series([None, None, None], dtype="float64")        })

        result = fill_missing_values(df)

        self.assertEqual(result["score"].isna().sum(), 3)

    def test_invalid_email_detection(self):
        df = pd.DataFrame({
            "email": ["valid@gmail.com", "wrong-email"]
        })

        result = validate_emails(df)

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result.iloc[0]["Invalid Email"],
            "wrong-email"
        )


if __name__ == "__main__":
    unittest.main()
