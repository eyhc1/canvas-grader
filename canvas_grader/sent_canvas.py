import os
import json

from glob import glob
from canvasapi import Canvas
from rich import print
from .cli import app, API_URL, API_KEY


@app.command()
def set_comments(course_id: int, assignment_id: int, api_url=API_URL, key=API_KEY, results: str="processing", for_canvas: str="for_canvas.txt"):
    """Send autograder for_canvas.txt comments to Canvas. Comments should be somewhere in the <results>/<student_canvas_id> folder

    :param course_id: Canvas API course id
    :type course_id: int
    :param assignment_id: Canvas API assignment id
    :type assignment_id: int
    :param api_url: Canvas API URL, defaults to API_URL
    :type api_url: str
    :param key: Canvas API Key, defaults to API_KEY
    :type key: str
    :param results: Results directory, defaults to "processing"
    :type results: str, optional
    :param for_canvas: for_canvas.txt comments. defaults to "for_canvas.txt"
    :type results: str, optional
    :return: Students whose comments are not found
    :rtype: List
    """
    canvas = Canvas(api_url, key)

    course = canvas.get_course(course_id)

    assignment = course.get_assignment(assignment_id)
    # post comments
    students = os.listdir(results)
    missing_comments = []
    for i in students:
        sid = i.split(".")[0]
        
        
        canvas_comments = glob(f"{results}/{i}/**/{for_canvas}", recursive=True)
        if len(canvas_comments) == 0:
            missing_comments.append(sid)
            continue
        comment = open(canvas_comments[0]).read()

        submission = assignment.get_submission(sid, include=["rubric_assessment", "user"])
        submission.edit(comment={"text_comment": comment})
        
    return missing_comments
        
        
@app.command()
def set_grades(course_id: int, assignment_id: int, api_url=API_URL, key=API_KEY, outputs: str="processing"):
    """Sent autograder's grade to an assignment in Canvas. The grades should be in the <outputs> folder and the file name should be the student's canvas id. You should have the grade rubric set in the assignment.

    :param course_id: Canvas API course id
    :type course_id: int
    :param assignment_id: Canvas API assignment id
    :type assignment_id: int
    :param api_url: Canvas API URL, defaults to API_URL
    :type api_url: str
    :param key: Canvas API Key, defaults to API_KEY
    :type key: str
    :param outputs: output folder to parse result from, defaults to "processing"
    :type outputs: str, optional
    :return: A list of students whose grades are missing
    :rtype: List
    """
    canvas = Canvas(api_url, key)

    course = canvas.get_course(course_id)

    assignment = course.get_assignment(assignment_id)   
    
    # get rubric, it is manually set for now
    # TODO: parse the autograder's correctness json file and create a rubric based on that
    rubric = {}
    for i in assignment.rubric:
        # print(i["id"], i["description"], i["points"])
        rubric[i["description"]] = {"id" :i["id"]}
        rubric[i["description"]]["points"] = i["points"]
            
    # get greades
    results = os.listdir(outputs)
    missing_grades = []
    for student in results:
        # get the correctness json file, the file name NUST BE correct_crit.json and it must be in the student's folder: processing/<student>/correct_crit.json
        corr_json = f'{outputs}/{student}/correct_crit.json'
        
        # check if file exists
        if os.path.exists(corr_json):
            correctness = json.load(open(corr_json, 'r'))
            rubric_assignment = {}

            for problem in rubric:
                part = problem
                if part not in correctness:  # skip if the part number is not in the correctness json
                    continue
                logic_total = correctness[part]["logic_weight"]  * float(correctness[part]["logic_function"])
                measurment_total = correctness[part]["num_correct_meas"] * correctness[part]["meas_weights"]
                
                rubric_assignment[rubric[problem]["id"]] = {
                    "points": logic_total + measurment_total
                }
            submission = assignment.get_submission(student, include=["rubric_assessment", "user"])
            submission.edit(rubric_assessment=rubric_assignment)
        else:
            missing_grades.append(student)
    
    print(f"WARN: Missing grades for {missing_grades}")
    return missing_grades

@app.command()
def grade_one(course_id: int, assignment_id: int, sid: int, api_url=API_URL, key=API_KEY, corr_json: str="correct_crit.json"):
    """Similar to set_grades, but grades only one student

    :param course_id: Canvas API course id
    :type course_id: int
    :param assignment_id: Canvas API assignment id
    :type assignment_id: int
    :param sid: Canvas student id (Not the netid)
    :type sid: int
    :param api_url: Canvas API URL, defaults to API_URL
    :type api_url: str
    :param key: Canvas API Key, defaults to API_KEY
    :type key: str
    :param corr_json: corr_json, defaults to "correct_crit.json"
    :type corr_json: str, optional
    """
    canvas = Canvas(api_url, key)

    course = canvas.get_course(course_id)

    assignment = course.get_assignment(assignment_id)  
    
    rubric = {}
    for i in assignment.rubric:
        # print(i["id"], i["description"], i["points"])
        rubric[i["description"]] = {"id" :i["id"]}
        rubric[i["description"]]["points"] = i["points"]

    if os.path.exists(corr_json):
            correctness = json.load(open(corr_json, 'r'))
            rubric_assignment = {}

            for problem in rubric:
                part = problem
                if part not in correctness:  # skip if the part number is not in the correctness json
                    continue
                logic_total = correctness[part]["logic_weight"]  * float(correctness[part]["logic_function"])
                measurment_total = correctness[part]["num_correct_meas"] * correctness[part]["meas_weights"]
                
                rubric_assignment[rubric[problem]["id"]] = {
                    "points": logic_total + measurment_total
                }
            submission = assignment.get_submission(sid, include=["rubric_assessment", "user"])
            submission.edit(rubric_assessment=rubric_assignment)
    else:
        print(f"ERROR: {corr_json} not found!")

