"""Test fixed streaming"""

import requests

session = requests.Session()
session.get("http://127.0.0.1:5001/")

url = "http://127.0.0.1:5001/chat"
headers = {"Content-Type": "application/json"}
data = {
    "message": "Please create a test response with: 1. A header using ###, 2. A bullet list with three items, 3. Some **bold** text, 4. A horizontal rule using ---, 5. A code block"
}

response = session.post(url, headers=headers, json=data, stream=True)

full_content = ""
for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            chunk = line_str[6:]
            # Unescape newlines
            chunk = chunk.replace('\\n', '\n').replace('\\r', '\r')
            full_content += chunk

print("RECONSTRUCTED CONTENT:")
print("=" * 50)
print(full_content)
print("=" * 50)

# Check structure
lines = full_content.split('\n')
print(f"\nTotal lines: {len(lines)}")
for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
    print(f"Line {i}: [{line}]")