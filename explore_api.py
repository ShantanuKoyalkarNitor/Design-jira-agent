#!/usr/bin/env python3
"""Explore available Jira API endpoints"""

import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('JIRA_URL').rstrip('/')
username = os.getenv('JIRA_USERNAME')
api_token = os.getenv('JIRA_API_TOKEN')

print("\n" + "=" * 70)
print("EXPLORING JIRA API ENDPOINTS")
print("=" * 70)

endpoints_to_try = [
    # v3 endpoints
    ('/rest/api/3/myself', 'Check current user'),
    ('/rest/api/3/projects', 'List projects (v3)'),
    ('/rest/api/3/search', 'Search issues (v3 - old)'),
    
    # v2 endpoints
    ('/rest/api/2/issue/SK101-10', 'Get issue (v2)'),
    ('/rest/api/2/search', 'Search (v2)'),
    ('/rest/api/2/project', 'List projects (v2)'),
    
    # Cloud endpoints
    ('/rest/cloud/v1/issue/SK101-10', 'Get issue (cloud)'),
]

for endpoint, desc in endpoints_to_try:
    full_url = f'{url}{endpoint}'
    response = requests.get(
        full_url,
        auth=HTTPBasicAuth(username, api_token),
        timeout=5
    )
    
    status = '✅' if response.status_code < 400 else '❌'
    print(f"\n{status} {endpoint}")
    print(f"   Description: {desc}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code < 400:
        print(f"   Response: OK (working!)")
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    keys = list(data.keys())[:5]
                    print(f"   Data keys: {keys}")
                elif isinstance(data, list):
                    print(f"   Data: List with {len(data)} items")
            except:
                print(f"   (Response body not JSON)")
    else:
        try:
            error = response.json()
            if 'errorMessages' in error:
                print(f"   Error: {error['errorMessages']}")
            elif 'detail' in error:
                print(f"   Error: {error['detail'][:60]}")
        except:
            print(f"   Error: {response.text[:60]}")
