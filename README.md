# AssetDesk 

A modern Asset Management System built with Django for managing organizational assets, support tickets, maintenance operations, and reporting through a centralized platform.

## Overview

AssetDesk is designed to help organizations efficiently manage their IT and operational assets throughout their lifecycle. The system provides role-based access control, asset tracking, maintenance management, support ticket handling, and reporting capabilities.

The platform includes dedicated dashboards for employees and staff members, allowing each user to access the information and tools relevant to their responsibilities.

---

## Features

### Asset Management

* Register and manage organizational assets
* Track asset lifecycle and status
* Assign assets to employees
* Monitor asset availability
* Retire outdated assets

### Ticket Management

* Create support tickets
* Track ticket status
* Manage ticket priorities
* Assign tickets to IT staff
* Monitor ticket resolution progress

### Maintenance Management

* Schedule maintenance activities
* Track maintenance progress
* Record maintenance history
* Monitor pending and completed maintenance tasks

### Reports & Analytics

* Interactive dashboards
* Asset statistics and summaries
* Ticket analytics
* Maintenance reporting
* PDF report generation

### User Management

* Custom user model
* Employee profiles
* Department management
* Role-based permissions



---

## User Roles

### Admin

* Full system access
* Manage users and departments
* Manage all assets, tickets, and maintenance records
* Access reports and analytics

### Manager

* Monitor organizational resources
* View reports and statistics
* Manage operational activities

### IT Expert

* Handle support tickets
* Manage maintenance operations
* Monitor assigned assets

### Employee

* View assigned assets
* Create support tickets
* Track personal requests

---

## Screenshots

### Landing Page

<img width="1911" height="1010" alt="image" src="https://github.com/user-attachments/assets/460e3c60-39ad-4c9b-9456-7ca0db87fd28" />
<img width="1913" height="925" alt="image" src="https://github.com/user-attachments/assets/1a31068d-2779-4eac-9b8d-ab8745ec1b01" />


### Dashboard
<img width="1919" height="705" alt="image" src="https://github.com/user-attachments/assets/0dd59bf8-08e0-419d-ba14-fc891b450001" />
<img width="1919" height="545" alt="image" src="https://github.com/user-attachments/assets/623bca72-5a3d-434d-92d2-3fd4052517c8" />
<img width="1920" height="581" alt="image" src="https://github.com/user-attachments/assets/db113d8f-539a-4102-9126-e841d001b6bd" />






### Asset Management
<img width="1913" height="587" alt="image" src="https://github.com/user-attachments/assets/41854339-6496-4cf1-b365-27eb4cee6fdd" />
<img width="1913" height="1003" alt="image" src="https://github.com/user-attachments/assets/373ea79b-fb79-4d05-86a1-87535e2ff349" />
<img width="1913" height="1003" alt="image" src="https://github.com/user-attachments/assets/56d5e04b-9547-4e80-8066-ac6a412c589f" />
<img width="1913" height="1003" alt="image" src="https://github.com/user-attachments/assets/7c325fd8-05ca-4176-9a38-f242f530ebde" />






### Ticket Management
<img width="1913" height="548" alt="image" src="https://github.com/user-attachments/assets/e7954016-f380-4255-9813-36603ce150dd" />
<img width="1909" height="941" alt="image" src="https://github.com/user-attachments/assets/0f4bdd3a-b96f-4fa8-a513-d7a9aab22b12" />



### Maintenance Management
<img width="1913" height="480" alt="image" src="https://github.com/user-attachments/assets/8fb25aa8-da42-4260-bb08-a2e4a5c0e193" />
<img width="1919" height="793" alt="image" src="https://github.com/user-attachments/assets/135148a0-409b-4da5-ba75-d7210e0621b6" />
<img width="1919" height="793" alt="image" src="https://github.com/user-attachments/assets/1427efea-48b0-4dc2-ba82-b894ec8ab5d0" />




### Reports & Analytics
<img width="1918" height="1008" alt="image" src="https://github.com/user-attachments/assets/c4a69314-f7fb-4d1d-89d1-66b4890bce25" />
<img width="1902" height="733" alt="image" src="https://github.com/user-attachments/assets/5d232865-4323-45cf-b5d6-720369beb53a" />
<img width="1918" height="670" alt="image" src="https://github.com/user-attachments/assets/889ed76c-d1c1-4677-82d2-ac287972212d" />



---

## Technology Stack

* Python 3.10+
* Django 5.2.15
* SQLite
* Bootstrap 5
* HTML5
* CSS3
* Chart.js

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Alma252/AssetDesk.git
cd AssetDesk
```

### Create Virtual Environment

```bash
python -m venv venv
```

Linux / macOS

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Apply Migrations

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Run Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000
```

---

## Authentication

User registration is managed by system administrators through the Django Admin Panel.

Users can authenticate using the provided login page and access resources based on their assigned role.

---

## Future Improvements

* Scheduled reports
* Email notifications
* Asset QR codes
* REST API integration
* Audit logging
* Advanced analytics
* PostgreSQL deployment

