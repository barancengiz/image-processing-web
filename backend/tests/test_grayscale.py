import requests

# API endpoint
url = "http://127.0.0.1:8000/process/"

# File and operation
files = {'file': open('/app/tests/assets/image_high_res.png', 'rb')}
data = {'operation': 'grayscale'}

# Send POST request
response = requests.post(url, files=files, data=data)
response.raise_for_status()  # raises exception when not a 2xx response

# Print the response
print(response.json())