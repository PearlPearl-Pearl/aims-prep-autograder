# Python Assignment Autograder

A lightweight, semi-automated marking system for Python programming assignments submitted as Jupyter notebooks (`.ipynb`).

The system automates the **objective, code-based portion** of marking while allowing instructors to retain manual control over qualitative assessment such as code quality, style, documentation, and other rubric criteria.

---

## Overview

Students submit their assignments as Jupyter notebooks using a prescribed filename format:

```text
student_identifier_ASSIGNMENT_CODE.ipynb
```

For example:

```text
firstname_lastname_PP1.ipynb
```

The autograder then:

1. Discovers submitted files.
2. Validates their filenames and file types.
3. Converts valid notebooks into Python files.
4. Runs instructor-defined `pytest` test cases against the submitted code.
5. Calculates an objective score using a marks configuration.
6. Reports the results for each submission.

Invalid submissions are not tested.

The system deliberately does **not** attempt to replace manual marking. The automated score is intended to form one component of the final grade.

---

## Project Structure

A typical project looks like this:

```text
autograder/
│
├── main.py
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── submissions_manager.py
│   └── test_engine.py
│
├── submissions/
│   └── student_assignment.ipynb
│
└── assignments/
    └── PP1/
        ├── marks.json
        └── tests/
            └── test_add.py
```

Student-specific data such as submissions, emails, grades, and feedback should not be committed to the repository.

---

## Requirements

Python 3 is required.

All Python dependencies are listed in:

```text
requirements.txt
```

Install them with:

```bash
python -m pip install -r requirements.txt
```

---

## Running the Autograder

Place the submissions to be marked inside:

```text
submissions/
```

Then run:

```bash
python main.py PP1
```

To mark another assignment:

```bash
python main.py PP2
```

The assignment code determines which tests and marking configuration are used.

---

## Submission Naming Convention

Students should follow a strict naming convention:

```text
student_identifier_ASSIGNMENT_CODE.ipynb
```

For example, for assignment `PP1`:

```text
firstname_lastname_PP1.ipynb
```

If an identifier is based on an email address, periods in the identifier can be replaced with underscores.

For example:

```text
firstname.lastname@example.com
```

could correspond to:

```text
firstname_lastname_PP1.ipynb
```

The exact naming convention should be communicated to students before submissions open.

Incorrectly named submissions are treated as invalid and are not passed to the test engine.

---

## Submission Manager

`src/submissions_manager.py` is responsible for discovering and validating submissions.

It checks:

* whether the submission is a file;
* whether it is a Jupyter notebook;
* whether the filename follows the required naming convention;
* whether the assignment code matches the assignment currently being marked.

For example:

```text
pearl_kuuridong_PP1.ipynb
```

is valid when marking `PP1`.

However:

```text
pearl_kuuridong_PP2.ipynb
```

is rejected when marking `PP1`.

---

## Test Engine

`src/test_engine.py` handles the objective marking process.

It:

* loads the assignment's marking configuration;
* converts submitted notebooks into Python source files;
* executes the instructor's `pytest` test suite;
* determines which tests passed;
* calculates the objective score.

The converted student submission is made available to the tests as:

```python
from student_submission import ...
```

Test authors therefore do not need to know where the temporary student file is stored.

---

## Writing Tests

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

---

## Marks Configuration

Each assignment contains a `marks.json` file:

```text
assignments/
└── PP1/
    ├── marks.json
    └── tests/
        └── test_add.py
```

The file assigns marks to individual tests.

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

In this example, the total objective mark is:

```text
20
```

---

## Example Output

A successful run might look like:

```text
Processing: studentname_coursecode.ipynb

============================= test session starts =============================
collected 6 items

test_add.py::test_add_positive PASSED
test_add.py::test_add_negative PASSED
test_add.py::test_add_zero PASSED
test_add.py::test_add_large_numbers PASSED
test_add.py::test_add_floats PASSED
test_add.py::test_add_strings PASSED

============================== 6 passed ==============================

Objective score: 20/20
```

Invalid submissions are reported separately:

```text
Processing: randomfile.ipynb
INVALID: Filename 'randomfile.ipynb' does not match assignment 'PP1'.
```

---

## Manual Marking

The system is intentionally **semi-automated**.

Automated tests handle objective criteria such as:

* expected outputs;
* required functionality;
* edge cases;
* function behaviour;
* other objectively testable requirements.

The instructor can then manually assess qualitative criteria such as:

* code quality;
* readability;
* documentation;
* variable naming;
* programming style;
* algorithmic approach;
* explanations;
* adherence to assignment instructions.

This allows the instructor to combine automated and manual assessment when determining the final grade.

---

## Design Philosophy

The system intentionally keeps the architecture simple.

The core workflow is:

```text
Submission
    │
    ▼
Submission Manager
    │
    ├── Invalid ──────────────► Reject
    │
    ▼
Valid Notebook
    │
    ▼
Notebook → Python
    │
    ▼
Test Engine
    │
    ▼
pytest Tests
    │
    ▼
Objective Score
    │
    ▼
Manual Assessment
    │
    ▼
Final Grade
```

The goal is not to build a complete learning management system or replace the instructor.

The goal is to eliminate repetitive code execution and objective checking while keeping the instructor in control of the final assessment.

---

## Security Considerations

Student submissions are **untrusted code**.

The current implementation executes submitted Python code directly and should therefore be used in a controlled environment.

Student code may potentially:

* access files;
* consume system resources;
* execute arbitrary Python code;
* interact with the network.

This project should **not** be considered a secure sandbox for arbitrary code execution.

For environments where submissions cannot be trusted, additional isolation or sandboxing should be implemented before using the system.

---

## Privacy and Sensitive Data

Student information should not be committed to a public repository.

This includes:

* email addresses;
* names;
* submissions;
* grades;
* feedback;
* student-specific configuration;
* other personally identifiable information.

For example, `.gitignore` can contain:

```gitignore
# Student data
emails.csv
submissions/
results/
feedback/

# Temporary files
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

## Future Development

The current version focuses on the core objective-marking mechanism.

Potential future components include:

* automated feedback generation;
* per-test feedback;
* final grade calculation;
* CSV/Excel grade reports;
* email feedback;
* submission statistics;
* assignment configuration;
* logging;
* improved error handling;
* stronger isolation for student code execution.

These can be developed independently while preserving the current separation between submission management and test execution.

---