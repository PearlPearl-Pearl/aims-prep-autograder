from pathlib import Path
import csv
import json


class ResultsManager:

    def __init__(self, results_dir: Path):
        self.results_dir = Path(results_dir)

    def save_result(self, result: dict) -> None:
        """
        Save a student's result as a JSON file.
        """

        assignment = result["assignment"]
        identifier = result["identifier"]

        assignment_dir = self.results_dir / assignment
        assignment_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        result_file = assignment_dir / f"{identifier}.json"

        with result_file.open("w", encoding="utf-8") as file:
            json.dump(
                result,
                file,
                indent=4
            )

    def load_result(
        self,
        assignment: str,
        identifier: str
    ) -> dict:
        """
        Load a student's saved result.
        """

        result_file = (
            self.results_dir
            / assignment
            / f"{identifier}.json"
        )

        with result_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def get_assignment_results(
        self,
        assignment: str
    ) -> list[dict]:
        """
        Load all saved results for an assignment.
        """

        assignment_dir = self.results_dir / assignment

        if not assignment_dir.exists():
            return []

        results = []

        for result_file in assignment_dir.glob("*.json"):
            with result_file.open("r", encoding="utf-8") as file:
                results.append(json.load(file))

        return results

    def update_summary(self, result: dict) -> None:
        """
        Add or update a student's objective mark in the
        assignment summary CSV.
        """

        assignment = result["assignment"]
        identifier = result["identifier"]

        assignment_dir = self.results_dir / assignment
        assignment_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        summary_file = assignment_dir / "objective_marks.csv"

        rows = []

        # Load existing records if the CSV already exists
        if summary_file.exists():
            with summary_file.open(
                "r",
                encoding="utf-8",
                newline=""
            ) as file:
                reader = csv.DictReader(file)
                rows = list(reader)

        # Remove an existing record for this student
        # so rerunning the grader doesn't create duplicates.
        rows = [
            row
            for row in rows
            if row["identifier"] != identifier
        ]

        # Add the latest result
        rows.append({
            "identifier": identifier,
            "objective_score": result["objective_score"],
            "total_marks": result["total_marks"],
            # "objective_percentage": round(
            #     result["objective_score"]
            #     / result["total_marks"]
            #     * 100,
            #     2
            # )
        })

        # Keep students alphabetically ordered
        rows.sort(
            key=lambda row: row["identifier"].lower()
        )

        with summary_file.open(
            "w",
            encoding="utf-8",
            newline=""
        ) as file:

            fieldnames = [
                "identifier",
                "objective_score",
                "total_marks",
                # "objective_percentage"
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(rows)