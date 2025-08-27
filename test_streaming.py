"""Test script to debug streaming issues"""

import requests

# Create a session to handle cookies
session = requests.Session()

# First get the main page to establish session
session.get("http://127.0.0.1:5001/")

# Send a test message
url = "http://127.0.0.1:5001/chat"
headers = {"Content-Type": "application/json"}
data = {
    "message": "Please create a test response with: 1. A header using ###, 2. A bullet list with three items, 3. Some **bold** text, 4. A horizontal rule using ---, 5. A code block"
}

response = session.post(url, headers=headers, json=data, stream=True)

print("=" * 50)
print("RAW STREAMING CHUNKS:")
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
            print(f"Chunk {chunk_count}: [{chunk}]")
            print(f"  Length: {len(chunk)} chars")
            if len(chunk) < 50:  # Only show repr for short chunks
                print(f"  Repr: {repr(chunk)}")
            print()

print("=" * 50)
print("FULL RECONSTRUCTED CONTENT:")
print("=" * 50)
print(full_content)
print()
print(f"Total chunks: {chunk_count}")
print(f"Total length: {len(full_content)} chars")

# Check for missing spaces
import re
# Look for lowercase letter followed directly by uppercase (potential missing space)
missing_spaces = re.findall(r'[a-z][A-Z]', full_content)
if missing_spaces:
    print(f"\nPotential missing spaces found: {missing_spaces}")
    
# Check for markdown elements
print("\nMarkdown elements found:")
if '###' in full_content:
    print("✓ Headers (###)")
else:
    print("✗ No headers (###)")
    
if '- ' in full_content or '* ' in full_content:
    print("✓ Bullet lists")
else:
    print("✗ No bullet lists")
    
if '**' in full_content:
    print("✓ Bold text")
else:
    print("✗ No bold text")
    
if '---' in full_content:
    print("✓ Horizontal rule")
else:
    print("✗ No horizontal rule")
    
if '```' in full_content:
    print("✓ Code blocks")
else:
    print("✗ No code blocks")