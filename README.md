# Python Assignment Autograder

A lightweight, semi-automated marking system for Python programming assignments submitted as Jupyter notebooks (`.ipynb`).

The system automates the **objective, code-based portion** of marking while allowing tutors to retain manual control over qualitative assessment such as code quality, style, documentation, explanations, plagiarism/AI review, and other rubric criteria.

The system also generates per-student automated feedback and provides a separate tool for sending the completed feedback to students by email.

---

## Overview

Students submit their assignments as Jupyter notebooks using a prescribed filename format:

```text
student_identifier_ASSIGNMENT_CODE.ipynb
```

For example:

```text
pearl_kuuridong_PP1.ipynb
```

The student identifier is the root of the student's email address.

For example:

```text
sinyabe.joachim@gmail.com
```

corresponds to the identifier:

```text
sinyabe.joachim
```

and a `PP1` submission would therefore be:

```text
sinyabe.joachim_PP1.ipynb
```

The autograder then:

1. Discovers submitted files.
2. Validates their filenames and file types.
3. Extracts the student's identifier from the filename.
4. Converts valid notebooks into Python source files.
5. Runs instructor-defined `pytest` test cases against the submitted code.
6. Calculates an objective score using the assignment's marks configuration.
7. Saves the complete test result as JSON.
8. Updates an assignment-level CSV containing objective marks.
9. Generates a human-readable `.txt` feedback file containing the automated test results.

The email-sending component is deliberately separate from the marking workflow. Tutors can review and annotate student submissions before sending the final feedback.

---

# Project Structure

A typical project looks like:

```text
autograder/
│
├── main.py
├── email_sender.py
├── requirements.txt
├── .env
├── .gitignore
│
├── src/
│   ├── submissions_manager.py
│   ├── test_engine.py
│   ├── results_manager.py
│   └── feedback_generator.py
│
├── submissions/
│
├── assignments/
│   └── PP1/
│       ├── marks.json
│       └── tests/
│           └── test_add.py
│
├── results/
│   └── PP1/
│       ├── objective_marks.csv
│       ├── pearl_kuuridong.json
│       └── sinyabe.joachim.json
│
└── feedback/
    └── PP1/
        ├── pearl_kuuridong_PP1.txt
        ├── pearl_kuuridong_PP1.ipynb
        ├── sinyabe.joachim_PP1.txt
        └── sinyabe.joachim_PP1.ipynb
```

The `src/` directory contains the reusable components responsible for automated marking and feedback generation.

`email_sender.py` is kept at the project root because it is a **separate operational workflow** rather than part of the automated marking pipeline.

---

# Requirements

Python 3 is required.

Install the dependencies with:

```bash
python -m pip install -r requirements.txt
```

The project uses packages including:

* `pytest`
* `nbformat`
* `nbconvert`
* `python-dotenv`

---

# Running the Autograder

Place student submissions inside:

```text
submissions/assignment_code/
```

Then run:

```bash
python main.py PP1
```

For another assignment:

```bash
python main.py PP2
```

The assignment code determines which assignment directory, tests, and marks configuration are used.

---

# Submission Naming Convention

Students should use:

```text
student_identifier_ASSIGNMENT_CODE.ipynb
```

For example:

```text
pearl_kuuridong_PP1.ipynb
```

If the student's email address is:

```text
pearl_kuuridong@gmail.com
```

the identifier is:

```text
pearl_kuuridong
```

and the submission should be:

```text
pearl_kuuridong_PP1.ipynb
```

For an email containing a period:

```text
sinyabe.joachim@gmail.com
```

the identifier remains:

```text
sinyabe.joachim
```

and the submission should be:

```text
sinyabe.joachim_PP1.ipynb
```

The identifier should therefore be used **exactly as the root of the student's email address**, without modifying it.

The email sender relies on this convention to reconstruct the student's email address.

Incorrectly named submissions are treated as invalid and are not passed to the test engine.

---

# Submission Manager

`src/submissions_manager.py` is responsible for discovering and validating submissions.

It:

* scans the `submissions/` directory;
* ignores directories;
* checks that submissions are Jupyter notebooks;
* validates the assignment code in the filename;
* extracts the student identifier;
* records invalid submissions and the reason for rejection.

For example:

```text
pearl_kuuridong_PP1.ipynb
```

