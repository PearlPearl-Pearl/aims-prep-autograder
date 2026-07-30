from pathlib import Path
import argparse

from src.submissions_manager import get_submissions
from src.test_engine import TestEngine
from src.results_manager import ResultsManager


SUBMISSIONS_DIR = Path("submissions")
ASSIGNMENTS_DIR = Path("assignments")
RESULTS_DIR = Path("results")


def main():
    parser = argparse.ArgumentParser(
        description="Run automated marking for an assignment."
    )

    parser.add_argument(
        "assignment_code",
        help="Assignment code, e.g. PP1"
    )

    args = parser.parse_args()

    assignment_code = args.assignment_code

    submissions = get_submissions(
        submissions_dir=SUBMISSIONS_DIR,
        assignment_code=assignment_code
    )

    engine = TestEngine(
        assignments_dir=ASSIGNMENTS_DIR
    )

    results_manager = ResultsManager(
        results_dir=RESULTS_DIR
    )

    for submission in submissions:

        print(
            f"\nProcessing: "
            f"{submission['file'].name}"
        )

        if not submission["valid"]:
            print(
                f"INVALID: "
                f"{submission['reason']}"
            )
            continue

        result = engine.run_tests(
            notebook_path=submission["file"],
            assignment_code=submission["assignment"]
        )

        result["identifier"] = submission["identifier"]
        result["assignment"] = submission["assignment"]

        results_manager.save_result(result)

        print(result["stdout"])

        if result["stderr"]:
            print("ERRORS:")
            print(result["stderr"])

        print(
            f"Objective score: "
            f"{result['objective_score']}/"
            f"{result['total_marks']}"
        )

        print("\nSaved result:")
        print(result)


if __name__ == "__main__":
    main()
