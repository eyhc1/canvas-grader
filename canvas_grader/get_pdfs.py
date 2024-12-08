# Get student's reports from the processing folder, all should be in pdf format
import os
import shutil

from glob import glob
from docx2pdf import convert
from canvasapi import Canvas
from .cli import app, API_URL, API_KEY


@app.command()
def get_pdfs(course_id: int, api_url=API_URL, key=API_KEY, dest: str="reports"):
    """Extract report documents from processing folder and convert them to pdfs. The pdfs are then stored in the destnation folder.

    :param course_id: Canvas course id
    :type course_id: int
    :param api_url: Canvas url, defaults to API_URL
    :type api_url: str, optional
    :param key: Canvas API key, defaults to API_KEY
    :type key: str, optional
    :param dest: destnation folder, defaults to "reports"
    :type dest: str, optional
    """
    # Initialize a new Canvas object
    canvas = Canvas(api_url, key)

    course = canvas.get_course(course_id)

    os.makedirs(dest, exist_ok=True)

    matched_patterns = glob("processing/**/*eport*.*", recursive=True)
    for files in matched_patterns:
        # the studure for ALL should be "processing/{student_canvas_id}/<0_or_more_directies>/<some_report_doc_or_pdf>"
        # so assumed that the student_canvas_id is the second element in the path
        path = files.split("\\")
        name = course.get_user(path[1]).sortable_name.replace(", ", "_")
        if path[-1].endswith(".docx"):
            # convert doc to pdf when needed
            print(f"Converting {path[-1]}.docx to pdf")
            convert(files, f"{dest}/{name}.pdf")
        elif path[-1].endswith(".pdf"):
            # copy the file to the reports folder
            shutil.copy(files, f"{dest}/{name}.pdf")
