from flask import Flask, request, redirect, url_for, jsonify, render_template_string
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from pypdf import PdfReader

# Optional OCR dependencies.
# Text PDFs work with pypdf alone; scanned/image PDFs use PyMuPDF + Tesseract OCR.
try:
    import pymupdf as fitz  # Preferred PyMuPDF API
except Exception:
    try:
        import fitz  # Backward-compatible fallback
    except Exception:
        fitz = None

try:
    import pytesseract
except Exception:
    pytesseract = None

try:
    from PIL import Image
except Exception:
    Image = None

import os
import re
import html
from datetime import datetime


# ============================================================
# CAPABILITY EVIDENCE OS
# SAP HACKFEST 2026
# V3 - DYNAMIC RESUME INTELLIGENCE PROTOTYPE
# ============================================================

app = Flask(__name__)
app.secret_key = "capability-evidence-os-demo-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# ============================================================
# CAPABILITY INTELLIGENCE RULES
# ============================================================

CAPABILITY_RULES = [
    {
        "name": "Budgeting",
        "keywords": [
            "budget",
            "budgeting",
            "budget preparation",
            "budget planning",
            "forecasting",
            "variance analysis",
            "cost planning"
        ]
    },
    {
        "name": "Documentation",
        "keywords": [
            "documentation",
            "documented",
            "record keeping",
            "records management",
            "maintained records",
            "maintained documentation",
            "invoices",
            "invoicing",
            "reports"
        ]
    },
    {
        "name": "Coordination",
        "keywords": [
            "coordination",
            "coordinated",
            "coordinating",
            "stakeholder",
            "stakeholders",
            "cross-functional",
            "liaison",
            "team coordination"
        ]
    },
    {
        "name": "Excel",
        "keywords": [
            "excel",
            "microsoft excel",
            "spreadsheet",
            "spreadsheets"
        ]
    },
    {
        "name": "Advanced Excel",
        "keywords": [
            "advanced excel",
            "pivot table",
            "pivot tables",
            "vlookup",
            "xlookup",
            "hlookup",
            "index match",
            "power query",
            "power pivot",
            "excel macros",
            "macro",
            "macros",
            "conditional formatting",
            "data validation"
        ]
    },
    {
        "name": "Financial Reporting",
        "keywords": [
            "financial reporting",
            "financial reports",
            "financial statements",
            "financial statement",
            "monthly accounts",
            "month end",
            "month-end",
            "profit and loss",
            "p&l",
            "balance sheet",
            "cash flow",
            "cashflow"
        ]
    },
    {
        "name": "Data Analysis",
        "keywords": [
            "data analysis",
            "data analytics",
            "data analyst",
            "analysed data",
            "analyzed data",
            "data interpretation",
            "business analysis",
            "trend analysis",
            "dashboard"
        ]
    },
    {
        "name": "Accounting",
        "keywords": [
            "accounting",
            "accountancy",
            "bookkeeping",
            "book keeping",
            "accounts payable",
            "accounts receivable",
            "journal entries",
            "general ledger",
            "ledger",
            "bank reconciliation",
            "reconciliation"
        ]
    },
    {
        "name": "SQL",
        "keywords": [
            "sql",
            "mysql",
            "postgresql",
            "postgres",
            "sql server"
        ]
    },
    {
        "name": "Python",
        "keywords": [
            "python",
            "pandas",
            "numpy",
            "python programming"
        ]
    },
    {
        "name": "Java",
        "keywords": [
            "java",
            "java programming",
            "core java"
        ]
    },
    {
        "name": "C Programming",
        "keywords": [
            "c programming",
            "programming in c",
            "c language"
        ]
    },
    {
        "name": "SAP",
        "keywords": [
            "sap",
            "s/4hana",
            "s4hana",
            "sap erp",
            "sap fico",
            "sap fi",
            "sap mm"
        ]
    },
    {
        "name": "Power BI",
        "keywords": [
            "power bi",
            "powerbi"
        ]
    },
    {
        "name": "Tableau",
        "keywords": [
            "tableau"
        ]
    },
    {
        "name": "Project Management",
        "keywords": [
            "project management",
            "project coordination",
            "project planning",
            "agile",
            "scrum",
            "project execution"
        ]
    },
    {
        "name": "Communication",
        "keywords": [
            "communication",
            "presentation",
            "presentations",
            "client communication",
            "written communication",
            "verbal communication"
        ]
    },
    {
        "name": "Problem Solving",
        "keywords": [
            "problem solving",
            "problem-solving",
            "analytical thinking",
            "critical thinking",
            "troubleshooting"
        ]
    },
]


# ============================================================
# JOB REQUIREMENTS
# ============================================================

JOB_REQUIREMENTS = {
    "Software / Application Developer": ["Python", "SQL", "Problem Solving", "Project Management", "Communication"],
    "Data Analyst": ["Data Analysis", "SQL", "Excel", "Power BI", "Communication"],
    "Finance / Accounting Analyst": ["Accounting", "Financial Reporting", "Budgeting", "Excel", "Data Analysis"],
    "Marketing / Business Development": ["Communication", "Project Management", "Data Analysis", "Problem Solving"],
    "HR / People Operations": ["Communication", "Project Management", "Documentation", "Problem Solving"],
    "Project / Operations Coordinator": ["Project Management", "Communication", "Problem Solving", "Documentation"],
    "Technology / Systems Engineer": ["Python", "SQL", "Problem Solving", "Communication", "Project Management"],
    "General / Entry-Level Professional": ["Communication", "Problem Solving", "Documentation", "Project Management"]
}

ROLE_SIGNALS = {
    "Software / Application Developer": ["software developer", "software engineer", "developer", "programming", "python", "java", "javascript", "flask", "django", "react", "node.js", "github", "git", "api", "web development"],
    "Data Analyst": ["data analyst", "data analysis", "data analytics", "statistics", "power bi", "tableau", "pandas", "numpy", "sql", "dashboard", "data science"],
    "Finance / Accounting Analyst": ["accountant", "accounting", "finance analyst", "financial analyst", "bookkeeping", "gst", "taxation", "audit", "accounts payable", "accounts receivable", "financial reporting", "budgeting", "ledger"],
    "Marketing / Business Development": ["marketing", "seo", "sem", "social media", "content marketing", "campaign", "branding", "business development", "sales"],
    "HR / People Operations": ["human resources", "hr", "recruitment", "talent acquisition", "payroll", "employee relations", "onboarding", "people operations"],
    "Project / Operations Coordinator": ["project manager", "project management", "project coordinator", "operations", "supply chain", "logistics", "procurement", "inventory", "warehouse", "agile", "scrum"],
    "Technology / Systems Engineer": ["system administrator", "systems engineer", "network engineer", "devops", "cloud", "aws", "azure", "docker", "kubernetes", "cyber security", "cybersecurity", "networking"]
}


# ============================================================
# GLOBAL DEMO STATE
# ============================================================

STATE = {
    "candidate": None,
    "capabilities": [],
    "raw_text": "",
    "filename": "",
    "uploaded_at": None,
    "job": {
        "title": "General / Entry-Level Professional",
        "requirements": JOB_REQUIREMENTS["General / Entry-Level Professional"].copy(),
        "confidence": 0,
        "reason": "Waiting for resume analysis."
    },
    "verification": {
        "started": False,
        "completed": False,
        "capability": None,
        "evidence": None,
        "started_at": None,
        "completed_at": None,
    },
    "review": {}
}



# ============================================================
# HELPERS
# ============================================================

def esc(value):
    return html.escape(str(value or ""))


def clean_text(text):
    text = text or ""
    text = text.replace("\x00", " ")
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_line(line):
    line = re.sub(r"\s+", " ", line or "").strip()
    return line


def get_lines(text):
    lines = []

    for line in (text or "").splitlines():
        line = clean_line(line)

        if line:
            lines.append(line)

    return lines


def normalize_for_match(text):
    text = (text or "").lower()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text


def keyword_in_text(text, keyword):
    text = normalize_for_match(text)
    keyword = normalize_for_match(keyword)

    if not keyword:
        return False

    return keyword in text


def find_email(text):
    match = re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        text or "",
        re.IGNORECASE
    )

    return match.group(0) if match else "Not detected"


