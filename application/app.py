from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

app = Flask(__name__)

# MySQL connection setup
DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT", 3306))
GROUP_NAME = os.environ.get("GROUP_NAME") or "Group 1"

# Initialize the database connection here so it's available in all routes
def init_db_connection():
    return connections.Connection(
        host=DBHOST,
        port=DBPORT,
        user=DBUSER,
        password=DBPWD,
        db=DATABASE
    )

# Initialize the database connection globally
db_conn = init_db_connection()

# S3 Details
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("S3_KEY")

# Define the path where you'll save the downloaded image
DOWNLOADS_PATH = "static/downloads"
if not os.path.exists(DOWNLOADS_PATH):
    os.makedirs(DOWNLOADS_PATH)

IMAGE_PATH = os.path.join(DOWNLOADS_PATH, "sample1.jpg")

# Download image from S3 bucket using boto3
try:
    s3_client = boto3.client('s3')  # boto3 will use ~/.aws/credentials
    if not os.path.exists(IMAGE_PATH):  # Avoid re-downloading if already present
        print(f"Downloading image from S3 bucket: {S3_BUCKET}, key: {S3_KEY}")
        s3_client.download_file(S3_BUCKET, S3_KEY, IMAGE_PATH)
        print("Image downloaded successfully.")
    else:
        print(f"Image already exists at {IMAGE_PATH}")
except NoCredentialsError:
    print("AWS credentials not found. Ensure your ~/.aws/credentials file is properly configured.")
except ClientError as e:
    print(f"Failed to download image from S3: {e}")
except Exception as e:
    print(f"Error processing image download: {e}")

# Background image path for rendering in HTML
BACKGROUND_IMAGE_PATH = "/static/downloads/sample1.jpg"
print(f"Background Image Path: {BACKGROUND_IMAGE_PATH}")

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', background_image=BACKGROUND_IMAGE_PATH, GROUP_NAME=GROUP_NAME)

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', background_image=BACKGROUND_IMAGE_PATH, GROUP_NAME=GROUP_NAME)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    print("All modifications done...")
    return render_template('addempoutput.html', name=emp_name, background_image=BACKGROUND_IMAGE_PATH, GROUP_NAME=GROUP_NAME)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", background_image=BACKGROUND_IMAGE_PATH, GROUP_NAME=GROUP_NAME)

@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']
    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]

    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"],
                           background_image=BACKGROUND_IMAGE_PATH, GROUP_NAME=GROUP_NAME)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
