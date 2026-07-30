from pathlib import Path
import json
import subprocess
import tempfile
import sys
import nbformat
from nbconvert import PythonExporter

class TestEngine:

    def __init__(self, assignments_dir: Path):
        self.assignments_dir = Path(assignments_dir)

    def get_assignment_dir(self, assignment_code: str) -> Path:
        return self.assignments_dir / assignment_code

    def get_tests_dir(self, assignment_code: str) -> Path:
        return self.get_assignment_dir(assignment_code) / "tests"

    def get_marks_file(self, assignment_code: str) -> Path:
        return self.get_assignment_dir(assignment_code) / "marks.json"

    def load_marks(self, assignment_code: str) -> dict:
        marks_file = self.get_marks_file(assignment_code)

        if not marks_file.exists():
            raise FileNotFoundError(
                f"Marks file not found: {marks_file}"
            )

        with marks_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def convert_notebook(self, notebook_path: Path, output_dir: Path) -> Path:
        """Convert a Jupyter notebook directly to a Python file."""

        notebook_path = Path(notebook_path)
        output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "student_submission.py"

        with notebook_path.open("r", encoding="utf-8") as file:
            notebook = nbformat.read(file, as_version=4)

        exporter = PythonExporter()

        python_code, _ = exporter.from_notebook_node(notebook)

        output_file.write_text(
            python_code,
            encoding="utf-8"
        )

        return output_file


    def run_tests(
        self,
        notebook_path: Path,
        assignment_code: str
    ) -> dict:
        """Run pytest against a student's notebook."""

        tests_dir = self.get_tests_dir(assignment_code).resolve()
        marks = self.load_marks(assignment_code)

        if not tests_dir.exists():
            raise FileNotFoundError(
                f"Tests directory not found: {tests_dir}"
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_dir = Path(temp_dir)

            self.convert_notebook(
                notebook_path,
                runtime_dir
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(tests_dir),
                    "-v",
                ],
                cwd=runtime_dir,
                capture_output=True,
                text=True,
            )

            test_results = self.collect_results(
                result.stdout,
                marks
            )

            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "tests": test_results,
                "objective_score": sum(
                    test["earned"]
                    for test in test_results
                ),
                "total_marks": sum(marks.values()),
            }

    def collect_results(
        self,
        pytest_output: str,
        marks: dict
    ) -> list:
        """
        Extract test results from pytest output and
        associate each test with its allocated marks.
        """

        results = []

        for test_name, test_marks in marks.items():

            passed = f"::{test_name} PASSED" in pytest_output

            results.append({
                "test": test_name,
                "passed": passed,
                "possible": test_marks,
                "earned": test_marks if passed else 0
            })

        return results


if __name__ == "__main__":

    engine = TestEngine(
        assignments_dir=Path("..", "assignments")
    )

    result = engine.run_tests(
        notebook_path=Path(
            "..",
            "submissions",
            "pearl_kuuridong_PP1.ipynb"
        ),
        assignment_code="PP1"
    )

    for test in result["tests"]:
        print(
            f"{test['test']}: "
            f"{test['earned']}/{test['possible']}"
        )

    print(
        f"\nObjective score: "
        f"{result['objective_score']}/"
        f"{result['total_marks']}"
    )