import sys
import requests
from requests.auth import HTTPBasicAuth
import json
import os

# Clear error.txt if it exists from a previous run
if os.path.exists("error.txt"):
    os.remove("error.txt")

if len(sys.argv) != 4:
    print("Usage: python3 MigrateSpecificExecutionStatus.py <username> <password> <project_key>")
    sys.exit(1)

with open('app.properties', 'r') as file:
    for line in file:
        if line.startswith('host'):
            instance_url = line.split('=', 1)[1].strip()
            break

username = sys.argv[1]
password = sys.argv[2]
project_key = sys.argv[3]
base_url = instance_url
mc_auth = HTTPBasicAuth(username, password)

query_url = f"{base_url}/rest/api/2/search?jql=project = {project_key} AND issuetype = Test &maxResults=1"
default_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

issues_response = requests.get(query_url, headers=default_headers, auth=mc_auth)

if issues_response.status_code == 200:
    response_data = issues_response.json()

    # Check if there are issues in the response
    if "issues" in response_data and response_data["issues"]:
        first_issue = response_data["issues"][0]

        issue_id = first_issue["id"]
        project_id = first_issue["fields"]["project"]["id"]

        print(f"ID={project_id}")
        print(f"baseURL={base_url}")

    else:
        print("No issues found in the response.")
        sys.exit(1)
else:
    with open("error.txt", "w") as error_file:
        error_file.write(f"Error: {issues_response.status_code} - {issues_response.text}")
    print(f"Error: {issues_response.status_code} - {issues_response.text}\nError details saved to error.txt")
    sys.exit(1)

PostStatusURL = f"{base_url}/rest/tests/1.0/testresultstatus"


status_list = [
    {
        "name": "Descoped",
        "description": "Description for Descoped",
        "color": "#9900ff"
    },
    {
        "name": "Not Delivered Yet",
        "description": "Description for Retested",
        "color": "#ff9966"
    },
    {
        "name": "WIP",
        "description": "Description for WIP",
        "color": "#ff9965"
    }
]

# Set the environment variables before the loop
os.environ['MIGRATION_ID'] = str(project_id)
os.environ['MIGRATION_BASE_URL'] = base_url

# Iterate through the status_list and send request to create new status.
for index, status_details in enumerate(status_list):
    payload = {
        "projectId": int(project_id),
        "name": status_details["name"],
        "description": status_details["description"],
        "color": status_details["color"],
        "index": index,
        "items": []
    }
    
    response = requests.post(PostStatusURL, json=payload, headers=default_headers, auth=mc_auth)

    if response.status_code == 200:
        print(f"Status {index} posted successfully.")
    else:
        with open("error.txt", "a") as error_file:
            error_file.write(f"Error posting status {index}: {response.status_code} - {response.text}\n")
        print(f"Error posting status {index}. Error details saved to error.txt")
        sys.exit(1)
