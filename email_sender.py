import os
import smtplib
from pathlib import Path
from collections import defaultdict
from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

FEEDBACK_DIR = Path("feedback")
ASSIGNMENT_CODE = "PP1"

EMAIL_DOMAIN = "@gmail.com"

SUBJECT_TEMPLATE = "Feedback on your Python Assignment {assignment}"

SENDER_NAME = "Your Instructor"


# ============================================================
# EMAIL SENDER
# ============================================================

class FeedbackSender:

    def __init__(
        self,
        feedback_dir: Path,
        assignment_code: str,
        email_domain: str = "@gmail.com"
    ):
        self.feedback_dir = Path(feedback_dir)
        self.assignment_code = assignment_code
        self.email_domain = email_domain

    def get_feedback_dir(self) -> Path:
        return (
            self.feedback_dir
            / self.assignment_code
        )

    def get_student_identifier(
        self,
        filename: str
    ) -> str | None:
        """
        Extract the student's email root from a filename.

        Example:

            j.nartey1000_PP1.txt
            -> j.nartey1000

            j.nartey1000_PP1.ipynb
            -> j.nartey1000
        """

        path = Path(filename)

        suffix = f"_{self.assignment_code}"

        name = path.stem

        if not name.endswith(suffix):
            return None

        return name[:-len(suffix)]

    def collect_files(self) -> dict[str, list[Path]]:
        """
        Group all feedback files by student identifier.

        Example:

        {
            "j.nartey1000": [
                Path("feedback/PP1/j.nartey1000_PP1.txt"),
                Path("feedback/PP1/j.nartey1000_PP1.ipynb")
            ]
        }
        """

        feedback_dir = self.get_feedback_dir()

        if not feedback_dir.exists():
            raise FileNotFoundError(
                f"Feedback directory not found: {feedback_dir}"
            )

        students = defaultdict(list)

        for file in feedback_dir.iterdir():

            if not file.is_file():
                continue

            identifier = self.get_student_identifier(
                file.name
            )

            if identifier is None:
                print(
                    f"Skipping file with unexpected name: "
                    f"{file.name}"
                )
                continue

            students[identifier].append(file)

        return dict(students)

    def build_email(
        self,
        identifier: str,
        files: list[Path]
    ) -> EmailMessage:

        student_email = (
            identifier
            + self.email_domain
        ).lower()

        message = EmailMessage()

        message["Subject"] = SUBJECT_TEMPLATE.format(
            assignment=self.assignment_code
        )

        message["From"] = EMAIL_ADDRESS
        message["To"] = student_email

        message.set_content(
            f"""Dear student,

Please find attached your feedback for Python Assignment {self.assignment_code}.

Your feedback contains the automated test results and the annotated submission where applicable.

Best,
{SENDER_NAME}
"""
        )

        for file in files:

            with file.open("rb") as attachment:
                file_data = attachment.read()

            message.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=file.name
            )

        return message

    def send(self) -> None:
        """
        Send feedback to every student represented in the
        feedback directory.
        """

        students = self.collect_files()

        if not students:
            print("No feedback files found.")
            return

        print(
            f"Found feedback for "
            f"{len(students)} student(s).\n"
        )

        counter = 0

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_PASSWORD
            )

            for identifier, files in sorted(
                students.items()
            ):

                student_email = (
                    identifier
                    + self.email_domain
                ).lower()

                message = self.build_email(
                    identifier,
                    files
                )

                smtp.send_message(message)

                counter += 1

                print(
                    f"Sent to {student_email}"
                )

                for file in files:
                    print(
                        f"    Attached: {file.name}"
                    )

        print(
            f"\n{counter} student(s) sent."
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    sender = FeedbackSender(
        feedback_dir=FEEDBACK_DIR,
        assignment_code=ASSIGNMENT_CODE
    )

    sender.send()