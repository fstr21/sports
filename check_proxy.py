import socket
import requests
import time

def check_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8080))
    sock.close()
    return result == 0

def test_http():
    try:
        response = requests.get('http://127.0.0.1:8080/', timeout=5)
        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return True
    except Exception as e:
        print(f"HTTP Error: {e}")
        return False

def test_sse_endpoint():
    try:
        response = requests.get('http://127.0.0.1:8080/servers/espn/sse', timeout=5)
        print(f"SSE Status: {response.status_code}")
        print(f"SSE Response: {response.text[:200]}")
        return True
    except Exception as e:
        print(f"SSE Error: {e}")
        return False

print("=== Checking MCP Proxy Status ===")
print(f"Port 8080 open: {check_port()}")
if check_port():
    print("Testing HTTP root...")
    test_http()
    print("Testing SSE endpoint...")
    test_sse_endpoint()
else:
    print("Port 8080 is not accessible. Is the proxy running?")