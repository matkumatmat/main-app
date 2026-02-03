import time
import requests
import sys

# Configuration
URL = "http://localhost:8080/api/auth/health"
LIMIT = 5 

print(f"Testing Redirect Logic: {URL}")
print(f"Expectation: {LIMIT}x 200 OK, then 302 Redirect to Telkomsel\n")

for i in range(1, 10):
    try:
        # allow_redirects=False penting buat ngecek header Location
        response = requests.get(URL, allow_redirects=False)
        status = response.status_code
        
        status_str = ""
        if status == 200:
            status_str = f"{status} (OK - Masuk Server)"
        elif status == 302 or status == 301:
            location = response.headers.get('Location', 'Unknown')
            status_str = f"{status} (DIBUANG ke -> {location})"
        elif status == 429:
            status_str = f"{status} (Masih JSON Error, belum Redirect)"
        else:
            status_str = f"{status}"
            
        print(f"Req #{i}: {status_str}")
        
    except requests.exceptions.ConnectionError:
        print(f"Req #{i}: Connection Refused")
        sys.exit(1)
        
    time.sleep(0.5)

print("\nFinished.")