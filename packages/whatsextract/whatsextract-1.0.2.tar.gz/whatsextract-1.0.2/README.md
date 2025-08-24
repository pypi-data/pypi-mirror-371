# whatsextract (Python SDK)

Lightweight client for the WhatsExtract API.

## Install
```bash
pip install whatsextract
Usage
python
Copy
Edit
from whatsextract import WhatsExtract

client = WhatsExtract(api_key="YOUR_API_KEY", base_url="https://api.whatsextract.com")
result = client.batch(["Priya here. Email priya@gmail.com, phone 9876543210"])
print(result)
Links
Home: https://whatsextract.com

API Docs: https://docs.whatsextract.com
