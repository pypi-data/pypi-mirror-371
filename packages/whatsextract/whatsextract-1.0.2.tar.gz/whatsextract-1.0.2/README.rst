# WhatsExtract

> Node.js & Python client for the [WhatsExtract API](https://whatsextract.com) — extract leads (names, emails, phones, requirements) from WhatsApp messages using AI.

---

## 🚀 Features
- Extracts **name, email, phone, budget, company, requirements** from WhatsApp-style text  
- **95% accuracy**, <500ms response time  
- Sync + Async client support  
- Works with **Node.js** and **Python**  
- Free tier: 100 calls/month  

---

## 📦 Installation

### Node.js
```bash
npm install whatsextract
Python
bash
Copy
Edit
pip install whatsextract
⚡ Quick Start
Node.js (ESM)
js
Copy
Edit
import { WhatsExtract } from "whatsextract";

const client = new WhatsExtract(process.env.WE_API_KEY);

const result = await client.extract("Priya here. Email priya@gmail.com, phone 9876543210");
console.log(result);
Node.js (CommonJS)
js
Copy
Edit
const { WhatsExtract } = require("whatsextract");

const client = new WhatsExtract(process.env.WE_API_KEY);

client.extract("Contact Sarah at sarah@company.com or +1 555 123 4567")
  .then(console.log);
Python
python
Copy
Edit
from whatsextract import WhatsExtract

client = WhatsExtract("we_xxx")

print(client.extract("Email john@example.com").email)
📊 Example Response
json
Copy
Edit
{
  "name": "Priya",
  "email": "priya@gmail.com",
  "phone": "+919876543210",
  "budget": null,
  "company": null,
  "requirement": "Priya here. Email priya@gmail.com, phone 9876543210",
  "confidence": 0.85
}
🔑 Authentication
You’ll need an API key from WhatsExtract.
Export it as an environment variable:

bash
Copy
Edit
export WE_API_KEY=your_api_key_here
📚 Resources
Docs

API Playground

Support

MIT License © 2025 devopsballog25

php
Copy
Edit

---

### ✅ `README.rst`
```rst
WhatsExtract
============

Node.js & Python client for the `WhatsExtract API <https://whatsextract.com>`_ — extract leads (names, emails, phones, requirements) from WhatsApp messages using AI.

Features
--------

- Extracts **name, email, phone, budget, company, requirements** from WhatsApp-style text
- **95% accuracy**, <500ms response time
- Sync + Async client support
- Works with **Node.js** and **Python**
- Free tier: 100 calls/month

Installation
------------

Node.js::

   npm install whatsextract

Python::

   pip install whatsextract

Quick Start
-----------

Node.js (ESM)::

   import { WhatsExtract } from "whatsextract";

   const client = new WhatsExtract(process.env.WE_API_KEY);

   const result = await client.extract("Priya here. Email priya@gmail.com, phone 9876543210");
   console.log(result);

Node.js (CommonJS)::

   const { WhatsExtract } = require("whatsextract");

   const client = new WhatsExtract(process.env.WE_API_KEY);

   client.extract("Contact Sarah at sarah@company.com or +1 555 123 4567")
     .then(console.log);

Python::

   from whatsextract import WhatsExtract

   client = WhatsExtract("we_xxx")

   print(client.extract("Email john@example.com").email)

Example Response
----------------

.. code-block:: json

   {
     "name": "Priya",
     "email": "priya@gmail.com",
     "phone": "+919876543210",
     "budget": null,
     "company": null,
     "requirement": "Priya here. Email priya@gmail.com, phone 9876543210",
     "confidence": 0.85
   }

Authentication
--------------

You’ll need an API key from `WhatsExtract <https://whatsextract.com>`_.  
Export it as an environment variable::

   export WE_API_KEY=your_api_key_here

Resources
---------

- `Docs <https://whatsextract.com/docs>`_
- `API Playground <https://whatsextract.com/playground>`_
- `Support <https://whatsextract.com/support>`_

License
-------

MIT License © 2025 devopsballog25