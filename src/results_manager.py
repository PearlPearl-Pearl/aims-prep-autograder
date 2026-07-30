from pathlib import Path
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