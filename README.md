# Capability Evidence OS

### Evidence-Driven Capability Intelligence for an Inclusive Workforce

> **“Don’t judge potential from a resume. Discover the evidence behind capability.”**

Capability Evidence OS is a Flask-based prototype that helps organizations look beyond traditional resume claims by connecting a candidate's experience with evidence, capabilities, job requirements, and verification pathways.

The system is designed around a simple principle:

**Missing evidence does not always mean missing capability.**

Instead of automatically rejecting a candidate when evidence is incomplete, the system identifies the evidence gap and suggests a practical way to verify the capability while keeping the final decision with a human reviewer.

---

## Problem

Traditional recruitment systems often depend heavily on:

* Resume keywords
* Job titles
* Years of experience
* Career history
* Static qualifications

However, these signals may not fully represent what a person can actually do.

Career gaps, non-traditional experience, career transitions, and incomplete resumes can make valuable capabilities difficult to discover.

---

## Solution

Capability Evidence OS creates an evidence-driven workflow:

**Candidate → Evidence → Capability → Job Requirement → Gap → Verification → Human Review**

The system extracts available information from candidate resumes, identifies evidence related to capabilities, compares those capabilities with job requirements, and highlights areas where additional verification may be useful.

The system is designed to **support human decision-making, not replace it.**

---

## Key Features

### Resume / PDF Processing

Upload a candidate resume and extract relevant text for analysis.

### Evidence Detection

Identify experience, projects, certifications, skills, and other evidence from available candidate information.

### Capability Mapping

Translate evidence into structured capabilities that can be compared with job requirements.

### Job Requirement Mapping

Compare candidate capabilities with the requirements of a target role.

### Evidence Gap Detection

Identify capabilities where supporting evidence is missing, weak, or requires further verification.

### Verification Workflow

Recommend practical verification methods such as assessments, work samples, or other evidence sources.

### Human-in-the-Loop Review

Keep the final evaluation with a human reviewer instead of making an automatic hiring decision.

---

## Prototype Workflow

```text
Candidate
    ↓
Evidence
    ↓
Capability
    ↓
Job Requirement
    ↓
Evidence Gap
    ↓
Verification
    ↓
Human Review
```

---

## Example Scenario

Consider a candidate returning to work after a career gap.

Her previous experience may show evidence of:

* Financial reporting
* Budgeting
* Documentation
* Coordination
* Excel

For a Financial Analyst role, the system may identify:

```text
Financial Reporting    → Evidence Found
Budgeting              → Evidence Found
Advanced Excel         → Additional Evidence Needed
Data Analysis          → Additional Evidence Needed
```

Instead of treating the missing evidence as an automatic rejection, the system can recommend a practical verification step.

This creates a more evidence-driven evaluation process.

---

## Screenshots

### Candidate Profile

![Candidate Profile](screenshots/candidate.png)

### Evidence Intelligence

![Evidence Intelligence](screenshots/evidence.png)

### Capability Mapping

![Capability Mapping](screenshots/capability.png)

### Evidence Gap

![Evidence Gap](screenshots/gap.png)

### Verification

![Verification](screenshots/verification.png)

### Human Review

![Human Review](screenshots/human-review.png)

> If your actual screenshot filenames are different, update the filenames in this section accordingly.

---

## Technology Stack

| Technology     | Purpose                             |
| -------------- | ----------------------------------- |
| Python         | Application logic                   |
| Flask          | Web application framework           |
| HTML           | Interface structure                 |
| CSS            | Interface styling                   |
| JavaScript     | Client-side interactions            |
| PDF Processing | Resume text extraction              |
| Git & GitHub   | Version control and project hosting |

---

## Project Architecture

```text
                    ┌──────────────────────┐
                    │     Candidate        │
                    │    Resume / PDF      │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │   Evidence Detection │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │  Capability Mapping  │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Job Requirement Map  │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │   Evidence Gap      │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │    Verification      │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │    Human Review      │
                    └──────────────────────┘
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Pardhu89068/Capability-Evidence-OS.git
```

```bash
cd Capability-Evidence-OS
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

### 5. Open the application

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## Demo Flow

The prototype can be demonstrated using the following flow:

```text
1. Open the application
2. Select Candidate
3. Upload / use the demo resume
4. Review extracted evidence
5. View capability mapping
6. Select a target job
7. Review evidence gaps
8. Open verification workflow
9. Review verified evidence
10. Continue to Human Review
```

---

## Design Principle

Capability Evidence OS follows a human-centered approach.

The system does not attempt to make the final hiring decision.

Instead:

```text
AI / Automation
      ↓
Finds and organizes evidence
      ↓
Identifies capability signals
      ↓
Highlights evidence gaps
      ↓
Suggests verification
      ↓
Human Review
      ↓
Final Decision
```

### Core Principle

> **AI makes the evidence visible. Humans make the decision.**

---

## Inclusive Workforce

The project is designed around the idea that capability can exist beyond what is immediately visible on a traditional resume.

It can help surface evidence for candidates with:

* Career gaps
* Career transitions
* Non-traditional experience
* Different learning pathways
* Incomplete or keyword-light resumes
* Skills demonstrated through projects or practical work

The goal is not to lower hiring standards.

The goal is to make capability **more visible and verifiable**.

---

## Future Scope

Potential future improvements include:

* Enterprise HR system integration
* Advanced capability extraction using modern AI models
* Verified digital credentials
* Skill assessments and work-sample verification
* Multilingual candidate support
* Explainable capability scoring
* Enterprise analytics
* Role-specific verification workflows
* Secure evidence storage
* Integration with enterprise workforce platforms

---

## Current Status

**Prototype / Proof of Concept**

The current version demonstrates the core workflow from candidate evidence collection through capability mapping, evidence-gap detection, verification, and human review.

Enterprise integrations and production-scale deployment are future development areas.

---

## Project Context

Developed as a prototype for:

**SAP HackFest 2026 — Theme 2: Inclusive Workforce**

The project explores how evidence-driven capability intelligence can complement existing workforce and recruitment processes.

---

## Contributors

This project was developed collaboratively.

* Pardhu
* Project Collaborator

See the GitHub repository contributor history for the latest contribution information.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Final Thought

**A resume tells us what a candidate claims.**

**Evidence helps us understand what a candidate can demonstrate.**

Capability Evidence OS explores the layer between the two.