is valid when marking `PP1`.

However:

```text
pearl_kuuridong_PP2.ipynb
```

is rejected when running:

```bash
python main.py PP1
```

Likewise:

```text
randomfile.ipynb
```

is rejected because it does not follow the expected naming convention.

Non-notebook files are also reported as invalid.

---

# Test Engine

`src/test_engine.py` handles the objective marking process.

For each valid submission, it:

1. Locates the assignment's tests.
2. Loads the assignment's `marks.json`.
3. Converts the submitted notebook into Python source code.
4. Creates a temporary execution directory.
5. Runs the assignment's `pytest` test suite.
6. Collects the status of each test.
7. Associates each test with its allocated marks.
8. Calculates the student's objective score.

The submitted notebook is converted to:

```text
student_submission.py
```

inside a temporary directory.

The tests can therefore import the student's code normally:

```python
from student_submission import add
```

The temporary directory is removed after the tests finish.

---

# Writing Tests

Each assignment has its own test directory:

```text
assignments/
└── PP1/
    └── tests/
        └── test_add.py
```

Tests are written using `pytest`.

For example:

```python
from student_submission import add


def test_add_positive():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-2, -3) == -5


def test_add_zero():
    assert add(5, 0) == 5
```

Each test should represent an objectively assessable requirement of the assignment.

The test function names are important because they are used to associate test results with the marks configuration and automated feedback.

---

# Marks Configuration

Each assignment contains a `marks.json` file:

```text
assignments/
└── PP1/
    ├── marks.json
    └── tests/
        └── test_add.py
```

For example:

```json
{
    "test_add_positive": 2,
    "test_add_negative": 3,
    "test_add_zero": 5,
    "test_add_large_numbers": 4,
    "test_add_floats": 3,
    "test_add_strings": 3
}
```

The test names in `marks.json` must correspond to the names of the pytest functions.

In this example:

```text
Total objective mark = 20
```

---

# Results Manager

`src/results_manager.py` handles persistent storage of marking results.

Each student's complete automated result is stored as a JSON file:

```text
results/
└── PP1/
    ├── pearl_kuuridong.json
    └── sinyabe.joachim.json
```

The JSON result contains information such as:

* pytest return code;
* pytest standard output;
* pytest error output;
* individual test results;
* marks earned for each test;
* total objective score;
* total possible objective marks;
* student identifier;
* assignment code.

The results manager can also load previously saved results.

---

## Objective Marks CSV

The results manager also maintains:

```text
results/PP1/objective_marks.csv
```

The CSV contains:

```text
identifier,objective_score,total_marks
```

For example:

```csv
identifier,objective_score,total_marks
pearl_kuuridong,20,20
sinyabe.joachim,15,20
```

When a student's result is processed again, their existing row is replaced rather than duplicated.

The rows are kept alphabetically ordered by student identifier.

The CSV deliberately stores the **raw objective score and total marks**, rather than an objective percentage.

---

# Feedback Generator

`src/feedback_generator.py` generates human-readable automated feedback from the test results.

The feedback generator reads the assignment's test files and uses Python's `ast` module to extract information from test assertions.

For example:

```python
def test_add_positive():
    assert add(2, 3) == 5
```

produces feedback containing:

```text
Test:
test_add_positive

Input:
add(2, 3)

Expected:
5
```

The extracted test information is combined with the actual test result produced by the test engine.

---

## Generated Feedback

A generated feedback file may look like:

```text
Python Assignment PP1
Student: pearl_kuuridong

TEST FEEDBACK
=======================

1. test_add_positive
   Input:
   add(2, 3)

   Expected output:
   5

   Status: PASSED
```

The file is saved using:

```text
student_identifier_ASSIGNMENT_CODE.txt
```

For example:

```text
feedback/
└── PP1/
    └── pearl_kuuridong_PP1.txt
```

---

# Manual Review and Annotation

The automated feedback is not intended to replace human review.

For Python assignments, tutors may manually inspect each student's submission for:

* code quality;
* readability;
* documentation;
* variable naming;
* programming style;
* explanations;
* algorithmic approach;
* adherence to assignment instructions;
* plagiarism;
* inappropriate use of AI;
* other qualitative rubric criteria.

