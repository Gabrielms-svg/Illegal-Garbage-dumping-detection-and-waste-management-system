Illegal Garbage Dump Detection & Waste Management System (Dump Surveillance AI)
-------------------------------------------------------------------------------


Abstract
---------
Dump Surveillance AI is an AI-powered web application designed to detect, analyze, and manage illegal garbage dumping activities. 
The system leverages CCTV surveillance feeds and advanced computer vision techniques to automatically identify illegal dumping incidents and support effective waste management.
The application employs YOLO-based object detection to recognize dumping activities and extract vehicle number plates involved in the offense. Detected incidents are processed using clustering and analytical models to generate actionable insights. These insights are visualized on interactive maps using the Leaflet API, enabling authorities to identify and monitor illegal dumping hotspots efficiently.
In addition to surveillance-based detection, the platform allows citizens to report illegal dumping by uploading media along with time, location, and incident details. Users can also locate authorized legal dumping sites nearby, promoting responsible waste disposal. To enhance public awareness, the system includes an AI-powered chatbot that provides guidance on proper waste management practices.
Illegal waste dumping remains a significant environmental and public health challenge in India, primarily due to limited access to legal disposal facilities and inadequate offender accountability. Unregulated dumping leads to pollution, health hazards, and ecosystem degradation. Traditional manual monitoring methods are inefficient and resource-intensive. This project aims to automate surveillance and reporting, enabling government authorities to improve enforcement, ensure accountability, and promote cleaner and safer environments.


⚠️ Note: This project uses CUDA 11.8-enabled PyTorch for GPU-accelerated inference

requirements :
--------------

Programming Language
-------------------------------
Python: 3.11.2

Web Framework & Backend
-------------------------------
Django: 3.2.7

Pytest : 9.0.2

Pluggy : 1.6.0

asgiref: 3.9.1

sqlparse: 0.5.3

pytz / tzdata: 2025.2

Database
-------------------------------
MySQL

mysqlclient: 2.2.7

Computer Vision & AI
-------------------------------
YOLO (Ultralytics): 8.3.237

OpenCV: 4.12.0.88

EasyOCR: 1.7.2

PyTorch: 2.7.1+cu118

TorchVision: 0.22.1+cu118

TorchAudio: 2.7.1+cu118

Machine Learning & Analytics
-------------------------------
NumPy: 2.2.6

Pandas: 2.3.3

Scikit-learn: 1.7.2

SciPy: 1.16.3

Joblib: 1.5.2

Visualization & Mapping
-------------------------------
Matplotlib: 3.10.8

Shapely: 2.1.2

Image & Signal Processing
------------------------------
Pillow: 11.3.0

Scikit-image: 0.26.0

ImageIO: 2.37.2

Tifffile: 2025.12.20

Utilities & Supporting Libraries
---------------------------------
Requests: 2.32.5

PyYAML: 6.0.3

Psutil: 7.1.3

NetworkX: 3.6.1

SymPy: 1.14.0


Deployment & Environment variables
----------------------------------
Use environment variables to configure runtime settings and keep secrets out of source control. Below are the environment variables supported by the project's settings package and example commands to run locally.

Required (production):
- `DJANGO_SECRET_KEY`: strong secret key (must be set in production).
- `DJANGO_ALLOWED_HOSTS`: comma-separated hosts (e.g. `example.com,www.example.com`).

Common optional vars:
- `DJANGO_ENV`: `production` or `development` (controls default settings selection).
- `DJANGO_SETTINGS_MODULE`: explicit settings module (e.g. `garbmgmt.settings.production`). If set, it overrides `DJANGO_ENV`.
- `DJANGO_DEBUG`: `True` or `False` (development override).
- `DJANGO_TIME_ZONE`: timezone (default from base settings).

Database (override defaults):
- `DJANGO_DB_ENGINE` (e.g. `django.db.backends.mysql`)
- `DJANGO_DB_NAME`
- `DJANGO_DB_USER`
- `DJANGO_DB_PASSWORD`
- `DJANGO_DB_HOST`
- `DJANGO_DB_PORT`

Security / production flags (optional):
- `DJANGO_SECURE_SSL_REDIRECT` (True/False)
- `DJANGO_HSTS_SECONDS`

Example (PowerShell - development):
```
$env:DJANGO_SETTINGS_MODULE = 'garbmgmt.settings.development'
$env:DJANGO_SECRET_KEY = 'dev-secret-change-me'
python manage.py runserver 0.0.0.0:8000
```

Example (bash - development):
```
export DJANGO_SETTINGS_MODULE=garbmgmt.settings.development
export DJANGO_SECRET_KEY='dev-secret-change-me'
python manage.py runserver 0.0.0.0:8000
```

Example (production container): set env vars in your container/orchestration platform and ensure `DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS` are present. To use the production settings via `DJANGO_ENV`:
```
export DJANGO_ENV=production
export DJANGO_SECRET_KEY='your-strong-secret'
export DJANGO_ALLOWED_HOSTS='example.com,www.example.com'
gunicorn garbmgmt.wsgi:application
```

Notes:
- Do NOT commit `DJANGO_SECRET_KEY` or DB credentials into source control.
- Consider using a secrets manager (AWS Secrets Manager, Azure Key Vault) or a `.env` file managed outside of Git for local convenience.
- After changing static configuration, run `python manage.py collectstatic` in production.

