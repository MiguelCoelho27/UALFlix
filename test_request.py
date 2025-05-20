import requests

try:
    r = requests.get("http://host.docker.internal:5001/videos")
    print("Status:", r.status_code)
    print("Texto:", r.text)
    print("JSON:", r.json())
except Exception as e:
    print("Erro:", e)