def find_phone(text):
    patterns = [
        r"(?<!\d)(?:\+91[\s.-]?)?[6-9]\d{9}(?!\d)",
        r"(?<!\d)\+?\d[\d\s().-]{8,14}\d(?!\d)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text or "")

        if match:
            value = re.sub(r"\s+", " ", match.group(0)).strip()
            return value

    return "Not detected"


def looks_like_name(line):
    if not line:
        return False

    low = line.lower().strip()

    blocked = [
        "resume",
        "curriculum vitae",
        "curriculum",
        "cv",
        "profile",
        "objective",
        "summary",
        "career objective",
        "contact",
        "email",
        "phone",
        "mobile",
        "address",
        "linkedin",
        "github",
        "www.",
        "education",
        "experience",
        "skills",
        "projects",
        "certifications",
        "achievements",
        "professional summary"
    ]

    if any(item in low for item in blocked):
        return False

    if "@" in line:
        return False

    if re.search(r"\d", line):
        return False

    if len(line) < 3 or len(line) > 60:
        return False

    words = line.split()

    if len(words) < 2 or len(words) > 6:
        return False

    allowed = 0

    for word in words:
        cleaned = re.sub(r"[^A-Za-z.'-]", "", word)

        if cleaned and re.fullmatch(r"[A-Za-z.'-]+", cleaned):
            allowed += 1

    return allowed >= len(words) - 1


def extract_name(lines):
    for line in lines[:25]:
        if looks_like_name(line):
            return line

    return "Candidate"


def extract_education(text, lines):
    degree_patterns = [
        r"\bB\.?\s*Tech\b",
        r"\bB\.?\s*E\b",
        r"\bM\.?\s*Tech\b",
        r"\bM\.?\s*E\b",
        r"\bB\.?\s*Sc\b",
        r"\bM\.?\s*Sc\b",
        r"\bB\.?\s*Com\b",
        r"\bB\.?\s*Commerce\b",
        r"\bM\.?\s*Com\b",
        r"\bB\.?\s*BA\b",
        r"\bM\.?\s*BA\b",
        r"\bMBA\b",
        r"\bMCA\b",
        r"\bBCA\b",
        r"\bBBA\b",
        r"\bPh\.?D\b",
        r"\bBachelor(?:'s)?\b",
        r"\bMaster(?:'s)?\b",
        r"\bDiploma\b"
    ]

    matches = []

    for line in lines:
        for pattern in degree_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                if line not in matches:
                    matches.append(line)
                break

    if matches:
        return " • ".join(matches[:3])

    return "Not detected"


def extract_role(text, lines):
    role_patterns = [
        "software engineer",
        "software developer",
        "full stack developer",
        "frontend developer",
        "backend developer",
        "web developer",
        "data analyst",
        "data scientist",
        "business analyst",
        "financial analyst",
        "accountant",
        "senior accountant",
        "junior accountant",
        "finance analyst",
        "finance associate",
        "financial associate",
        "hr executive",
        "hr manager",
        "human resources",
        "project manager",
        "project coordinator",
        "business development executive",
        "business development associate",
        "marketing executive",
        "marketing associate",
        "sales executive",
        "sales associate",
        "system administrator",
        "network engineer",
        "devops engineer",
        "cloud engineer",
        "cyber security analyst",
        "cybersecurity analyst",
        "ui ux designer",
        "ui/ux designer",
        "graphic designer",
        "product manager",
        "intern",
        "developer",
        "engineer",
        "analyst",
        "manager",
        "coordinator",
        "consultant"
    ]

    lower_text = normalize_for_match(text)

    for role in role_patterns:
        if role in lower_text:
            return role.title()

    for line in lines:
        lower = line.lower()

        if any(
            marker in lower
            for marker in [
                "experience",
                "designation",
                "position",
                "role"
            ]
        ):
            continue

        if 2 <= len(line.split()) <= 6:
            for role in role_patterns:
                if role in lower:
                    return line

    return "Not detected"


def extract_experience(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+experience"
    ]

    for pattern in patterns:
        match = re.search(pattern, text or "", re.IGNORECASE)

        if match:
            return match.group(1) + " Years"

    return "Not detected"


def extract_career_gap(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)[\s-]*(?:career\s*)?(?:gap|break)",
        r"(?:career\s+gap|career\s+break|employment\s+gap|work\s+gap)\s*(?:of|:|-)?\s*(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)",
        r"gap\s+of\s+(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)",
        r"(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)\s+(?:employment|work)\s+gap"
    ]

    for pattern in patterns:
        match = re.search(pattern, text or "", re.IGNORECASE)

        if match:
            return match.group(1) + " Years"

    return "Not detected"


def extract_goal(text, lines):
    goal_keywords = [
        "career objective",
        "objective",
        "career goal",
        "professional goal",
        "seeking",
        "looking for",
        "aim to",
        "return to workforce",
        "returning to work"
    ]

    for index, line in enumerate(lines):
        lower = line.lower()

        if any(keyword in lower for keyword in goal_keywords):
            if ":" in line:
                value = line.split(":", 1)[1].strip()

                if len(value) > 10:
                    return value

            if index + 1 < len(lines):
                next_line = lines[index + 1]

                if len(next_line) > 10:
                    return next_line

    return "Not detected"


def extract_summary(text, lines):
    summary_markers = [
        "professional summary",
        "profile summary",
        "summary",
        "about me",
        "career objective",
        "objective"
    ]

    for index, line in enumerate(lines):
        low = line.lower().strip()

        if low in summary_markers:
            collected = []

            for next_line in lines[index + 1:index + 4]:
                if len(next_line) > 20:
                    collected.append(next_line)

            if collected:
                return " ".join(collected)[:500]

    return "No summary detected"


def extract_skills(text):
    found = []

    skill_keywords = [
        "Python",
        "Java",
        "C Programming",
        "SQL",
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Node.js",
        "Flask",
        "Django",
        "Git",
        "GitHub",
        "Excel",
        "Advanced Excel",
        "Power BI",
        "Tableau",
        "SAP",
        "Accounting",
        "Financial Reporting",
        "Budgeting",
        "Data Analysis",
        "Communication",
        "Project Management",
        "Problem Solving",
        "Leadership",
        "Team Management",
        "Machine Learning",
        "Data Science",
        "Cloud Computing",
        "AWS",
        "Azure",
        "Docker",
        "Kubernetes"
    ]

    lower_text = normalize_for_match(text)

    for skill in skill_keywords:
        if normalize_for_match(skill) in lower_text:
            if skill not in found:
                found.append(skill)

    return found


def find_evidence_snippets(text, keywords):
    lines = get_lines(text)
    snippets = []
    matched_keywords = []

    for line in lines:
        low_line = normalize_for_match(line)

        matches = []

        for keyword in keywords:
            if normalize_for_match(keyword) in low_line:
                matches.append(keyword)

        if matches:
            for keyword in matches:
                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)

            if line not in snippets:
                snippets.append(line[:260])

        if len(snippets) >= 3:
            break

    return snippets, matched_keywords


def capability_status(snippets, matched_keywords):
    if not snippets:
        return "Unverified"

    if len(snippets) >= 2 or len(matched_keywords) >= 2:
        return "Strong"

    return "Partial"


def build_capabilities(text):
    capabilities = []

    for rule in CAPABILITY_RULES:
        snippets, matched_keywords = find_evidence_snippets(
            text,
            rule["keywords"]
        )

        status = capability_status(
            snippets,
            matched_keywords
        )

        capabilities.append({
            "name": rule["name"],
            "status": status,
            "evidence": snippets,
            "matched_keywords": matched_keywords
        })

    return capabilities


def build_candidate(text, filename):
    lines = get_lines(text)

    candidate = {
        "name": extract_name(lines),
        "email": find_email(text),
        "phone": find_phone(text),
        "role": extract_role(text, lines),
        "education": extract_education(text, lines),
        "experience": extract_experience(text),
        "career_gap": extract_career_gap(text),
        "goal": extract_goal(text, lines),
        "summary": extract_summary(text, lines),
        "skills": extract_skills(text),
        "filename": filename
    }

    return candidate


def capability_by_name(name):
    for capability in STATE["capabilities"]:
        if capability["name"] == name:
            return capability

    return None


def infer_job_profile(candidate, text, capabilities):
    source = normalize_for_match(" ".join([text or "", candidate.get("role", "") if candidate else "", " ".join(candidate.get("skills", [])) if candidate else ""]))
    scores = {role: sum(1 for signal in signals if normalize_for_match(signal) in source) for role, signals in ROLE_SIGNALS.items()}
    best_role = max(scores, key=scores.get) if scores else "General / Entry-Level Professional"
    best_score = scores.get(best_role, 0)
    explicit_map = {
        "software developer": "Software / Application Developer", "software engineer": "Software / Application Developer",
        "full stack developer": "Software / Application Developer", "frontend developer": "Software / Application Developer",
        "backend developer": "Software / Application Developer", "web developer": "Software / Application Developer",
        "data analyst": "Data Analyst", "data scientist": "Data Analyst",
        "financial analyst": "Finance / Accounting Analyst", "finance analyst": "Finance / Accounting Analyst", "accountant": "Finance / Accounting Analyst",
        "marketing executive": "Marketing / Business Development", "marketing associate": "Marketing / Business Development",
        "business development executive": "Marketing / Business Development", "hr executive": "HR / People Operations", "hr manager": "HR / People Operations",
        "human resources": "HR / People Operations", "project manager": "Project / Operations Coordinator", "project coordinator": "Project / Operations Coordinator",
        "system administrator": "Technology / Systems Engineer", "network engineer": "Technology / Systems Engineer", "devops engineer": "Technology / Systems Engineer",
        "cloud engineer": "Technology / Systems Engineer", "cyber security analyst": "Technology / Systems Engineer", "cybersecurity analyst": "Technology / Systems Engineer"
    }
    extracted_role = normalize_for_match(candidate.get("role", "") if candidate else "")
    role = explicit_map.get(extracted_role, best_role if best_score > 0 else "General / Entry-Level Professional")
    requirements = JOB_REQUIREMENTS[role].copy()
    return {"title": role, "requirements": requirements, "confidence": min(100, 45 + best_score * 10), "reason": "Detected from resume role, skills, projects and experience evidence."}


def required_capabilities():
    return (STATE.get("job") or {}).get("requirements") or JOB_REQUIREMENTS["General / Entry-Level Professional"]


def capability_match_status(status):
    if status in ["Strong", "Verified"]:
        return "MATCH"

    if status == "Partial":
        return "PARTIAL"

    return "UNVERIFIED"


def evidence_health():
    if not STATE["capabilities"]:
        return 0

    verified = 0

    for capability in STATE["capabilities"]:
        if capability["status"] in ["Strong", "Verified"]:
            verified += 1

    return round((verified / len(STATE["capabilities"])) * 100)


def get_gaps():
    gaps = []

    for requirement in required_capabilities():
        capability = capability_by_name(requirement)

        if capability:
            if capability["status"] not in ["Strong", "Verified"]:
                gaps.append(capability)

    return gaps


def next_verification_capability():
    gaps = get_gaps()

    for gap in gaps:
        if gap["status"] == "Unverified":
            return gap

    for gap in gaps:
        if gap["status"] == "Partial":
            return gap

    return None


