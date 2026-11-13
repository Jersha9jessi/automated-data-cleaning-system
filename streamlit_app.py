
import streamlit as st
import pandas as pd
import json
import tempfile
from pathlib import Path

from app import clean_data


st.set_page_config(
    page_title="Automated Data Cleaning",
    page_icon="🧹",
    layout="wide"
)

st.title("🧹 Automated Data Cleaning System")
st.caption("Clean, validate and analyze your datasets automatically.")

uploaded_file = st.file_uploader(
    "Upload your CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    st.info(f"Selected file: {uploaded_file.name}")

    if st.button("🚀 Clean My Data", type="primary"):

        try:
            with tempfile.TemporaryDirectory() as temp_dir:

                input_path = Path(temp_dir) / uploaded_file.name

                input_path.write_bytes(uploaded_file.getvalue())

                with st.spinner("Cleaning your data..."):
                    clean_data(str(input_path))

                output_excel = input_path.with_name(
                    input_path.stem + "_cleaned.xlsx"
                )

                output_json = input_path.with_name(
                    input_path.stem + "_report.json"
                )

                cleaned_df = pd.read_excel(
                    output_excel,
                    sheet_name="Cleaned Data"
                )

                with open(output_json, encoding="utf-8") as file:
                    report = json.load(file)

                st.success("Data cleaning completed successfully!")

                st.subheader("📊 Cleaning Summary")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Original Rows",
                    report["original_rows"]
                )

                col2.metric(
                    "Cleaned Rows",
                    report["cleaned_rows"]
                )

                col3.metric(
                    "Duplicates Removed",
                    report["duplicates_removed"]
                )

                col4.metric(
                    "Invalid Emails",
                    report["invalid_emails"]
                )

                st.subheader("📋 Cleaned Data Preview")
                st.dataframe(
                    cleaned_df,
                    use_container_width=True
                )

                st.subheader("📈 Data Quality Reports")

                before_report = pd.read_excel(
                    output_excel,
                    sheet_name="Before Quality"
                )

                after_report = pd.read_excel(
                    output_excel,
                    sheet_name="After Quality"
                )

                tab1, tab2, tab3 = st.tabs([
                    "Before Cleaning",
                    "After Cleaning",
                    "Comparison"
                ])

                with tab1:
                    st.dataframe(
                        before_report,
                        use_container_width=True
                    )

                with tab2:
                    st.dataframe(
                        after_report,
                        use_container_width=True
                    )

                with tab3:
                    comparison = pd.read_excel(
                        output_excel,
                        sheet_name="Comparison"
                    )
                    st.dataframe(
                        comparison,
                        use_container_width=True
                    )

                st.subheader("📥 Download Reports")

                st.download_button(
                    "Download Cleaned Excel",
                    data=output_excel.read_bytes(),
                    file_name="cleaned_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                st.download_button(
                    "Download JSON Report",
                    data=output_json.read_bytes(),
                    file_name="cleaning_report.json",
                    mime="application/json"
                )

                st.subheader("⚠️ Unresolved Missing Values")
                st.json(
                    report.get("unresolved_missing_columns", {})
                )

        except Exception as error:
            st.error(f"An error occurred: {error}")

else:
    st.info("Upload a CSV or XLSX file to get started.")
