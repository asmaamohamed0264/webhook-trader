# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fire",
#     "python-dotenv",
#     "requests",
#     "rich",
# ]
# ///
import os
import json

from dotenv import load_dotenv
import requests
import fire
from rich import print_json

load_dotenv()

BASE_URL = os.getenv("BASE_URL", 'http://localhost:8000')


def get_account(name: str):
    '''Get an account by name.'''
    resp = requests.get(f"{BASE_URL}/account/{name}")
    data = resp.text
    print_json(data)


def get_snapshots():
    '''Get the last 12 snapshots for each account.'''
    resp = requests.get(f"{BASE_URL}/snapshots")
    data = resp.text
    print_json(data)


def get_snapshot(name: str):
    '''Get a snapshot for an account by name.'''
    resp = requests.get(f"{BASE_URL}/snapshot/{name}")
    data = resp.text
    print_json(data)

def webhook(body_file: str):
    '''Send a webhook to the server.'''
    with open(body_file, 'r') as f:
        body = json.load(f)
    resp = requests.post(f"{BASE_URL}/webhook/{body['nickname']}", json=body)
    data = resp.text
    print_json(data)

if __name__ == "__main__":
    fire.Fire()