def reset_state():
    STATE["candidate"] = None
    STATE["capabilities"] = []
    STATE["raw_text"] = ""
    STATE["filename"] = ""
    STATE["uploaded_at"] = None

    STATE["verification"] = {
        "started": False,
        "completed": False,
        "capability": None,
        "evidence": None,
        "started_at": None,
        "completed_at": None,
    }

    STATE["review"] = {}


def _configure_tesseract():
    """Configure Tesseract robustly on Windows and verify it works."""

    if pytesseract is None:
        return False

    import shutil

    candidates = [
        os.environ.get("TESSERACT_CMD", ""),
        shutil.which("tesseract") or "",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    ]

    for candidate in candidates:
        if not candidate:
            continue

        candidate = os.path.expandvars(candidate)

        if not os.path.isfile(candidate):
            continue

        try:
            pytesseract.pytesseract.tesseract_cmd = candidate
            version = pytesseract.get_tesseract_version()
            print(f"Tesseract OCR ready: {version}")
            return True
        except Exception as error:
            print(f"Tesseract check failed for {candidate}: {error}")
            continue

    return False


def extract_pdf_text(filepath):
    """
    Extract text from a normal PDF first.
    If the PDF is scanned/image-only, automatically fall back to OCR.
    Returns a tuple: (text, extraction_mode, ocr_message).
    """

    reader = PdfReader(filepath)
    pages = []

    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""

            if page_text.strip():
                pages.append(page_text)
        except Exception:
            continue

    normal_text = clean_text("\n".join(pages))

    # Normal/selectable-text PDF. No OCR is needed.
    if normal_text.strip():
        return normal_text, "PDF TEXT", ""

    # --------------------------------------------------------
    # OCR FALLBACK FOR SCANNED / IMAGE-ONLY PDFs
    # --------------------------------------------------------

    if fitz is None:
        return "", "OCR UNAVAILABLE", (
            "Scanned PDF detected, but PyMuPDF is not installed. "
            "Run: pip install pymupdf"
        )

    if pytesseract is None or Image is None:
        return "", "OCR UNAVAILABLE", (
            "Scanned PDF detected, but OCR Python packages are missing. "
            "Run: pip install pytesseract pillow"
        )

    if not _configure_tesseract():
        return "", "OCR UNAVAILABLE", (
            "Scanned PDF detected, but Tesseract OCR is not installed. "
            "Install Tesseract OCR and restart the app."
        )

    ocr_pages = []

    try:
        document = fitz.open(filepath)

        for page_number, pdf_page in enumerate(document, start=1):
            try:
                # 2x rendering gives Tesseract enough resolution for most
                # college/resume scans while keeping the prototype responsive.
                matrix = fitz.Matrix(2.0, 2.0)
                pix = pdf_page.get_pixmap(
                    matrix=matrix,
                    alpha=False
                )

                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )

                page_text = pytesseract.image_to_string(
                    image,
                    config="--oem 3 --psm 6"
                ) or ""

                # Some resumes have complex columns/layouts. If the first
                # OCR pass returns almost nothing, retry with automatic layout.
                if len(re.sub(r"\s+", "", page_text)) < 25:
                    retry_text = pytesseract.image_to_string(
                        image,
                        config="--oem 3 --psm 3"
                    ) or ""
                    if len(re.sub(r"\s+", "", retry_text)) > len(
                        re.sub(r"\s+", "", page_text)
                    ):
                        page_text = retry_text

                if page_text.strip():
                    ocr_pages.append(
                        f"[Page {page_number}]\n{page_text}"
                    )

            except Exception:
                continue

        document.close()

    except Exception as error:
        return "", "OCR ERROR", (
            "OCR could not process this scanned PDF: "
            + str(error)[:250]
        )

    ocr_text = clean_text("\n".join(ocr_pages))

    if ocr_text.strip():
        return ocr_text, "OCR", ""

    return "", "OCR EMPTY", (
        "OCR ran, but no readable text was detected in the scanned pages."
    )


# ============================================================
# UI HELPERS
# ============================================================

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>{{ title }} — Capability Evidence OS</title>

<style>

:root {
    --bg: #060812;
    --panel: rgba(15, 19, 35, 0.82);
    --panel2: rgba(20, 25, 46, 0.78);
    --border: rgba(139, 157, 255, 0.16);
    --text: #f5f7ff;
    --muted: #9299b5;
    --cyan: #67e8f9;
    --purple: #9b8cff;
    --green: #5ee6a8;
    --yellow: #f6d365;
    --red: #ff718c;
    --shadow: 0 20px 70px rgba(0,0,0,.35);
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    color: var(--text);
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    background:
        radial-gradient(
            circle at 12% 12%,
            rgba(103,232,249,.10),
            transparent 28%
        ),
        radial-gradient(
            circle at 85% 18%,
            rgba(155,140,255,.13),
            transparent 30%
        ),
        radial-gradient(
            circle at 50% 100%,
            rgba(94,230,168,.06),
            transparent 30%
        ),
        #060812;
}

body:before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(255,255,255,.018) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,.018) 1px,
            transparent 1px
        );

    background-size: 42px 42px;
    mask-image: linear-gradient(
        to bottom,
        black,
        transparent 90%
    );
}

a {
    color: inherit;
    text-decoration: none;
}

button,
input {
    font: inherit;
}

.layout {
    display: flex;
    min-height: 100vh;
}

.sidebar {
    width: 260px;
    padding: 25px 18px;
    border-right: 1px solid var(--border);
    background: rgba(6,8,18,.78);
    backdrop-filter: blur(20px);
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 20;
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 35px;
}

.logo-mark {
    width: 42px;
    height: 42px;
    border-radius: 14px;

    display: grid;
    place-items: center;

    background:
        linear-gradient(
            135deg,
            rgba(103,232,249,.22),
            rgba(155,140,255,.28)
        );

    border: 1px solid rgba(103,232,249,.25);
    box-shadow:
        0 0 30px rgba(103,232,249,.10);
}

.logo-mark span {
    width: 14px;
    height: 14px;
    border: 2px solid var(--cyan);
    transform: rotate(45deg);
}

.logo-title {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: .08em;
}

.logo-sub {
    font-size: 10px;
    color: var(--muted);
    margin-top: 3px;
    letter-spacing: .08em;
}

.nav-label {
    color: #646b88;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .16em;
    margin: 20px 12px 9px;
}

.nav {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.nav a {
    padding: 11px 12px;
    border-radius: 11px;
    color: #9299b5;
    font-size: 13px;
    transition: .2s;
}

.nav a:hover {
    background: rgba(255,255,255,.045);
    color: white;
}

.nav a.active {
    color: white;
    background:
        linear-gradient(
            90deg,
            rgba(103,232,249,.10),
            rgba(155,140,255,.08)
        );
    border: 1px solid rgba(103,232,249,.11);
}

.sidebar-bottom {
    position: absolute;
    left: 18px;
    right: 18px;
    bottom: 22px;
}

.system-card {
    border: 1px solid var(--border);
    background: rgba(255,255,255,.025);
    padding: 14px;
    border-radius: 14px;
}

.system-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11px;
    color: var(--muted);
}

.dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 12px rgba(94,230,168,.8);
}

.main {
    margin-left: 260px;
    width: calc(100% - 260px);
    padding: 30px 34px 70px;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 30px;
}

.eyebrow {
    color: var(--cyan);
    text-transform: uppercase;
    letter-spacing: .16em;
    font-size: 10px;
    font-weight: 800;
    margin-bottom: 8px;
}

h1 {
    margin: 0;
    font-size: clamp(26px, 3vw, 40px);
    letter-spacing: -.04em;
}

.subtitle {
    margin-top: 7px;
    color: var(--muted);
    font-size: 13px;
}

.top-actions {
    display: flex;
    gap: 8px;
}

.btn {
    border: 1px solid var(--border);
    background: rgba(255,255,255,.035);
    color: white;
    padding: 10px 14px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 700;
    transition: .2s;
}

.btn:hover {
    transform: translateY(-1px);
    border-color: rgba(103,232,249,.35);
}

.btn-primary {
    border-color: rgba(103,232,249,.35);
    background:
        linear-gradient(
            135deg,
            rgba(103,232,249,.16),
            rgba(155,140,255,.18)
        );
}

.btn-danger {
    color: #ffb6c2;
}

.grid {
    display: grid;
    gap: 14px;
}

.metrics {
    grid-template-columns:
        repeat(5, minmax(0,1fr));
    margin-bottom: 18px;
}

.metric {
    padding: 18px;
    border: 1px solid var(--border);
    background: var(--panel);
    border-radius: 16px;
    box-shadow: var(--shadow);
}

.metric-label {
    color: var(--muted);
    font-size: 11px;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -.04em;
}

.metric-accent {
    margin-top: 8px;
    height: 2px;
    width: 55px;
    background: linear-gradient(
        90deg,
        var(--cyan),
        var(--purple)
    );
    border-radius: 99px;
}

.two-col {
    grid-template-columns: 1.25fr .75fr;
}

.three-col {
    grid-template-columns:
        repeat(3, minmax(0,1fr));
}

.card {
    border: 1px solid var(--border);
    background: var(--panel);
    border-radius: 18px;
    padding: 20px;
    box-shadow: var(--shadow);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 15px;
    margin-bottom: 18px;
}

.card-title {
    font-size: 15px;
    font-weight: 800;
}

.card-sub {
    color: var(--muted);
    font-size: 11px;
    margin-top: 5px;
}

.profile-head {
    display: flex;
    gap: 16px;
    align-items: center;
}

.avatar {
    width: 62px;
    height: 62px;
    border-radius: 18px;

    display: grid;
    place-items: center;

    background:
        linear-gradient(
            135deg,
            rgba(103,232,249,.14),
            rgba(155,140,255,.18)
        );

    border: 1px solid rgba(103,232,249,.20);
    font-weight: 900;
    font-size: 21px;
}

