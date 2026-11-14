import streamlit as st
import pandas as pd
import json
import tempfile
from pathlib import Path

from app import clean_data, clean_column_names, get_data_quality_score, generate_pdf_report
from ai_assistant import build_data_summary, ask_gemini

st.set_page_config(
    page_title="Automated Data Cleaning",
    page_icon="🧹",
    layout="wide"
)

# DATAWISE_PRO_THEME
st.markdown("""
<style>
.stApp {
    background: linear-gradient(145deg, #0b1120 0%, #111827 55%, #172554 100%);
}
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    color: #f8fafc !important;
    letter-spacing: -0.5px;
}
p, label, .stMarkdown {
    color: #dbe4f0;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1e293b, #172554);
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18);
}
[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
}
[data-testid="stMetricValue"] {
    color: #ffffff !important;
}
.stButton > button, .stDownloadButton > button {
    border-radius: 12px;
    border: 1px solid #6366f1;
    background: linear-gradient(100deg, #4f46e5, #7c3aed);
    color: white;
    font-weight: 600;
    min-height: 44px;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: #a5b4fc;
    color: white;
    background: linear-gradient(100deg, #4338ca, #6d28d9);
}
[data-testid="stFileUploader"] {
    background: rgba(30, 41, 59, 0.65);
    border: 1px dashed #818cf8;
    border-radius: 16px;
    padding: 12px;
}
div[data-testid="stExpander"] {
    border: 1px solid #334155;
    border-radius: 14px;
    background: rgba(30, 41, 59, 0.55);
}
[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 16px;
}
hr {
    border-color: #334155;
}
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.8rem 2rem;
    }
}
</style>
""", unsafe_allow_html=True)

st.title("🧹 Automated Data Cleaning System")
st.caption("Clean, validate and analyze your datasets automatically.")







