# ✨ DATAWISE AI — Smart Data Intelligence

<p align="center">
  <strong>Clean Smarter. Validate Better. Discover Insights.</strong>
</p>

<p align="center">
  An AI-powered data cleaning, validation and intelligence platform built with Python and Streamlit.
</p>

<p align="center">
  <a href="https://automated-data-cleaning-system-cpk29qedltytuajcudcbtz.streamlit.app/">
    🚀 Live Demo
  </a>
  |
  <a href="https://github.com/Jersha9jessi/automated-data-cleaning-system">
    💻 GitHub Repository
  </a>
</p>

---

## 🚀 About the Project

DATAWISE AI is a smart data intelligence platform designed to simplify data preparation and analysis.

It helps users clean datasets, handle missing values, detect duplicates, validate data, generate reports and interact with an AI assistant.

The platform combines automated data processing with AI-powered assistance in one application.

## ✨ Key Features

### 📊 Data Cleaning
- Upload CSV and Excel datasets.
- Automatically clean column names.
- Handle missing values using multiple strategies.
- Detect and remove duplicate records.
- Rename, delete, split and reorder columns.
- Compare original and cleaned datasets.

### 🛡️ Data Validation
- Email validation.
- Phone number validation.
- Date and time validation.
- Numeric column validation.
- Identify invalid and missing values.
- Calculate data quality scores.

### 🤖 AI Data Assistant
- Gemini-powered AI assistant.
- Ask questions about the application.
- Understand dataset summaries.
- Get help with data cleaning and validation.
- Receive guidance about supported file formats.

### 📄 PDF Validation
- Upload text-based PDF documents.
- Extract available PDF text.
- Identify emails, phone numbers, amounts and reference IDs.
- Generate structured validation results.

Note: Scanned-image PDF OCR is not currently included.

### 📥 Reports & Downloads
- Download cleaned CSV files.
- Download Excel files.
- Export JSON results.
- Generate professional PDF reports.
- Review before-and-after data comparisons.

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming |
| Streamlit | Web application |
| Pandas | Data processing |
| OpenPyXL | Excel processing |
| Gemini API | AI assistant |
| PyPDF | PDF text extraction |
| ReportLab | PDF report generation |
| Git & GitHub | Version control |

## 🏗️ Project Structure

```text
automated-data-cleaning-system/
│
├── streamlit_app.py       # Main Streamlit application
├── app.py                 # Data cleaning functions
├── ai_assistant.py        # Gemini AI integration
├── app_knowledge.py       # Application knowledge base
├── pdf_validator.py       # PDF validation
├── test_app.py            # Automated tests
├── requirements.txt       # Python dependencies
├── sample.csv             # Sample dataset
└── README.md               # Project documentation
```

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Jersha9jessi/automated-data-cleaning-system.git
cd automated-data-cleaning-system
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your Gemini API key securely using Streamlit secrets.

Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Never upload your API key or secrets file to GitHub.

Run the application:

```bash
streamlit run streamlit_app.py
```

## 🧪 Testing

Run the automated tests:

```bash
python -m unittest -v
```

## 🌐 Live Application

Try DATAWISE AI:

https://automated-data-cleaning-system-cpk29qedltytuajcudcbtz.streamlit.app/

## 🔒 Data & Privacy

The AI assistant uses dataset summaries for supported dataset-related questions rather than sending the entire dataset.

Do not upload confidential or sensitive business data without appropriate authorization.

## 🛣️ Future Improvements

- OCR support for scanned PDF documents.
- Advanced data visualizations.
- More data validation rules.
- Expanded AI-powered analysis.
- Enhanced dashboard and user experience.
- Additional file format support.

## 👨‍💻 Author

**DATAWISE AI Project**

Python | Data Cleaning | Automation | Data Validation | Generative AI

## 📜 License

MIT License