.profile-name {
    font-size: 21px;
    font-weight: 850;
}

.profile-role {
    color: var(--muted);
    margin-top: 4px;
    font-size: 12px;
}

.badges {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-top: 13px;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 9px;
    border-radius: 99px;
    border: 1px solid var(--border);
    color: #cbd1e8;
    background: rgba(255,255,255,.025);
    font-size: 10px;
    font-weight: 700;
}

.status {
    display: inline-flex;
    align-items: center;
    padding: 5px 8px;
    border-radius: 7px;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: .06em;
    text-transform: uppercase;
}

.status-strong,
.status-verified {
    color: var(--green);
    background: rgba(94,230,168,.08);
    border: 1px solid rgba(94,230,168,.18);
}

.status-partial {
    color: var(--yellow);
    background: rgba(246,211,101,.07);
    border: 1px solid rgba(246,211,101,.16);
}

.status-unverified {
    color: var(--red);
    background: rgba(255,113,140,.07);
    border: 1px solid rgba(255,113,140,.16);
}

.pipeline {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.pipe-node {
    padding: 10px 12px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,.025);
    border-radius: 10px;
    font-size: 10px;
    color: #cdd2e8;
}

.pipe-arrow {
    color: #59607b;
}

.capability-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.capability-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 12px;
    padding: 12px;
    border: 1px solid rgba(255,255,255,.055);
    background: rgba(255,255,255,.018);
    border-radius: 12px;
}

.capability-name {
    font-size: 12px;
    font-weight: 700;
}

.capability-evidence {
    color: var(--muted);
    font-size: 10px;
    margin-top: 5px;
    line-height: 1.5;
}

.evidence-box {
    padding: 14px;
    border: 1px solid rgba(103,232,249,.10);
    background: rgba(103,232,249,.025);
    border-radius: 12px;
    margin-top: 10px;
}

.evidence-label {
    color: var(--cyan);
    font-size: 9px;
    text-transform: uppercase;
    font-weight: 900;
    letter-spacing: .12em;
}

.evidence-text {
    color: #cbd1e8;
    font-size: 11px;
    line-height: 1.55;
    margin-top: 6px;
}

.info-grid {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0,1fr));
    gap: 10px;
}

.info-item {
    padding: 13px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,.055);
    background: rgba(255,255,255,.018);
}

.info-label {
    color: #727a97;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .1em;
    font-weight: 800;
}

.info-value {
    color: #e8ebf8;
    font-size: 12px;
    margin-top: 5px;
    line-height: 1.5;
    word-break: break-word;
}

.upload-zone {
    min-height: 330px;
    border: 1px dashed rgba(103,232,249,.30);
    border-radius: 22px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 35px;

    background:
        radial-gradient(
            circle at center,
            rgba(103,232,249,.06),
            transparent 58%
        );

    transition: .2s;
}

.upload-zone:hover {
    border-color: rgba(103,232,249,.55);
    background:
        radial-gradient(
            circle at center,
            rgba(103,232,249,.09),
            transparent 58%
        );
}

.upload-icon {
    width: 68px;
    height: 68px;
    border-radius: 20px;
    display: grid;
    place-items: center;
    font-size: 25px;

    background: rgba(103,232,249,.07);
    border: 1px solid rgba(103,232,249,.18);
    margin-bottom: 17px;
}

.upload-title {
    font-size: 19px;
    font-weight: 800;
}

.upload-sub {
    color: var(--muted);
    font-size: 12px;
    margin: 7px 0 20px;
    max-width: 520px;
    line-height: 1.6;
}

input[type="file"] {
    display: none;
}

.file-name {
    margin-top: 12px;
    color: var(--cyan);
    font-size: 11px;
}

.progress {
    height: 7px;
    background: rgba(255,255,255,.05);
    border-radius: 99px;
    overflow: hidden;
    margin-top: 10px;
}

.progress-fill {
    height: 100%;
    width: var(--width);
    background:
        linear-gradient(
            90deg,
            var(--cyan),
            var(--purple)
        );
}

.table-wrap {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    color: #737b98;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .1em;
    text-align: left;
    padding: 11px 10px;
    border-bottom: 1px solid var(--border);
}

td {
    padding: 13px 10px;
    border-bottom: 1px solid rgba(255,255,255,.045);
    color: #cfd4e9;
    font-size: 11px;
    vertical-align: top;
}

.req-symbol {
    font-size: 17px;
    font-weight: 900;
}

.symbol-match {
    color: var(--green);
}

.symbol-partial {
    color: var(--yellow);
}

.symbol-unverified {
    color: var(--red);
}

.gap-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding: 16px;
    border: 1px solid rgba(255,113,140,.14);
    background: rgba(255,113,140,.035);
    border-radius: 14px;
}

.gap-title {
    font-size: 13px;
    font-weight: 800;
}

.gap-sub {
    color: var(--muted);
    font-size: 10px;
    margin-top: 5px;
}

.verify-card {
    max-width: 800px;
    margin: auto;
}

.verify-hero {
    text-align: center;
    padding: 25px 10px 10px;
}

.verify-icon {
    width: 74px;
    height: 74px;
    border-radius: 23px;
    display: grid;
    place-items: center;
    margin: 0 auto 17px;

    background:
        linear-gradient(
            135deg,
            rgba(103,232,249,.12),
            rgba(155,140,255,.16)
        );

    border: 1px solid rgba(103,232,249,.22);
    font-size: 28px;
}

.verify-title {
    font-size: 25px;
    font-weight: 850;
}

.verify-description {
    color: var(--muted);
    max-width: 620px;
    margin: 8px auto 22px;
    font-size: 12px;
    line-height: 1.7;
}

.task-box {
    padding: 18px;
    border: 1px solid var(--border);
    border-radius: 15px;
    background: rgba(255,255,255,.025);
}

.task-title {
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 7px;
}

.task-text {
    color: #b9bfd4;
    font-size: 11px;
    line-height: 1.65;
}

textarea {
    width: 100%;
    min-height: 110px;
    resize: vertical;
    margin-top: 15px;
    border-radius: 12px;
    border: 1px solid var(--border);
    background: rgba(0,0,0,.2);
    color: white;
    padding: 13px;
    outline: none;
}

textarea:focus {
    border-color: rgba(103,232,249,.38);
}

.notice {
    padding: 13px 15px;
    border-radius: 12px;
    margin-bottom: 15px;
    font-size: 11px;
    line-height: 1.6;
}

.notice-info {
    color: #c9eefa;
    border: 1px solid rgba(103,232,249,.14);
    background: rgba(103,232,249,.04);
}

.notice-warning {
    color: #ffe7a6;
    border: 1px solid rgba(246,211,101,.14);
    background: rgba(246,211,101,.035);
}

.empty {
    text-align: center;
    padding: 65px 25px;
}

.empty-icon {
    font-size: 38px;
    margin-bottom: 15px;
    opacity: .8;
}

.empty-title {
    font-size: 18px;
    font-weight: 800;
}

.empty-sub {
    color: var(--muted);
    font-size: 11px;
    line-height: 1.7;
    max-width: 520px;
    margin: 8px auto 20px;
}

.footer-note {
    color: #606781;
    font-size: 10px;
    margin-top: 18px;
    line-height: 1.6;
}

@media(max-width: 1050px) {
    .metrics {
        grid-template-columns:
            repeat(3, minmax(0,1fr));
    }

    .two-col {
        grid-template-columns: 1fr;
    }
}

@media(max-width: 760px) {

    .sidebar {
        width: 100%;
        height: auto;
        position: relative;
        bottom: auto;
        border-right: 0;
        border-bottom: 1px solid var(--border);
    }

    .layout {
        display: block;
    }

    .main {
        margin-left: 0;
        width: 100%;
        padding: 22px 16px 50px;
    }

    .sidebar-bottom {
        display: none;
    }

    .nav {
        flex-direction: row;
        overflow-x: auto;
    }

    .nav-label {
        display: none;
    }

    .logo {
        margin-bottom: 15px;
    }

    .metrics,
    .three-col {
        grid-template-columns: 1fr 1fr;
    }

    .topbar {
        align-items: flex-start;
        gap: 15px;
        flex-direction: column;
    }

    .info-grid {
        grid-template-columns: 1fr;
    }
}

@media(max-width: 500px) {
    .metrics,
    .three-col {
        grid-template-columns: 1fr;
    }

    .gap-card {
        flex-direction: column;
        align-items: flex-start;
    }
}

</style>

</head>

<body>