# DATAWISE_HOME_NAV
st.markdown("""
<style>
.block-container {
    width: 100% !important;
    max-width: 100% !important;
    padding-left: 12px !important;
    padding-right: 12px !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
}
h1 { font-size: clamp(22px, 5vw, 36px) !important; }

/* Keep homepage cards in a true 2x2 grid */
.stApp:has(.st-key-nav_dashboard) [data-testid="stHorizontalBlock"]:has(.st-key-nav_dashboard),
.stApp:has(.st-key-nav_pdf) [data-testid="stHorizontalBlock"]:has(.st-key-nav_pdf) {
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 12px !important;
    width: 100% !important;
    box-sizing: border-box !important;
}
.stApp:has(.st-key-nav_dashboard) [data-testid="stHorizontalBlock"]:has(.st-key-nav_dashboard) [data-testid="column"],
.stApp:has(.st-key-nav_pdf) [data-testid="stHorizontalBlock"]:has(.st-key-nav_pdf) [data-testid="column"] {
    width: auto !important;
    min-width: 0 !important;
    max-width: none !important;
    flex: none !important;
    box-sizing: border-box !important;
}
.st-key-nav_dashboard button,
.st-key-nav_cleaning button,
.st-key-nav_pdf button,
.st-key-nav_explore button {
    width: 100% !important;
    height: 150px !important;
    min-height: 150px !important;
    padding: 14px !important;
    border-radius: 18px !important;
    white-space: pre-wrap !important;
    text-align: left !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
    border: 1px solid rgba(255,255,255,.2) !important;
}
.st-key-nav_dashboard button { background: #292044 !important; }
.st-key-nav_cleaning button { background: #173d38 !important; }
.st-key-nav_pdf button { background: #3d2c18 !important; }
.st-key-nav_explore button { background: #25314c !important; }

.st-key-nav_dashboard button p,
.st-key-nav_cleaning button p,
.st-key-nav_pdf button p,
.st-key-nav_explore button p {
    color: white !important;
    font-size: clamp(12px, 3.4vw, 16px) !important;
    line-height: 1.5 !important;
    overflow-wrap: anywhere !important;
    text-align: left !important;
}
@media (min-width: 900px) {
    .st-key-nav_dashboard button,
    .st-key-nav_cleaning button,
    .st-key-nav_pdf button,
    .st-key-nav_explore button {
        height: 175px !important;
        min-height: 175px !important;
        padding: 20px !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.session_state.setdefault("datawise_navigation", "Home")
page = st.session_state["datawise_navigation"]

if page != "Home":
    if st.button("← Home", key="back_to_home"):
        st.session_state["datawise_navigation"] = "Home"
        st.rerun()

if page == "Home":
    st.markdown("## ✨ DATAWISE AI")
    st.markdown("### Smart Data Intelligence")
    st.caption("Choose what you want to do")

    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button("🤖  **Dashboard & AI**  \nAI Assistant and overview",
                     key="nav_dashboard", use_container_width=True):
            st.session_state["datawise_navigation"] = "Dashboard & AI"
            st.rerun()

    with col2:
        if st.button("🧹  **Data Cleaning**  \nClean CSV and Excel files",
                     key="nav_cleaning", use_container_width=True):
            st.session_state["datawise_navigation"] = "Data Cleaning"
            st.rerun()

    col3, col4 = st.columns(2, gap="small")
    with col3:
        if st.button("📄  **PDF Validation**  \nExtract and validate PDF data",
                     key="nav_pdf", use_container_width=True):
            st.session_state["datawise_navigation"] = "PDF Validation"
            st.rerun()

    with col4:
        if st.button("➡️  **Explore**  \nDiscover DATAWISE AI features",
                     key="nav_explore", use_container_width=True):
            st.session_state["datawise_navigation"] = "Explore"
            st.rerun()

elif page == "Dashboard & AI":



    st.markdown("## 🏠 Dashboard")
    st.caption("Your intelligent data workspace")
    # ================= TOP AI ASSISTANT =================

    st.markdown("""
    <style>
    .ai-hero {
        background: linear-gradient(120deg, #111827, #312e81, #6d28d9);
        padding: 25px;
        border-radius: 18px;
        color: white;
        margin: 18px 0;
        border: 1px solid #6366f1;
    }
    .ai-hero h2 { color: white; margin: 10px 0; }
    .ai-hero p { color: #e0e7ff; margin-bottom: 5px; }
    </style>
    <div class="ai-hero">
        <div style="font-size:13px; letter-spacing:2px;">
            ✨ DATAWISE AI · SMART DATA INTELLIGENCE
        </div>
        <h2>Meet Your AI Data Assistant</h2>
        <p>Clean smarter. Discover insights. Ask questions about your data.</p>
    </div>
    """, unsafe_allow_html=True)

    ai_ready = "ai_data_summary" in st.session_state
    st.session_state.setdefault("ai_chat_history_v2", [])

    with st.form("top_ai_search", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            question = st.text_input(
                "Ask AI",
                placeholder="✨ Ask anything about your cleaned data...",
                label_visibility="collapsed",
                disabled=False
            )
        with col2:
            submitted = st.form_submit_button(
                "Ask AI ✨",
                use_container_width=True,
                disabled=False
            )

    if not ai_ready:
        st.caption("💡 Ask about this app or data formats anytime. Upload a file for dataset analysis.")

    if submitted and question.strip():
        history = st.session_state["ai_chat_history_v2"]
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            with st.spinner("✨ AI is analyzing your data..."):
                answer = ask_gemini(
                    question,
                    [],
                    st.session_state.get("ai_data_summary", ""),
                    api_key
                )
            history.append({"role": "user", "content": question})
            history.append({"role": "model", "content": answer})
        except Exception as error:
            st.error(f"AI Assistant error: {error}")

    if st.session_state["ai_chat_history_v2"]:
        with st.expander("💬 AI Conversation History", expanded=True):
            for message in st.session_state["ai_chat_history_v2"][-8:]:
                with st.chat_message(
                    "assistant" if message["role"] == "model" else "user"
                ):
                    st.markdown(message["content"])

    st.divider()



elif page == "Data Cleaning":
    st.markdown("## 🧹 Smart Data Cleaning")
    st.caption("Upload, clean and improve your dataset")
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
                        st.session_state["ai_data_summary"] = build_data_summary(cleaned_df, report)

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


elif page == "PDF Validation":
    st.markdown("## 📄 PDF Validation")
    st.caption("Extract and validate information from PDF documents")
    # ================= PDF VALIDATION MODULE =================

    st.divider()
    st.header("📄 PDF Upload & Data Validation")
    st.caption("Extract and validate email addresses, phone numbers, IDs and amounts from text-based and scanned PDF files using automatic OCR.")

    from pdf_validator import validate_pdf
    import io

    pdf_file = st.file_uploader(
        "Upload PDF for Validation",
        type=["pdf"],
        key="pdf_validation_upload"
    )

    if pdf_file is not None:
        try:
            with tempfile.TemporaryDirectory() as pdf_temp:
                pdf_path = Path(pdf_temp) / pdf_file.name
                pdf_path.write_bytes(pdf_file.getvalue())

                with st.spinner("Reading PDF and running OCR when needed..."):
                    extracted_text, pdf_results = validate_pdf(pdf_path)

            st.success("PDF reading completed!")

            total_items = len(pdf_results)
            valid_items = len(
                pdf_results[pdf_results["Status"] == "Valid Format"]
            ) if total_items else 0
            invalid_items = len(
                pdf_results[pdf_results["Status"] == "Invalid Format"]
            ) if total_items else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Detected Items", total_items)
            col2.metric("Valid Formats", valid_items)
            col3.metric("Invalid Formats", invalid_items)

            st.subheader("📋 PDF Validation Results")

            if not pdf_results.empty:
                st.dataframe(pdf_results, use_container_width=True)

                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    pdf_results.to_excel(
                        writer, index=False, sheet_name="PDF Validation"
                    )

                    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
                    from openpyxl.utils import get_column_letter

                    ws = writer.sheets["PDF Validation"]
                    ws.freeze_panes = "A2"
                    ws.auto_filter.ref = ws.dimensions
                    ws.sheet_view.showGridLines = False

                    header_fill = PatternFill(
                        fill_type="solid", fgColor="172554"
                    )
                    header_font = Font(
                        bold=True, color="FFFFFF", size=11
                    )
                    thin_border = Border(
                        bottom=Side(style="thin", color="D1D5DB")
                    )

                    for cell in ws[1]:
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = Alignment(
                            horizontal="center", vertical="center"
                        )
                        cell.border = thin_border

                    ws.row_dimensions[1].height = 28

                    for column_cells in ws.columns:
                        column_letter = get_column_letter(
                            column_cells[0].column
                        )
                        max_length = max(
                            len(str(cell.value or ""))
                            for cell in column_cells
                        )
                        ws.column_dimensions[column_letter].width = min(
                            max(max_length + 4, 14), 42
                        )

                    for row in ws.iter_rows(min_row=2):
                        for cell in row:
                            cell.alignment = Alignment(
                                vertical="center", wrap_text=True
                            )
                            cell.border = thin_border

                            if cell.column == 4:
                                if cell.value == "Valid Format":
                                    cell.font = Font(
                                        color="15803D", bold=True
                                    )
                                elif cell.value == "Invalid Format":
                                    cell.font = Font(
                                        color="DC2626", bold=True
                                    )
                                else:
                                    cell.font = Font(color="92400E")

                    ws.sheet_properties.pageSetUpPr.fitToPage = True
                    ws.page_setup.fitToWidth = 1
                    ws.page_setup.fitToHeight = 0
                    ws.page_setup.orientation = "landscape"

                st.download_button(
                    "📥 Download PDF Validation Excel",
                    data=excel_buffer.getvalue(),
                    file_name="pdf_validation_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No supported email, phone, amount or labelled ID details found.")

            with st.expander("📖 View Extracted PDF Text"):
                st.text(extracted_text if extracted_text.strip() else
                        "No selectable text found. OCR could not extract text from this scanned PDF.")

        except Exception as error:
            st.error(f"PDF validation failed: {error}")


elif page == "Explore":
    st.markdown("## ✨ Explore DATAWISE AI")
    st.caption("Discover the tools available in your data workspace.")
    st.markdown("""
    - 🤖 **AI Data Assistant:** Ask questions about your data and this app.
    - 🧹 **Smart Data Cleaning:** Handle missing values and duplicates.
    - ✅ **Data Validation:** Check emails, dates and other data fields.
    - 📊 **Data Quality:** Review quality scores and cleaning results.
    - 📄 **PDF Validation:** Extract and validate information from text-based PDFs.
    - 📥 **Reports:** Download supported reports and cleaned files.
    """)