After reviewing a student's notebook, the tutor can save an annotated version of the submission in the same assignment feedback directory.

For example:

```text
feedback/
└── PP1/
    ├── pearl_kuuridong_PP1.txt
    ├── pearl_kuuridong_PP1.ipynb
    ├── sinyabe.joachim_PP1.txt
    └── sinyabe.joachim_PP1.ipynb
```

The `.txt` file contains the automated test feedback.

The `.ipynb` file contains the tutor's manually annotated submission.

These files together form the student's feedback package.

---

# Email Sender

`email_sender.py` is a standalone script located at the **project root**, not inside `src/`.

This is intentional.

The automated marking workflow and email distribution workflow are separate:

```text
main.py
    │
    ▼
Automated marking
    │
    ▼
Automated feedback
    │
    ▼
Human review / annotation
    │
    ▼
email_sender.py
    │
    ▼
Student
```

The email sender should **not** be called automatically from `main.py`.

This gives tutors a human checkpoint between automated marking and communication with students.

---

## Feedback Directory

The email sender expects completed feedback to be stored under:

```text
feedback/
└── PP1/
```

Files must follow the naming convention:

```text
student_identifier_ASSIGNMENT_CODE.extension
```

For example:

```text
pearl_kuuridong_PP1.txt
pearl_kuuridong_PP1.ipynb
```

or:

```text
sinyabe.joachim_PP1.txt
sinyabe.joachim_PP1.ipynb
```

The sender extracts the identifier by removing the assignment suffix.

For example:

```text
sinyabe.joachim_PP1.txt
```

becomes:

```text
sinyabe.joachim
```

The sender then reconstructs:

```text
sinyabe.joachim@gmail.com
```

---

## Grouping Attachments

The sender scans the assignment's feedback directory and groups files by student identifier.

For example:

```text
feedback/PP1/
├── pearl_kuuridong_PP1.txt
├── pearl_kuuridong_PP1.ipynb
├── sinyabe.joachim_PP1.txt
└── sinyabe.joachim_PP1.ipynb
```

is interpreted as:

```text
pearl_kuuridong
    ├── pearl_kuuridong_PP1.txt
    └── pearl_kuuridong_PP1.ipynb

sinyabe.joachim
    ├── sinyabe.joachim_PP1.txt
    └── sinyabe.joachim_PP1.ipynb
```

Each student receives **one email** containing all files associated with their identifier.

This means tutors do not need to manually select attachments for individual students.

---

# Running the Email Sender

The email sender is run independently:

```bash
python email_sender.py
```

Before running it, tutors should make sure that:

1. automated feedback has been generated;
2. submissions have been manually reviewed;
3. annotated notebooks have been placed in the feedback directory;
4. all files intended for students follow the required naming convention;
5. the assignment code in `email_sender.py` is correct.

The sender then scans the feedback directory and sends the completed feedback packages.

---

# Email Configuration

The email sender uses environment variables for the sender's Gmail credentials.

Create a `.env` file:

```env
EMAIL_ADDRESS=youraddress@gmail.com
EMAIL_PASSWORD=your_app_password
```

The `.env` file must not be committed to version control.

For Gmail, an **App Password** should be used rather than the normal account password.

The sender connects using:

```text
SMTP server: smtp.gmail.com
Port: 465
Connection: SSL
```

The sender currently assumes Gmail addresses:

```python
EMAIL_DOMAIN = "@gmail.com"
```

Because the student identifier is the root of the student's email address, a separate `emails.csv` file is not required.

For example:

```text
sinyabe.joachim
```

becomes:

```text
sinyabe.joachim@gmail.com
```

---

# Complete Workflow

The automated marking workflow is:

```text
Student Submissions
        │
        ▼
Submission Manager
        │
        ├──────── Invalid ───────► Reject
        │
        ▼
Test Engine
        │
        ▼
pytest Tests
        │
        ▼
Results Manager
        │
        ├────────► JSON results
        │
        └────────► objective_marks.csv
        │
        ▼
Feedback Generator
        │
        ▼
Automated .txt Feedback
        │
        ▼
Human Review
        │
        ▼
Annotated .ipynb
        │
        ▼
feedback/PP1/
        │
        ▼
email_sender.py
        │
        ▼
Student Email
```

The key separation is:

### Automated stage

