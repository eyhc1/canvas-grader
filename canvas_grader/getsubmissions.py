import os
import multiprocessing

from canvasapi import Canvas
from .cli import app, API_URL, API_KEY

# Number of threads to download (half of the available threads)
MAX_THREADS = int(os.cpu_count() / 2)  

@app.command()
def download_submissions(course_id: str, assignment_id: str, folder_path: str, api_url: str=API_URL, api_key: str=API_KEY):
    """Download all the submissions for a given assignment

    :param course_id: Canvas course id
    :type course_id: str
    :param assignment_id: Canvas assignment id
    :type assignment_id: str
    :param folder_path: Folder path to save the submissions
    :type folder_path: str
    :param api_url: Canvas API url, defaults to https://canvas.uw.edu/
    :type api_url: str, optional
    :param api_key: Canvas API key, defaults to API_KEY
    :type api_key: str, optional
    """
    
    # Initialize a new Canvas object
    canvas = Canvas(api_url, api_key)

    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)

    submissions = assignment.get_submissions()
       
    pool = multiprocessing.Pool(processes=MAX_THREADS)
    res = []
    for submission in submissions:
        files = assignment.get_submission(submission.user_id).attachments
        if len(files) == 1:
            res.append(pool.apply_async(download, args=(files, f"{folder_path}/{submission.user_id}.zip")))
            
    pool.close()
    pool.join()

def download(attachments, dest):
    print(f"Downloading to {dest}")
    attachments[0].download(dest)
    print(f"done downloading to {dest}")
    
@app.command()
def rename2api(dirs: str):
    """rename canvas submission files format into just canvas student id (not netid!)

    :param dirs: directory containing the files/folders to be renamed
    :type dirs: str
    """

    submissions = os.listdir(dirs)

    renamed = 0

    for i in submissions:
        names = i.split("_")
        # go to next element if id is not a number.. we have the assumption that the first number is the canvas student id
        for name in names:
            if name.isdigit():
                new_name = f"{dirs}/{name}"
                if not os.path.exists(new_name):
                    os.rename(f"{dirs}/{i}", new_name)
                    renamed += 1
                else:
                    print(f"File {new_name} already exists!")
                    # attempt to rename the file
                    try:
                        os.remove(f"{dirs}/{i}")
                    except PermissionError:
                        print(f"Cannot remove {dirs}/{i}. Please remove it manually")
                break

    print(f"Renamed {renamed} students' submissions")
