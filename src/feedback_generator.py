from pathlib import Path
import ast


class FeedbackGenerator:

    def __init__(
        self,
        assignments_dir: Path,
        feedback_dir: Path
    ):
        self.assignments_dir = Path(assignments_dir)
        self.feedback_dir = Path(feedback_dir)

    def get_tests_dir(self, assignment_code: str) -> Path:
        return (
            self.assignments_dir
            / assignment_code
            / "tests"
        )

    def get_test_files(
        self,
        assignment_code: str
    ) -> list[Path]:

        tests_dir = self.get_tests_dir(
            assignment_code
        )

        if not tests_dir.exists():
            raise FileNotFoundError(
                f"Tests directory not found: {tests_dir}"
            )

        return sorted(
            tests_dir.glob("test_*.py")
        )

    def extract_tests(
        self,
        assignment_code: str
    ) -> list[dict]:

        test_files = self.get_test_files(
            assignment_code
        )

        tests = []

        for test_file in test_files:

            source = test_file.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(source)

            for node in ast.walk(tree):

                if not isinstance(
                    node,
                    ast.FunctionDef
                ):
                    continue

                if not node.name.startswith("test_"):
                    continue

                test_data = self.extract_test_case(
                    node
                )

                if test_data is not None:
                    test_data["test_file"] = (
                        test_file.name
                    )

                    tests.append(test_data)

        return tests

    def extract_test_case(
        self,
        test_function: ast.FunctionDef
    ) -> dict | None:

        for node in ast.walk(test_function):

            if not isinstance(
                node,
                ast.Assert
            ):
                continue

            assertion = node.test

            if not isinstance(
                assertion,
                ast.Compare
            ):
                continue

            if (
                len(assertion.ops) != 1
                or not isinstance(
                    assertion.ops[0],
                    ast.Eq
                )
                or len(assertion.comparators) != 1
            ):
                continue

            actual_expression = assertion.left
            expected_expression = (
                assertion.comparators[0]
            )

            return {
                "test": test_function.name,
                "input": ast.unparse(
                    actual_expression
                ),
                "expected": ast.unparse(
                    expected_expression
                )
            }

        return None

    def combine_results(
    self,
    assignment_code: str,
    result: dict
    ) -> list[dict]:

        test_definitions = self.extract_tests(
            assignment_code
        )

        result_by_test = {
            test["test"]: test
            for test in result["tests"]
        }

        combined = []

        for test in test_definitions:

            test_name = test["test"]

            marking_result = result_by_test.get(
                test_name
            )

            if marking_result is None:
                continue

            combined.append({
                "test": test_name,
                "input": test["input"],
                "expected": test["expected"],
                "status": marking_result["status"]
            })

        return combined

    def generate_feedback_text(
    self,
    identifier: str,
    assignment_code: str,
    result: dict
    ) -> str:

        tests = self.combine_results(
            assignment_code,
            result
        )

        lines = [
            f"Python Assignment {assignment_code}",
            f"Student: {identifier}",
            "",
            "TEST FEEDBACK",
            "=======================",
            ""
        ]

        for index, test in enumerate(tests, start=1):

            status = (
                "PASSED"
                if test["status"] == "passed"
                else "FAILED"
            )

            lines.extend([
                f"{index}. {test['test']}",
                f"   Input:",
                f"   {test['input']}",
                "",
                f"   Expected output:",
                f"   {test['expected']}",
                "",
                f"   Status: {status}",
                "",
                ""
            ])

        lines.extend([
            "Please review the failed test cases and investigate why",
            "your implementation does not produce the expected results.",
            ""
        ])

        return "\n".join(lines)

    def save_feedback(
    self,
    identifier: str,
    assignment_code: str,
    result: dict
    ) -> Path:

        assignment_dir = (
            self.feedback_dir
            / assignment_code
        )

        assignment_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        feedback_file = (
            assignment_dir
            / f"{identifier}.txt"
        )

        feedback_text = self.generate_feedback_text(
            identifier,
            assignment_code,
            result
        )

        feedback_file.write_text(
            feedback_text,
            encoding="utf-8"
        )

        return feedback_file




if __name__ == "__main__":

    from src.test_engine import TestEngine

    generator = FeedbackGenerator(
        assignments_dir=Path("assignments"),
        feedback_dir=Path("feedback")
    )

    engine = TestEngine(
        assignments_dir=Path("assignments")
    )

    result = engine.run_tests(
        notebook_path=Path(
            "submissions",
            "millicent_ayantoya_PP1.ipynb"
        ),
        assignment_code="PP1"
    )

    feedback_file = generator.save_feedback(
        identifier="millicent_ayantoya",
        assignment_code="PP1",
        result=result
    )

    print(f"Feedback saved to: {feedback_file}")