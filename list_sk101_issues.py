#!/usr/bin/env python3
"""List issues in SK101 project"""

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('JIRA_URL').rstrip('/')
username = os.getenv('JIRA_USERNAME')
api_token = os.getenv('JIRA_API_TOKEN')

print("\nListing issues in SK101 project...")
print("=" * 70)

# Method 1: Get project details
project_url = f'{url}/rest/api/3/projects/SK101'
response = requests.get(
    project_url,
    auth=HTTPBasicAuth(username, api_token),
    timeout=10
)

if response.status_code == 200:
    project = response.json()
    print(f"\n✅ Project Found:")
    print(f"   Key: {project.get('key')}")
    print(f"   Name: {project.get('name')}")
    print(f"   Type: {project.get('projectTypeKey')}")
else:
    print(f"❌ Error: {response.status_code}")

# Method 2: Try to get issues using issue search with query
search_url = f'{url}/rest/api/3/issues'
params = {
    'jql': 'project = SK101 ORDER BY created DESC',
    'maxResults': 50
}

response = requests.get(
    search_url,
    auth=HTTPBasicAuth(username, api_token),
    params=params,
    timeout=10
)

print(f"\n\nSearching for issues in SK101...")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    issues = data.get('issues', [])
    print(f"Found {len(issues)} issues:")
    
    for issue in issues[:20]:
        print(f"\n  • Key: {issue.get('key')}")
        print(f"    Summary: {issue.get('fields', {}).get('summary', 'N/A')[:60]}")
        print(f"    Status: {issue.get('fields', {}).get('status', {}).get('name', 'N/A')}")
        
else:
    print(f"Response: {response.text[:500]}")