<div class="layout">

    <aside class="sidebar">

        <a href="{{ url_for('home') }}" class="logo">

            <div class="logo-mark">
                <span></span>
            </div>

            <div>
                <div class="logo-title">
                    CAPABILITY OS
                </div>

                <div class="logo-sub">
                    EVIDENCE INTELLIGENCE
                </div>
            </div>

        </a>

        <div class="nav-label">
            WORKSPACE
        </div>

        <nav class="nav">

            <a href="{{ url_for('home') }}"
               class="{{ 'active' if active == 'home' else '' }}">
                Command Center
            </a>

            <a href="{{ url_for('candidate') }}"
               class="{{ 'active' if active == 'candidate' else '' }}">
                Candidate
            </a>

            <a href="{{ url_for('upload') }}"
               class="{{ 'active' if active == 'upload' else '' }}">
                Evidence Intake
            </a>

            <a href="{{ url_for('evidence') }}"
               class="{{ 'active' if active == 'evidence' else '' }}">
                Evidence Intelligence
            </a>

            <a href="{{ url_for('job') }}"
               class="{{ 'active' if active == 'job' else '' }}">
                Job Requirements
            </a>

            <a href="{{ url_for('gap') }}"
               class="{{ 'active' if active == 'gap' else '' }}">
                Evidence Gaps
            </a>

            <a href="{{ url_for('verify') }}"
               class="{{ 'active' if active == 'verify' else '' }}">
                Verification
            </a>

            <a href="{{ url_for('review') }}"
               class="{{ 'active' if active == 'review' else '' }}">
                Human Review
            </a>

        </nav>

        <div class="sidebar-bottom">

            <div class="system-card">

                <div class="system-row">
                    <span>Evidence Engine</span>
                    <span class="dot"></span>
                </div>

                <div class="system-row"
                     style="margin-top:9px;">
                    <span>Mode</span>
                    <span>DEMO</span>
                </div>

            </div>

        </div>

    </aside>


    <main class="main">

        <div class="topbar">

            <div>
                <div class="eyebrow">
                    SAP HACKFEST 2026 • THEME 2
                </div>

                <h1>{{ heading }}</h1>

                <div class="subtitle">
                    {{ subtitle }}
                </div>
            </div>

            <div class="top-actions">

                {% if has_candidate %}

                    <a href="{{ url_for('upload') }}"
                       class="btn btn-primary">
                        + Upload Resume
                    </a>

                    <form method="POST"
                          action="{{ url_for('api_reset') }}"
                          style="display:inline;">

                        <button
                            class="btn btn-danger"
                            type="submit">
                            Reset
                        </button>

                    </form>

                {% else %}

                    <a href="{{ url_for('upload') }}"
                       class="btn btn-primary">
                        Upload Resume
                    </a>

                {% endif %}

            </div>

        </div>

        {{ body|safe }}

    </main>

</div>

