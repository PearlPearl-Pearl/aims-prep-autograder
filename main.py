from pathlib import Path
import argparse

from src.submissions_manager import get_submissions
from src.test_engine import TestEngine


SUBMISSIONS_DIR = Path("submissions")
ASSIGNMENTS_DIR = Path("assignments")


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

        print(result["stdout"])

        if result["stderr"]:
            print("ERRORS:")
            print(result["stderr"])

        print(
            f"Objective score: "
            f"{result['objective_score']}/"
            f"{result['total_marks']}"
        )


if __name__ == "__main__":
    main()
