from pathlib import Path


def extract_student_identifier(filename: str, assignment_code: str) -> str:
    name_wo_extension = Path(filename).stem
    suffix = f"_{assignment_code}"

    if not name_wo_extension.endswith(suffix):
        raise ValueError(
            f"Filename '{filename}' does not match assignment '{assignment_code}'."
        )

    return name_wo_extension[:-len(suffix)]


def get_submissions(submissions_dir: Path, assignment_code: str):
    submissions = []

    for file in submissions_dir.iterdir():
        if not file.is_file():
            continue

        submission = {
            "file": file,
            "identifier": None,
            "assignment": assignment_code,
            "valid": False,
            "reason": None
        }

        if file.suffix != ".ipynb":
            submission["reason"] = "Invalid file type"
            submissions.append(submission)
            continue

        try:
            submission["identifier"] = extract_student_identifier(
                file.name,
                assignment_code
            )
            submission["valid"] = True

        except ValueError as error:
            submission["reason"] = str(error)

        submissions.append(submission)

    return submissions