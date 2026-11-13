import json
import urllib.request
import urllib.error
from app_knowledge import APP_KNOWLEDGE


MODEL = "gemini-3.1-flash-lite"


def build_data_summary(df, report=None):
    summary = {
        "rows": int(df.shape[0]),
        "columns_count": int(df.shape[1]),
        "columns": [
            {
                "name": str(col),
                "type": str(df[col].dtype),
                "missing_values": int(df[col].isna().sum())
            }
            for col in df.columns[:50]
        ],
        "duplicate_rows": int(df.duplicated().sum()),
    }

    numeric = df.select_dtypes(include="number")
    if not numeric.empty:
        summary["numeric_statistics"] = (
            numeric.describe().round(2).to_dict()
        )

    if report:
        summary["cleaning_report"] = {
            key: report.get(key)
            for key in [
                "original_rows",
                "cleaned_rows",
                "duplicates_removed",
                "invalid_emails",
                "missing_values_before",
                "missing_values_after"
            ]
            if key in report
        }

    return json.dumps(summary, ensure_ascii=False, default=str)


def ask_gemini(question, history, data_summary, api_key):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent?key={api_key}"
    )

    contents = []
    for item in history[-6:]:
        contents.append({
            "role": item["role"],
            "parts": [{"text": item["content"]}]
        })

    contents.append({
        "role": "user",
        "parts": [{"text": question}]
    })

    payload = {
        "systemInstruction": {
            "parts": [{
                "text": (
                    "You are DATAWISE AI, the official expert assistant for this app. " + APP_KNOWLEDGE + " "
                    "Answer general app questions even without an uploaded file. " "For dataset questions, use the dataset summary when available. "
                    "summary only. Do not invent data or claim to see "
                    "the original file. If information is unavailable, "
                    "say so. Dataset summary: " + data_summary
                )
            }]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1200
        }
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Gemini API error ({error.code}): {details[:500]}"
        ) from error

    except Exception as error:
        raise RuntimeError(
            f"AI connection failed: {type(error).__name__}: {error}"
        ) from error