```text
Submission
    ↓
Testing
    ↓
Objective Score
    ↓
Results
    ↓
Automated Feedback
```

### Human-controlled stage

```text
Review
    ↓
Annotation
    ↓
Approval
    ↓
Email
```

---

# Running the Complete Workflow

### 1. Run automated marking

```bash
python main.py PP1
```

This produces the JSON results, objective marks CSV, and automated `.txt` feedback.

### 2. Review submissions

Tutors inspect the submitted notebooks and perform any required manual assessment, including qualitative comments and plagiarism/AI review.

### 3. Save annotated submissions

Place the annotated notebooks in:

```text
feedback/PP1/
```

using the same filename convention:

```text
student_identifier_PP1.ipynb
```

### 4. Verify the feedback directory

For example:

```text
feedback/
└── PP1/
    ├── pearl_kuuridong_PP1.txt
    ├── pearl_kuuridong_PP1.ipynb
    ├── sinyabe.joachim_PP1.txt
    └── sinyabe.joachim_PP1.ipynb
```

### 5. Send the feedback

Run:

```bash
python email_sender.py
```

Each student receives one email with their complete feedback package attached.

---

# Design Philosophy

The system is intentionally **semi-automated**.

It automates repetitive and objectively verifiable work while leaving human judgment in the workflow.

The system does not attempt to:

* replace tutors;
* determine code quality automatically;
* make final qualitative judgments;
* automatically decide whether a student used AI;
* automatically determine plagiarism;
* send feedback immediately after automated marking.

Instead, it separates the workflow into two stages:

### Automated marking

```text
Test → Score → Save Result → Generate Feedback
```

### Human review and distribution

```text
Review → Annotate → Approve → Send
```

This separation gives tutors a deliberate opportunity to inspect the final feedback before it reaches students.

---

# Security Considerations

Student submissions are **untrusted code**.

The current implementation executes submitted Python code directly and should therefore be used in a controlled environment.

Student code may potentially:

* access files;
* consume system resources;
* execute arbitrary Python code;
* interact with the network;
* perform other operations available to the Python process.

The current implementation should **not** be considered a secure sandbox for arbitrary code execution.

For environments where submissions cannot be trusted, additional isolation should be implemented before deployment.

---

# Privacy and Sensitive Data

Student information should not be committed to a public repository.

This includes:

* student submissions;
* grades;
* test results;
* feedback;
* annotated notebooks;
* email addresses;
* `.env` files;
* other personally identifiable information.

A `.gitignore` should therefore contain:

```gitignore
# Student data
submissions/
results/
feedback/

# Credentials
.env

# Python generated files
__pycache__/
.pytest_cache/
*.pyc

# Virtual environments
.venv/
venv/
env/
```

The public repository should contain only reusable infrastructure and non-sensitive example data.

---

# Limitations

The current implementation makes several assumptions specific to the intended teaching workflow.

### Student identifiers

The student's submission identifier is assumed to be the root of their email address.

For example:

```text
sinyabe.joachim@gmail.com
```

corresponds to:

```text
sinyabe.joachim_PP1.ipynb
```

This allows the email sender to reconstruct the student's email address without maintaining a separate student-email database.

### Gmail

The current email sender is configured for Gmail SMTP and currently assumes Gmail student addresses.

### Python assignments

The automated feedback generator is designed specifically around Python assignments whose objective requirements are represented as `pytest` equality assertions.

### Test structure

The feedback generator currently extracts test information from straightforward equality assertions such as:

```python
assert function(x) == expected
```

More complicated test structures may not be represented fully in the generated feedback.

### Manual review

Qualitative assessment remains the responsibility of the tutor.

### Email sending

Email sending is intentionally manual and separate from automated marking. This prevents a marking run from automatically communicating with students before tutors have reviewed the results.

---

# Future Development

Possible future improvements include:

* richer automated feedback;
* improved handling of complex pytest assertions;
* final grade calculation combining objective and manual marks;
* richer CSV/Excel grade reports;
* assignment-level configuration files;
* tutor-specific configuration;
* configurable email templates;
* email delivery logging;
* resend/failed-delivery handling;
* marking statistics;
* improved execution isolation;
* stronger validation of assignment structure.

The current architecture is deliberately modular so these features can be added without replacing the core marking pipeline.
