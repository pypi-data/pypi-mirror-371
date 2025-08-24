.. COMPLETE FILE: packages/python/README.rst

WhatsExtract (Python)
=====================

Install::

  pip install whatsextract

Quick start::

  from whatsextract import WhatsExtract
  client = WhatsExtract("we_xxx")
  print(client.extract("Email john@example.com").email)
