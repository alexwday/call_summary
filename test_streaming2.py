"""Test script to debug newline issues"""

import requests

# Create a session to handle cookies
session = requests.Session()

# First get the main page to establish session
session.get("http://127.0.0.1:5001/")

# Send a test message
url = "http://127.0.0.1:5001/chat"
headers = {"Content-Type": "application/json"}
data = {
    "message": "Reply with exactly: Line1\\nLine2\\nLine3"
}

response = session.post(url, headers=headers, json=data, stream=True)

print("=" * 50)
print("RAW STREAMING CHUNKS WITH SPECIAL CHARS:")
print("=" * 50)

full_content = ""
chunk_count = 0

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            chunk = line_str[6:]
            chunk_count += 1
            full_content += chunk
            # Show representation to see special characters
            print(f"Chunk {chunk_count}: {repr(chunk)}")

print("=" * 50)
print("FULL CONTENT (repr):")
print("=" * 50)
print(repr(full_content))

print()
print("=" * 50)
print("FULL CONTENT (normal):")
print("=" * 50)
print(full_content)