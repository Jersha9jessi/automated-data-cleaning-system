import streamlit as st
import pandas as pd
import json
import tempfile
from pathlib import Path

from app import clean_data, clean_column_names, get_data_quality_score, generate_pdf_report

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

    try:
        if uploaded_file.name.lower().endswith(".csv"):
            try:
                preview_df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                preview_df = pd.read_csv(uploaded_file, encoding="latin-1")
        else:
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names

            selected_sheet = st.selectbox(
                "📑 Select Excel Sheet to Clean",
                sheet_names
            )

            uploaded_file.seek(0)
            preview_df = pd.read_excel(
                uploaded_file,
                sheet_name=selected_sheet
            )

        if uploaded_file.name.lower().endswith(".csv"):
            selected_sheet = None

        uploaded_file.seek(0)

        st.subheader("⚙️ Smart Missing Value Handling")
        st.caption("Choose how missing values should be handled in each column.")

        strategies = {}
        custom_values = {}

        options = {
            "Default (Median / Unknown)": "default",
            "Mean": "mean",
            "Median": "median",
            "Mode": "mode",
            "Custom Value": "custom",
            "Keep Empty": "keep_empty"
        }

        for column in preview_df.columns:
            selected = st.selectbox(
                f"Missing value strategy — {column}",
                list(options.keys()),
                key=f"strategy_{column}"
            )

            strategies[column] = options[selected]

            if selected == "Custom Value":
                custom_values[column] = st.text_input(
                    f"Custom value for {column}",
                    key=f"custom_{column}"
                )

        st.subheader("🔁 Smart Duplicate Removal")

        duplicate_mode = st.radio(
            "Choose duplicate removal method",
            ["All Columns", "Selected Columns"],
            horizontal=True
        )

        duplicate_columns = None

        if duplicate_mode == "Selected Columns":
            normalized_preview = clean_column_names(preview_df.copy())
            duplicate_columns = st.multiselect(
                "Select columns to identify duplicates",
                options=list(normalized_preview.columns)
            )

            if not duplicate_columns:
                st.warning("Select at least one column. Otherwise choose All Columns.")

        st.subheader("🛠️ Advanced Column Operations")

        normalized_preview = clean_column_names(preview_df.copy())
        original_columns = list(normalized_preview.columns)

        with st.expander("Open Column Operations"):
            st.write("Rename Columns")
            column_renames = {}

            for column in original_columns:
                new_name = st.text_input(
                    f"Rename: {column}",
                    value=column,
                    key=f"rename_{column}"
                )
                if new_name.strip() and new_name.strip() != column:
                    column_renames[column] = new_name.strip()

            renamed_columns = [
                column_renames.get(col, col)
                for col in original_columns
            ]

            st.write("Delete Columns")
            columns_to_delete = st.multiselect(
                "Select columns to delete",
                options=renamed_columns,
                key="delete_columns"
            )

            remaining_columns = [
                col for col in renamed_columns
                if col not in columns_to_delete
            ]

            st.write("Split a Column")
            split_choice = st.selectbox(
                "Select column to split",
                ["None"] + remaining_columns,
                key="split_choice"
            )

            split_columns = {}
            if split_choice != "None":
                separator = st.text_input(
                    "Split separator (example: comma , or space)",
                    value=",",
                    key="split_separator"
                )
                if separator:
                    split_columns[split_choice] = separator

            final_columns = [
                col for col in remaining_columns
                if col != split_choice
            ]
            if split_choice != "None":
                final_columns.extend([
                    f"{split_choice}_part1",
                    f"{split_choice}_part2"
                ])

            st.write("Reorder Columns")
            column_order = st.multiselect(
                "Choose columns in the desired order",
                options=final_columns,
                default=final_columns,
                key="column_order"
            )

        if st.button("🚀 Clean My Data", type="primary"):
            if duplicate_mode == "Selected Columns" and not duplicate_columns:
                st.error("Please select at least one column for duplicate removal.")
                st.stop()
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_path = Path(temp_dir) / uploaded_file.name
                    input_path.write_bytes(uploaded_file.getvalue())

                    with st.spinner("Cleaning your data..."):
                        clean_data(
                            str(input_path),
                            strategies,
                            custom_values,
                            duplicate_columns,
                            selected_sheet,
                            column_renames=column_renames,
                            columns_to_delete=columns_to_delete,
                            column_order=column_order,
                            split_columns=split_columns
                        )

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

                    col1.metric("Original Rows", report["original_rows"])
                    col2.metric("Cleaned Rows", report["cleaned_rows"])
                    col3.metric("Duplicates Removed", report["duplicates_removed"])
                    col4.metric("Invalid Emails", report["invalid_emails"])

                    col5, col6 = st.columns(2)
                    col5.metric("Missing Values Before", report["missing_values_before"])
                    col6.metric("Missing Values After", report["missing_values_after"])

                    quality_score = get_data_quality_score(cleaned_df)
                    st.metric("🏆 Data Quality Score", f"{quality_score}%")

                    st.progress(quality_score / 100)

                    st.subheader("📋 Cleaned Data Preview")
                    st.dataframe(cleaned_df, use_container_width=True)

                    st.subheader("📈 Data Quality Reports")

                    before_report = pd.read_excel(
                        output_excel, sheet_name="Before Quality"
                    )
                    after_report = pd.read_excel(
                        output_excel, sheet_name="After Quality"
                    )
                    comparison = pd.read_excel(
                        output_excel, sheet_name="Comparison"
                    )
                    validation_report = pd.read_excel(
                        output_excel, sheet_name="Validation Issues"
                    )

                    tab1, tab2, tab3, tab4 = st.tabs([
                        "Before Cleaning",
                        "After Cleaning",
                        "Comparison",
                        "Validation Issues"
                    ])

                    with tab1:
                        st.dataframe(before_report, use_container_width=True)

                    with tab2:
                        st.dataframe(after_report, use_container_width=True)

                    with tab3:
                        st.dataframe(comparison, use_container_width=True)

                    with tab4:
                        st.metric("Total Validation Issues", len(validation_report))
                        st.dataframe(validation_report, use_container_width=True)

                    output_pdf = input_path.with_name(
                        input_path.stem + "_report.pdf"
                    )

                    generate_pdf_report(
                        report,
                        quality_score,
                        output_pdf,
                        validation_report
                    )

                    st.subheader("📥 Download Reports")

                    st.download_button(
                        "📄 Download Professional PDF Report",
                        data=output_pdf.read_bytes(),
                        file_name="professional_cleaning_report.pdf",
                        mime="application/pdf"
                    )


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
                    st.json(report.get("unresolved_missing_columns", {}))

            except Exception as error:
                st.error(f"An error occurred: {error}")

    except Exception as error:
        st.error(f"Could not read the uploaded file: {error}")

else:
    st.info("Upload a CSV or XLSX file to get started.")