</body>
</html>
"""


def page(title, heading, subtitle, body, active):
    return render_template_string(
        BASE_TEMPLATE,
        title=title,
        heading=heading,
        subtitle=subtitle,
        body=body,
        active=active,
        has_candidate=STATE["candidate"] is not None
    )


def initials(name):
    parts = name.split()

    if not parts:
        return "C"

    if len(parts) == 1:
        return parts[0][0].upper()

    return (
        parts[0][0] +
        parts[-1][0]
    ).upper()


def status_html(status):
    css = status.lower()

    return (
        f'<span class="status status-{css}">'
        f'{esc(status)}'
        f'</span>'
    )


# ============================================================
# HOME / COMMAND CENTER
# ============================================================

@app.route("/")
def home():

    if not STATE["candidate"]:

        body = """
        <div class="card">
            <div class="empty">

                <div class="empty-icon">
                    ◇
                </div>

                <div class="empty-title">
                    No candidate evidence loaded
                </div>

                <div class="empty-sub">
                    Upload a candidate resume to activate the
                    Capability Evidence OS. The uploaded resume
                    becomes the source of truth for the candidate
                    profile, capability map, evidence snippets,
                    evidence gaps and verification flow.
                </div>

                <a href="/upload"
                   class="btn btn-primary">
                    Upload Candidate Resume
                </a>

                <div class="footer-note">
                    PDF text extraction only in this prototype.
                    Scanned image-only PDFs may not produce readable text.
                </div>

            </div>
        </div>
        """

        return page(
            "Command Center",
            "Evidence Command Center",
            "Upload a resume to begin capability intelligence.",
            body,
            "home"
        )

    candidate = STATE["candidate"]

    total_capabilities = len(STATE["capabilities"])
    gaps = len(get_gaps())
    pending = sum(
        1
        for c in STATE["capabilities"]
        if c["status"] == "Unverified"
    )

    body = f"""
    <div class="grid metrics">

        <div class="metric">
            <div class="metric-label">PEOPLE</div>
            <div class="metric-value">1</div>
            <div class="metric-accent"></div>
        </div>

        <div class="metric">
            <div class="metric-label">CAPABILITIES</div>
            <div class="metric-value">{total_capabilities}</div>
            <div class="metric-accent"></div>
        </div>

        <div class="metric">
            <div class="metric-label">EVIDENCE HEALTH</div>
            <div class="metric-value">{evidence_health()}%</div>
            <div class="metric-accent"></div>
        </div>

        <div class="metric">
            <div class="metric-label">EVIDENCE GAPS</div>
            <div class="metric-value">{gaps}</div>
            <div class="metric-accent"></div>
        </div>

        <div class="metric">
            <div class="metric-label">PENDING VERIFICATION</div>
            <div class="metric-value">{pending}</div>
            <div class="metric-accent"></div>
        </div>

    </div>

    <div class="grid two-col">

        <div class="card">

            <div class="card-header">

                <div>
                    <div class="card-title">
                        Candidate Evidence Profile
                    </div>

                    <div class="card-sub">
                        Source: {esc(candidate["filename"])}
                    </div>
                </div>

                {status_html("Strong")}

            </div>

            <div class="profile-head">

                <div class="avatar">
                    {esc(initials(candidate["name"]))}
                </div>

                <div>

                    <div class="profile-name">
                        {esc(candidate["name"])}
                    </div>

                    <div class="profile-role">
                        {esc(candidate["role"])}
                    </div>

                    <div class="badges">
                        <span class="badge">
                            {esc(candidate["education"])}
                        </span>

                        <span class="badge">
                            {esc(candidate["experience"])}
                        </span>

                        <span class="badge">
                            Gap: {esc(candidate["career_gap"])}
                        </span>
                    </div>

                </div>

            </div>

            <div style="margin-top:22px;">

                <div class="card-sub"
                     style="margin-bottom:9px;">
                    CAPABILITY PIPELINE
                </div>

                <div class="pipeline">

                    <div class="pipe-node">
                        Candidate
                    </div>

                    <div class="pipe-arrow">→</div>

                    <div class="pipe-node">
                        Evidence
                    </div>

                    <div class="pipe-arrow">→</div>

                    <div class="pipe-node">
                        Capability
                    </div>

                    <div class="pipe-arrow">→</div>

                    <div class="pipe-node">
                        Gap
                    </div>

                    <div class="pipe-arrow">→</div>

                    <div class="pipe-node">
                        Verification
                    </div>

                    <div class="pipe-arrow">→</div>

                    <div class="pipe-node">
                        Human Review
                    </div>

                </div>

            </div>

        </div>


        <div class="card">

            <div class="card-header">

                <div>
                    <div class="card-title">
                        Evidence Principle
                    </div>

                    <div class="card-sub">
                        Core system rule
                    </div>
                </div>

            </div>

            <div style="
                font-size:24px;
                font-weight:900;
                letter-spacing:-.04em;
                margin:10px 0 12px;
            ">
                UNVERIFIED
                <span style="color:#59607b;">≠</span>
                ABSENT
            </div>

            <div class="notice notice-info">
                Missing evidence does not automatically mean
                missing capability. The system identifies the
                evidence gap and routes it toward verification.
            </div>

            <div class="notice notice-warning">
                AI provides evidence intelligence. It does not
                make the final hiring decision.
            </div>

        </div>

    </div>

    <div class="card" style="margin-top:14px;">

        <div class="card-header">

            <div>
                <div class="card-title">
                    Capability Snapshot
                </div>

                <div class="card-sub">
                    Detected from uploaded resume evidence
                </div>
            </div>

            <a href="/evidence"
               class="btn">
                View all
            </a>

        </div>

        <div class="capability-list">
    """

    for capability in STATE["capabilities"][:8]:

        evidence_text = (
            capability["evidence"][0]
            if capability["evidence"]
            else "No direct evidence found in uploaded resume."
        )

        body += f"""
            <div class="capability-row">

                <div>
                    <div class="capability-name">
                        {esc(capability["name"])}
                    </div>

                    <div class="capability-evidence">
                        {esc(evidence_text[:190])}
                    </div>
                </div>

                <div>
                    {status_html(capability["status"])}
                </div>

            </div>
        """

    body += """
        </div>
    </div>
    """

    return page(
        "Command Center",
        "Evidence Command Center",
        "Candidate capability intelligence from uploaded evidence.",
        body,
        "home"
    )


# ============================================================
# UPLOAD
# ============================================================

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        if "resume" not in request.files:

            body = """
            <div class="card">
                <div class="notice notice-warning">
                    No resume file was selected.
                </div>

                <a href="/upload" class="btn">
                    Back to upload
                </a>
            </div>
            """

            return page(
                "Evidence Intake",
                "Evidence Intake",
                "Upload a candidate resume.",
                body,
                "upload"
            )

        file = request.files["resume"]

        if not file.filename:

            body = """
            <div class="card">
                <div class="notice notice-warning">
                    Please select a PDF resume.
                </div>

                <a href="/upload" class="btn">
                    Back to upload
                </a>
            </div>
            """

            return page(
                "Evidence Intake",
                "Evidence Intake",
                "Upload a candidate resume.",
                body,
                "upload"
            )

        filename = secure_filename(file.filename)

        if not filename.lower().endswith(".pdf"):

            body = """
            <div class="card">
                <div class="notice notice-warning">
                    This prototype accepts PDF resumes only.
                </div>

                <a href="/upload" class="btn">
                    Try again
                </a>
            </div>
            """

            return page(
                "Evidence Intake",
                "Evidence Intake",
                "PDF resume required.",
                body,
                "upload"
            )

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        try:
            extracted_text, extraction_mode, extraction_message = extract_pdf_text(
                filepath
            )

        except Exception as error:

            body = f"""
            <div class="card">

                <div class="notice notice-warning">
                    The PDF could not be processed.
                    Please try another readable PDF resume.
                </div>

                <div class="footer-note">
                    Technical detail: {esc(str(error)[:300])}
                </div>

                <a href="/upload"
                   class="btn"
                   style="margin-top:15px;">
                    Try again
                </a>

            </div>
            """

            return page(
                "Upload Error",
                "Resume Processing Error",
                "The evidence intake engine could not read this file.",
                body,
                "upload"
            )

        print(
            f"Resume extraction mode: {extraction_mode}; "
            f"characters: {len(extracted_text)}"
        )

        if not extracted_text.strip():

            message = extraction_message or (
                "No readable text was detected in this PDF."
            )

            body = f"""
            <div class="card">

                <div class="notice notice-warning">
                    {esc(message)}
                </div>

                <div class="footer-note" style="margin-top:14px;">
                    The intake engine supports both normal text PDFs and
                    scanned/image-based resumes when OCR is available.
                </div>

                <a href="/upload"
                   class="btn"
                   style="margin-top:15px;">
                    Try another PDF
                </a>

            </div>
            """

            return page(
                "Extraction Issue",
                "No Readable Evidence",
                "The resume could not be converted into readable evidence.",
                body,
                "upload"
            )

        # ----------------------------------------------------
        # RESET OLD CANDIDATE
        # ----------------------------------------------------

        reset_state()

        # ----------------------------------------------------
        # BUILD NEW CANDIDATE
        # ----------------------------------------------------

        candidate = build_candidate(
            extracted_text,
            filename
        )

        capabilities = build_capabilities(
            extracted_text
        )

        STATE["candidate"] = candidate
        STATE["capabilities"] = capabilities
        STATE["raw_text"] = extracted_text
        STATE["filename"] = filename
        STATE["uploaded_at"] = datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        )
        STATE["job"] = infer_job_profile(
            candidate, extracted_text, capabilities
        )

        return redirect(url_for("candidate"))

    body = """
    <div class="card">

        <div class="card-header">

            <div>
                <div class="card-title">
                    Resume → Evidence Intelligence
                </div>

                <div class="card-sub">
                    Upload the resume that should become
                    the candidate's source of truth.
                </div>
            </div>

            <span class="badge">
                PDF • MAX 10 MB
            </span>

        </div>

        <form method="POST"
              enctype="multipart/form-data"
              id="uploadForm">

            <label for="resume"
                   class="upload-zone"
                   id="uploadZone">

                <div class="upload-icon">
                    ↑
                </div>

                <div class="upload-title">
                    Drop resume here
                </div>

                <div class="upload-sub">
                    Or click to browse your computer.
                    The system will extract text, detect
                    capabilities and build an evidence map.
                </div>

                <span class="btn btn-primary">
                    Select PDF Resume
                </span>

                <div class="file-name"
                     id="fileName">
                </div>

            </label>

            <input
                type="file"
                name="resume"
                id="resume"
                accept=".pdf,application/pdf"
                required
            >

            <div style="
                margin-top:18px;
                text-align:right;
            ">

                <button
                    type="submit"
                    class="btn btn-primary">
                    Run Evidence Analysis →
                </button>

            </div>

        </form>

    </div>


    <div class="grid three-col"
         style="margin-top:14px;">

        <div class="card">

            <div class="eyebrow">
                01
            </div>

            <div class="card-title">
                Extract
            </div>

            <div class="card-sub"
                 style="line-height:1.6;">
                Read resume text and identify profile,
                education, experience and skills.
            </div>

        </div>

        <div class="card">

            <div class="eyebrow">
                02
            </div>

            <div class="card-title">
                Translate
            </div>

            <div class="card-sub"
                 style="line-height:1.6;">
                Translate activities and resume signals
                into capability evidence.
            </div>

        </div>

        <div class="card">

            <div class="eyebrow">
                03
            </div>

            <div class="card-title">
                Verify
            </div>

            <div class="card-sub"
                 style="line-height:1.6;">
                Unverified capabilities become candidates
                for practical verification.
            </div>

        </div>

    </div>


    <div class="footer-note">
        Privacy note: this local prototype stores the uploaded
        PDF inside the project's uploads folder. It is not sent
        to an external AI service by this prototype.
    </div>


    <script>

    const input = document.getElementById("resume");
    const fileName = document.getElementById("fileName");
    const zone = document.getElementById("uploadZone");

    input.addEventListener("change", function() {

        if (input.files.length > 0) {
            fileName.textContent =
                "Selected: " + input.files[0].name;
        }

    });

    zone.addEventListener("dragover", function(event) {
        event.preventDefault();
        zone.style.borderColor =
            "rgba(103,232,249,.75)";
    });

    zone.addEventListener("dragleave", function() {
        zone.style.borderColor =
            "rgba(103,232,249,.30)";
    });

    zone.addEventListener("drop", function(event) {

        event.preventDefault();

        zone.style.borderColor =
            "rgba(103,232,249,.30)";

        if (event.dataTransfer.files.length > 0) {

            input.files =
                event.dataTransfer.files;

            fileName.textContent =
                "Selected: " +
                event.dataTransfer.files[0].name;
        }

    });

    </script>
    """

    return page(
        "Evidence Intake",
        "Evidence Intake",
        "Upload the candidate resume and build the evidence layer.",
        body,
        "upload"
    )


# ============================================================
# CANDIDATE
# ============================================================

@app.route("/candidate")
def candidate():

    if not STATE["candidate"]:

        body = """
        <div class="card">
            <div class="empty">
                <div class="empty-icon">◇</div>
                <div class="empty-title">No Candidate Loaded</div>
                <div class="empty-sub">No candidate profile is currently loaded. Upload a resume to create the candidate profile and start capability analysis.</div>
                <div style="margin-top:22px;">
                    <a href="/upload" class="btn btn-primary">Upload Candidate Resume</a>
                </div>
            </div>
        </div>
        """

        return page(
            "Candidate",
            "Candidate Profile",
            "Candidate intelligence workspace.",
            body,
            "candidate"
        )

    c = STATE["candidate"]

    skills_html = ""

    if c["skills"]:

        for skill in c["skills"]:
            skills_html += f"""
            <span class="badge">
                {esc(skill)}
            </span>
            """

    else:

        skills_html = """
        <span class="badge">
            No listed skills detected
        </span>
        """

    body = f"""

    <div class="grid two-col">

        <div class="card">

            <div class="profile-head">

                <div class="avatar">
                    {esc(initials(c["name"]))}
                </div>

                <div>

                    <div class="profile-name">
                        {esc(c["name"])}
                    </div>

                    <div class="profile-role">
                        {esc(c["role"])}
                    </div>

                    <div class="badges">

                        <span class="badge">
                            Resume: {esc(c["filename"])}
                        </span>

                        <span class="badge">
                            Uploaded: {esc(STATE["uploaded_at"])}
                        </span>

                    </div>

                </div>

            </div>

            <div style="margin-top:22px;">

                <div class="card-sub"
                     style="margin-bottom:9px;">
                    DETECTED SKILLS
                </div>

                <div class="badges">
                    {skills_html}
                </div>

            </div>

        </div>


        <div class="card">

            <div class="card-header">

                <div>
                    <div class="card-title">
                        Profile Intelligence
                    </div>

                    <div class="card-sub">
                        Extracted directly from uploaded resume
                    </div>
                </div>

            </div>

            <div class="info-grid">

                <div class="info-item">
                    <div class="info-label">
                        Name
                    </div>
                    <div class="info-value">
                        {esc(c["name"])}
                    </div>
                </div>

                <div class="info-item">
                    <div class="info-label">
                        Role
                    </div>
                    <div class="info-value">
                        {esc(c["role"])}
                    </div>
                </div>

                <div class="info-item">
                    <div class="info-label">
                        Education
                    </div>
                    <div class="info-value">
                        {esc(c["education"])}
                    </div>
                </div>

                <div class="info-item">
                    <div class="info-label">
                        Experience
                    </div>
                    <div class="info-value">
                        {esc(c["experience"])}
                    </div>
                </div>

                <div class="info-item">
                    <div class="info-label">
                        Career Gap
                    </div>
                    <div class="info-value">
                        {esc(c["career_gap"])}
                    </div>
                </div>

                <div class="info-item">
                    <div class="info-label">
                        Email
                    </div>
                    <div class="info-value">
                        {esc(c["email"])}
                    </div>
                </div>

                <div class="info-item">
                    <div class="info-label">
                        Phone
                    </div>
                    <div class="info-value">
                        {esc(c["phone"])}
                    </div>
                </div>

                <div class="info-item">
                    <div class="info-label">
                        Goal
                    </div>
                    <div class="info-value">
                        {esc(c["goal"])}
                    </div>
                </div>

            </div>

        </div>

    </div>


    <div class="card"
         style="margin-top:14px;">

        <div class="card-header">

            <div>
                <div class="card-title">
                    Resume Summary
                </div>

                <div class="card-sub">
                    Extracted profile context
                </div>
            </div>

        </div>

        <div class="evidence-box">

            <div class="evidence-label">
                PROFILE EVIDENCE
            </div>

            <div class="evidence-text">
                {esc(c["summary"])}
            </div>

        </div>

    </div>


    <div class="card"
         style="margin-top:14px;">

        <div class="card-header">

            <div>
                <div class="card-title">
                    Candidate Capability Map
                </div>

                <div class="card-sub">
                    Capability states generated from resume evidence
                </div>
            </div>

        </div>

        <div class="capability-list">
    """

    for capability in STATE["capabilities"]:

        first_evidence = (
            capability["evidence"][0]
            if capability["evidence"]
            else "No direct evidence found."
        )

        body += f"""
            <div class="capability-row">

                <div>

                    <div class="capability-name">
                        {esc(capability["name"])}
                    </div>

                    <div class="capability-evidence">
                        {esc(first_evidence)}
                    </div>

                </div>

                <div>
                    {status_html(capability["status"])}
                </div>

            </div>
        """

    body += """
        </div>
    </div>
    """

    return page(
        "Candidate",
        "Candidate Capability Profile",
        "The uploaded resume is the source of truth.",
        body,
        "candidate"
    )


# ============================================================
# EVIDENCE
# ============================================================

@app.route("/evidence")
def evidence():

    if not STATE["candidate"]:
        return redirect(url_for("upload"))

    body = """
    <div class="card">

        <div class="card-header">

            <div>
                <div class="card-title">
                    Evidence Intelligence
                </div>

                <div class="card-sub">
                    Capability states and supporting resume evidence
                </div>
            </div>

            <span class="badge">
                SOURCE: RESUME
            </span>

        </div>

        <div class="capability-list">
    """

    for capability in STATE["capabilities"]:

        body += f"""
        <div class="card"
             style="
                background:rgba(255,255,255,.018);
                box-shadow:none;
             ">

            <div class="card-header">

                <div>
                    <div class="card-title">
                        {esc(capability["name"])}
                    </div>

                    <div class="card-sub">
                        Matched signals:
                        {esc(", ".join(capability["matched_keywords"])
                              if capability["matched_keywords"]
                              else "None detected")}
                    </div>
                </div>

                {status_html(capability["status"])}

            </div>
        """

        if capability["evidence"]:

            for snippet in capability["evidence"]:

                body += f"""
                <div class="evidence-box">

                    <div class="evidence-label">
                        RESUME EVIDENCE
                    </div>

                    <div class="evidence-text">
                        {esc(snippet)}
                    </div>

                </div>
                """

        else:

            body += """
            <div class="notice notice-warning"
                 style="margin-top:0;">
                No direct evidence detected for this capability.
                This means UNVERIFIED, not ABSENT.
            </div>
            """

        body += """
        </div>
        """

    body += """
        </div>
    </div>
    """

    return page(
        "Evidence Intelligence",
        "Evidence Intelligence",
        "From resume claims and activities to capability evidence.",
        body,
        "evidence"
    )


# ============================================================
# JOB REQUIREMENTS
# ============================================================

@app.route("/job")
def job():

    if not STATE["candidate"]:
        return redirect(url_for("upload"))

    requirements = required_capabilities()
    job_profile = STATE.get("job") or {}
    job_title = job_profile.get("title", "General / Entry-Level Professional")
    job_confidence = job_profile.get("confidence", 0)

    body = f"""
    <div class="card">

        <div class="card-header">

            <div>
                <div class="card-title">
                    {esc(job_title)}
                </div>

                <div class="card-sub">
                    Dynamically inferred from this candidate's resume • {job_confidence}% profile confidence
                </div>
            </div>

            <span class="badge">
                REQUIREMENT ANALYSIS
            </span>

        </div>

        <div class="table-wrap">

            <table>

                <thead>

                    <tr>
                        <th>Required Capability</th>
                        <th>Candidate Evidence</th>
                        <th>State</th>
                        <th>Requirement Match</th>
                    </tr>

                </thead>

                <tbody>
    """

    for requirement in requirements:

        capability = capability_by_name(requirement)

        if capability:

            status = capability["status"]

            if status in ["Strong", "Verified"]:
                symbol = "✓"
                symbol_class = "symbol-match"

            elif status == "Partial":
                symbol = "~"
                symbol_class = "symbol-partial"

            else:
                symbol = "?"
                symbol_class = "symbol-unverified"

            evidence = (
                capability["evidence"][0]
                if capability["evidence"]
                else "No direct resume evidence detected."
            )

        else:

            status = "Unverified"
            symbol = "?"
            symbol_class = "symbol-unverified"
            evidence = "No capability record detected."

        body += f"""

                    <tr>

                        <td>
                            <strong>
                                {esc(requirement)}
                            </strong>
                        </td>

                        <td>
                            {esc(evidence[:180])}
                        </td>

                        <td>
                            {status_html(status)}
                        </td>

                        <td>
                            <span class="
                                req-symbol
                                {symbol_class}
                            ">
                                {symbol}
                            </span>
                        </td>

                    </tr>
        """

    body += """

                </tbody>

            </table>

        </div>

    </div>


    <div class="notice notice-info"
         style="margin-top:14px;">

        Requirement mapping identifies evidence states.
        It does not make a hiring decision.

    </div>
    """

    return page(
        "Job Requirements",
        "Job Requirement Map",
        "Map candidate capability evidence against role requirements.",
        body,
        "job"
    )


# ============================================================
# GAP
# ============================================================

@app.route("/gap")
def gap():

    if not STATE["candidate"]:
        return redirect(url_for("upload"))

    gaps = get_gaps()

    if not gaps:

        body = """
        <div class="card">

            <div class="empty">

                <div class="empty-icon">
                    ✓
                </div>

                <div class="empty-title">
                    No current evidence gaps
                </div>

                <div class="empty-sub">
                    All detected role requirements
                    currently have Strong or Verified evidence.
                </div>

                <a href="/review"
                   class="btn btn-primary">
                    Continue to Human Review
                </a>

            </div>

        </div>
        """

    else:

        body = """

        <div class="notice notice-info">

            Evidence gaps are opportunities for verification.
            An unverified capability is not automatically absent.

        </div>

        <div class="grid">

        """

        for item in gaps:

            action = "Start Verification"

            if item["status"] == "Partial":
                action = "Strengthen Evidence"

            body += f"""
            <div class="gap-card">

                <div>

                    <div class="gap-title">
                        {esc(item["name"])}
                    </div>

                    <div class="gap-sub">
                        Current state:
                        {esc(item["status"])}
                        • Recommended action:
                        practical verification
                    </div>

                </div>

                <a href="/verify?capability={esc(item["name"])}"
                   class="btn btn-primary">
                    {action} →
                </a>

            </div>
            """

        body += """
        </div>
        """

    return page(
        "Evidence Gaps",
        "Evidence Gap Engine",
        "Find evidence that needs verification instead of assuming absence.",
        body,
        "gap"
    )


# ============================================================
# VERIFICATION
# ============================================================

@app.route("/verify")
def verify():

    if not STATE["candidate"]:
        return redirect(url_for("upload"))

    requested = request.args.get("capability")

    target = None

    if requested:
        target = capability_by_name(requested)

    if not target:
        target = next_verification_capability()

    if not target:

        body = """
        <div class="card verify-card">

            <div class="verify-hero">

                <div class="verify-icon">
                    ✓
                </div>

                <div class="verify-title">
                    Verification Queue Clear
                </div>

                <div class="verify-description">
                    There are currently no unverified or partial
                    role capability requirements
                    requiring verification.
                </div>

                <a href="/review"
                   class="btn btn-primary">
                    Open Human Review
                </a>

            </div>

        </div>
        """

        return page(
            "Verification",
            "Verification Center",
            "Turn evidence gaps into verifiable evidence.",
            body,
            "verify"
        )

    capability_name = target["name"]

    already_verified = (
        target["status"] == "Verified"
    )

    if already_verified:

        evidence = target["evidence"]

        evidence_text = (
            evidence[-1]
            if evidence
            else "Verification evidence recorded."
        )

        body = f"""
        <div class="card verify-card">

            <div class="verify-hero">

                <div class="verify-icon">
                    ✓
                </div>

                <div class="verify-title">
                    {esc(capability_name)} Verified
                </div>

                <div class="verify-description">
                    The prototype verification task has been
                    completed and the capability state has changed
                    to Verified.
                </div>

            </div>

            <div class="notice notice-info">
                Verification mode:
                <strong>Demo Practical Verification</strong>
            </div>

            <div class="task-box">

                <div class="task-title">
                    Recorded Evidence
                </div>

                <div class="task-text">
                    {esc(evidence_text)}
                </div>

            </div>

            <div style="
                margin-top:18px;
                text-align:center;
            ">

                <a href="/review"
                   class="btn btn-primary">
                    Send to Human Review →
                </a>

            </div>

        </div>
        """

        return page(
            "Verification Complete",
            "Verification Complete",
            "Verified evidence is now visible for human review.",
            body,
            "verify"
        )

    body = f"""
    <div class="card verify-card">

        <div class="verify-hero">

            <div class="verify-icon">
                ◈
            </div>

            <div class="verify-title">
                Verify {esc(capability_name)}
            </div>

            <div class="verify-description">
                The resume does not provide enough evidence
                to confidently classify this capability.
                Instead of assuming absence, the system
                creates a practical verification opportunity.
            </div>

        </div>


        <div class="notice notice-warning">

            Current state:
            <strong>{esc(target["status"])}</strong>

            <br>

            Rule:
            <strong>
                UNVERIFIED ≠ ABSENT
            </strong>

        </div>


        <div class="task-box">

            <div class="task-title">
                Suggested Practical Verification
            </div>

            <div class="task-text">
                Complete a short practical task related to
                <strong>{esc(capability_name)}</strong>.
                For example, provide a small work sample,
                analysis task, structured exercise or other
                relevant evidence that a human reviewer can inspect.
            </div>

        </div>


        <div class="task-box"
             style="margin-top:12px;">

            <div class="task-title">
                Prototype Demo Task
            </div>

            <div class="task-text">
                Complete a short practical task related to
                <strong>{esc(capability_name)}</strong> within
                approximately 10 minutes. The task is selected
                from the candidate's inferred role and capability gap.
            </div>

        </div>


        <div style="
            margin-top:20px;
            text-align:center;
        ">

            <button
                id="startVerification"
                class="btn btn-primary">
                Start Demo Verification
            </button>

        </div>

        <div id="verificationArea"
             style="display:none;margin-top:18px;">

            <div class="notice notice-info">
                Verification started. Add a short description
                of the evidence produced by the task.
            </div>

            <textarea
                id="verificationEvidence"
                placeholder="Example: Completed the practical analysis task and demonstrated the requested capability."></textarea>

            <div style="
                margin-top:12px;
                text-align:right;
            ">

                <button
                    id="completeVerification"
                    class="btn btn-primary">
                    Complete Verification →
                </button>

            </div>

        </div>

    </div>


    <script>

    const startButton =
        document.getElementById("startVerification");

    const area =
        document.getElementById("verificationArea");

    const completeButton =
        document.getElementById("completeVerification");

    startButton.addEventListener("click", async function() {{

        const response = await fetch(
            "/api/start-verification",
            {{
                method: "POST",
                headers: {{
                    "Content-Type":
                        "application/json"
                }},
                body: JSON.stringify({{
                    capability:
                        {esc(capability_name)}
                }})
            }}
        );

        const data = await response.json();

        if (data.success) {{

            startButton.style.display = "none";
            area.style.display = "block";

        }} else {{

            alert(
                data.message ||
                "Could not start verification."
            );

        }}

    }});


    completeButton.addEventListener("click", async function() {{

        const evidence =
            document.getElementById(
                "verificationEvidence"
            ).value.trim();

        if (!evidence) {{

            alert(
                "Please enter the verification evidence."
            );

            return;
        }}

        const response = await fetch(
            "/api/complete-verification",
            {{
                method: "POST",
                headers: {{
                    "Content-Type":
                        "application/json"
                }},
                body: JSON.stringify({{
                    capability:
                        {esc(capability_name)},
                    evidence:
                        evidence
                }})
            }}
        );

        const data = await response.json();

        if (data.success) {{
            window.location.href = "/verify";
        }} else {{
            alert(
                data.message ||
                "Verification could not be completed."
            );
        }}

    }});

    </script>
    """

    return page(
        "Verification",
        "Evidence Verification",
        "Convert an evidence gap into verifiable evidence.",
        body,
        "verify"
    )


# ============================================================
# HUMAN REVIEW
# ============================================================

@app.route("/review")
def review():

    if not STATE["candidate"]:
        return redirect(url_for("upload"))

    c = STATE["candidate"]

    body = f"""
    <div class="card">

        <div class="card-header">

            <div>
                <div class="card-title">
                    Human Review Workspace
                </div>

                <div class="card-sub">
                    Evidence is visible to a human reviewer.
                    The system does not make the final hiring decision.
                </div>
            </div>

            <span class="badge">
                HUMAN-IN-THE-LOOP
            </span>

        </div>


        <div class="profile-head"
             style="margin-bottom:20px;">

            <div class="avatar">
                {esc(initials(c["name"]))}
            </div>

            <div>

                <div class="profile-name">
                    {esc(c["name"])}
                </div>

                <div class="profile-role">
                    {esc(c["role"])}
                </div>

            </div>

        </div>


        <div class="table-wrap">

            <table>

                <thead>

                    <tr>
                        <th>Capability</th>
                        <th>Status</th>
                        <th>Evidence</th>
                        <th>Review</th>
                    </tr>

                </thead>

                <tbody>
    """

    for capability in STATE["capabilities"]:

        evidence = (
            capability["evidence"][0]
            if capability["evidence"]
            else "No direct evidence detected."
        )

        reviewed = STATE["review"].get(
            capability["name"]
        )

        review_text = (
            "Acknowledged"
            if reviewed == "acknowledged"
            else
            "More evidence requested"
            if reviewed == "more_evidence"
            else
            "Pending"
        )

        body += f"""

                    <tr>

                        <td>
                            <strong>
                                {esc(capability["name"])}
                            </strong>
                        </td>

                        <td>
                            {status_html(capability["status"])}
                        </td>

                        <td>
                            {esc(evidence[:230])}
                        </td>

                        <td>

                            <div style="
                                display:flex;
                                gap:6px;
                                flex-wrap:wrap;
                            ">

                                <button
                                    class="btn"
                                    onclick="reviewAction(
                                        '{esc(capability["name"])}',
                                        'acknowledged'
                                    )">
                                    Acknowledge
                                </button>

                                <button
                                    class="btn"
                                    onclick="reviewAction(
                                        '{esc(capability["name"])}',
                                        'more_evidence'
                                    )">
                                    Request Evidence
                                </button>

                            </div>

                            <div
                                style="
                                    margin-top:7px;
                                    color:#737b98;
                                    font-size:9px;
                                "
                                id="review-{esc(capability["name"]).replace(' ', '-')}"
                            >
                                Review: {esc(review_text)}
                            </div>

                        </td>

                    </tr>
        """

    body += """

                </tbody>

            </table>

        </div>

    </div>


    <div class="notice notice-info"
         style="margin-top:14px;">

        Final decision remains with the human reviewer.
        Capability Evidence OS provides evidence visibility,
        verification pathways and structured context.

    </div>


    <script>

    async function reviewAction(capability, action) {

        const response = await fetch(
            "/api/review-action",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    capability: capability,
                    action: action
                })
            }
        );

        const data = await response.json();

        if (data.success) {

            const id =
                "review-" +
                capability.replaceAll(" ", "-");

            const element =
                document.getElementById(id);

            if (element) {

                element.textContent =
                    "Review: " +
                    (
                        action === "acknowledged"
                        ? "Acknowledged"
                        : "More evidence requested"
                    );

            }

        }

    }

    </script>
    """

    return page(
        "Human Review",
        "Human Review",
        "AI makes evidence visible. Humans make the decision.",
        body,
        "review"
    )


# ============================================================
# API — START VERIFICATION
# ============================================================

@app.route(
    "/api/start-verification",
    methods=["POST"]
)
def api_start_verification():

    data = request.get_json(
        silent=True
    ) or {}

    capability_name = (
        data.get("capability")
    )

    capability = capability_by_name(
        capability_name
    )

    if not capability:

        return jsonify({
            "success": False,
            "message": "Capability not found."
        }), 404

    if capability["status"] == "Verified":

        return jsonify({
            "success": False,
            "message": "Capability is already verified."
        })

    STATE["verification"] = {
        "started": True,
        "completed": False,
        "capability": capability_name,
        "evidence": None,
        "started_at": datetime.now().isoformat(),
        "completed_at": None
    }

    return jsonify({
        "success": True,
        "capability": capability_name,
        "message": "Verification started."
    })


# ============================================================
# API — COMPLETE VERIFICATION
# ============================================================

@app.route(
    "/api/complete-verification",
    methods=["POST"]
)
def api_complete_verification():

    data = request.get_json(
        silent=True
    ) or {}

    capability_name = (
        data.get("capability")
    )

    evidence = (
        data.get("evidence") or ""
    ).strip()

    if not capability_name:

        return jsonify({
            "success": False,
            "message": "Capability is required."
        }), 400

    if not evidence:

        return jsonify({
            "success": False,
            "message": "Verification evidence is required."
        }), 400

    if not STATE["verification"]["started"]:

        return jsonify({
            "success": False,
            "message": "Start verification first."
        }), 400

    if (
        STATE["verification"]["capability"]
        != capability_name
    ):

        return jsonify({
            "success": False,
            "message": "Verification capability mismatch."
        }), 400

    capability = capability_by_name(
        capability_name
    )

    if not capability:

        return jsonify({
            "success": False,
            "message": "Capability not found."
        }), 404

    # --------------------------------------------------------
    # IMPORTANT:
    # This is DEMO verification.
    # It must not pretend that the system independently
    # validated a real-world credential.
    # --------------------------------------------------------

    capability["status"] = "Verified"

    demo_evidence = (
        "Practical Verification Task (Demo): "
        + evidence
    )

    capability["evidence"].append(
        demo_evidence
    )

    capability["matched_keywords"].append(
        "DEMO_VERIFICATION"
    )

    STATE["verification"]["completed"] = True
    STATE["verification"]["evidence"] = demo_evidence
    STATE["verification"]["completed_at"] = (
        datetime.now().isoformat()
    )

    return jsonify({
        "success": True,
        "capability": capability_name,
        "status": "Verified",
        "message": "Demo verification completed."
    })


# ============================================================
# API — HUMAN REVIEW ACTION
# ============================================================

@app.route(
    "/api/review-action",
    methods=["POST"]
)
def api_review_action():

    data = request.get_json(
        silent=True
    ) or {}

    capability = data.get(
        "capability"
    )

    action = data.get(
        "action"
    )

    allowed_actions = [
        "acknowledged",
        "more_evidence"
    ]

    if not capability:
        return jsonify({
            "success": False,
            "message": "Capability is required."
        }), 400

    if action not in allowed_actions:
        return jsonify({
            "success": False,
            "message": "Invalid review action."
        }), 400

    if not capability_by_name(capability):
        return jsonify({
            "success": False,
            "message": "Capability not found."
        }), 404

    STATE["review"][capability] = action

    return jsonify({
        "success": True,
        "capability": capability,
        "action": action
    })


# ============================================================
# API — RESET
# ============================================================

@app.route(
    "/api/reset",
    methods=["POST"]
)
def api_reset():

    reset_state()

    return redirect(
        url_for("home")
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "project": "Capability Evidence OS",
        "version": "V3",
        "candidate_loaded":
            STATE["candidate"] is not None,
        "capabilities":
            len(STATE["capabilities"]),
        "evidence_health":
            evidence_health()
    })


# ============================================================
# FILE SIZE ERROR
# ============================================================

@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(error):

    body = """
    <div class="card">

        <div class="notice notice-warning">
            Resume file is larger than the 10 MB limit.
        </div>

        <a href="/upload"
           class="btn btn-primary">
            Upload another resume
        </a>

    </div>
    """

    return page(
        "File Too Large",
        "Upload Limit Exceeded",
        "Maximum resume size is 10 MB.",
        body,
        "upload"
    ), 413


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 62)
    print("CAPABILITY EVIDENCE OS")
    print("SAP HACKFEST 2026 - V3")
    print("=" * 62)
    print()
    print("Dynamic Resume Intelligence")
    print("PDF → Text → Candidate → Evidence → Capability")
    print("→ Job → Gap → Verification → Human Review")
    print()
    print("Prototype running at:")
    print("http://127.0.0.1:5000")
    print()
    print("Upload your resume to begin.")
    print()
    print("Press CTRL+C to stop.")
    print("=" * 62)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )