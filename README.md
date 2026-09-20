Capability Evidence OS

Evidence intelligence for inclusive workforce decisions.

Don't judge potential from a resume. Discover the evidence behind capability.

Capability Evidence OS is a Flask-based prototype built around a simple principle:
Unverified capability is not the same as absent capability.

The system extracts evidence from a candidate PDF resume, translates activities into capabilities, compares those capabilities with job requirements, identifies evidence gaps, proposes verification, and keeps the final decision with a human reviewer.

Core flow

Candidate → Evidence → Capability → Job → Gap → Verification → Human Review

What the prototype demonstrates

PDF resume upload and text extraction

Candidate profile extraction

Evidence and skill detection

Capability mapping with status such as Strong, Partial, Missing and Unverified

Evidence snippets linked to detected capabilities

Job requirement mapping for a Financial Analyst scenario

Evidence-gap detection

Practical capability verification workflow

Human review stage

Evidence health and command-center metrics

JSON API endpoints for verification and review actions

/health endpoint for a simple application health check

Product principle

The prototype is designed to support human review, not replace it.

When evidence is insufficient, the system surfaces the gap and creates a path to verification instead of automatically treating the capability as absent.

Tech stack

Python

Flask

pypdf

HTML/CSS/JavaScript

Server-side in-memory demo state

Run locally

1. Create a virtual environment

Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

2. Install dependencies

pip install -r requirements.txt

3. Start the application

python app.py

Open:

http://127.0.0.1:5000

4. Demo flow

Open Evidence Intake.

For a quick demo, use demo/Ananya_Demo_Resume.pdf.

Upload a readable PDF resume.

Open Candidate to view the extracted profile.

Open Evidence Intelligence to inspect evidence.

Open Job Requirements to compare the candidate with a Financial Analyst role.

Open Evidence Gaps to see unverified or missing evidence.

Use Verification to create and complete a practical verification task.

Use Human Review for the final review state.

Important prototype limitations

State is stored in memory and resets when the application restarts.

Resume processing currently supports text-based PDFs; scanned image-only PDFs may not produce extractable text.

This is a demonstration prototype, not a production hiring system.

No real hiring decision should be made automatically from the prototype output.

Repository structure

Capability_Evidence_OS/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── uploads/
    └── .gitkeep

Hackathon context

Created as a prototype for SAP HackFest 2026 — Theme 2: Inclusive Workforce.

The project explores an evidence-intelligence layer that can sit around an enterprise system of record and make human capability more visible, verifiable and reviewable.

Suggested project description for GitHub

A Flask-based capability intelligence prototype that extracts evidence from resumes, maps experience to capabilities, detects evidence gaps, proposes verification tasks, and keeps final workforce decisions with humans.