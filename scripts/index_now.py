import os
import json
import urllib.request
from google.oauth2 import service_account
import google.auth.transport.requests

SCOPES = ['https://www.googleapis.com/auth/indexing']
ENDPOINT = 'https://indexing.googleapis.com/v3/urlNotifications:publish'

def get_credentials():
    # 0. Check CLI arg
    import sys
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        return service_account.Credentials.from_service_account_file(sys.argv[1], scopes=SCOPES)

    # 1. First check environment variable (for GitHub Actions Secret)
    secret_env = os.getenv('GOOGLE_INDEXING_KEY')
    if secret_env:
        try:
            key_dict = json.loads(secret_env)
            return service_account.Credentials.from_service_account_info(key_dict, scopes=SCOPES)
        except Exception as e:
            print(f"Failed to parse GOOGLE_INDEXING_KEY env var: {e}")

    # 2. Check local Downloads folder fallback
    local_paths = [
        r'C:\Users\Admin\Downloads\yt4mp3-509012-44fccbc450ca.json',
        r'/tmp/google_key.json',
        r'google_indexing_key.json'
    ]
    for p in local_paths:
        if os.path.exists(p):
            return service_account.Credentials.from_service_account_file(p, scopes=SCOPES)

    raise FileNotFoundError("Google Indexing Service Account Key not found in env or local path.")

def ping_google_indexing():
    credentials = get_credentials()
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    token = credentials.token
    print("Google OAuth2 token verified successfully.")

    urls = [
        'https://www.yt4mp3.cc/',
        'https://www.yt4mp3.cc/youtube-to-mp3',
        'https://www.yt4mp3.cc/youtube-to-mp4',
        'https://www.yt4mp3.cc/contact-us',
        'https://www.yt4mp3.cc/terms-of-service',
        'https://www.yt4mp3.cc/privacy-policy'
    ]

    print(f"Sending Google Indexing API ping for {len(urls)} URLs...")
    for url in urls:
        data = json.dumps({'url': url, 'type': 'URL_UPDATED'}).encode('utf-8')
        req = urllib.request.Request(
            ENDPOINT,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            method='POST'
        )
        try:
            with urllib.request.urlopen(req) as response:
                print(f"[SUCCESS 200] Pinged Google Indexing: {url}")
        except urllib.error.HTTPError as e:
            err = e.read().decode('utf-8')
            print(f"[ERROR {e.code}] {url} -> {err}")

if __name__ == '__main__':
    ping_google_indexing()
