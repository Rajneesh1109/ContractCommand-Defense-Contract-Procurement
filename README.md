# ContractCommand — Defense Contract & Procurement Management System
## HCL Technologies Enterprise Defense Domain Project

---

### Project Overview

**ContractCommand** is a full-stack defense procurement lifecycle management system built with **Python / Django / MySQL**, covering the complete acquisition chain from operational requisitioning to treasury disbursement.

| Attribute | Detail |
|---|---|
| **Domain** | Aerospace & Defense |
| **Tech Stack** | Python 3.11, Django 5.2, SQLite/MySQL 8.0, Bootstrap 5 |
| **CI/CD** | GitLab CI/CD + Jenkins Pipeline |
| **Security** | ITAR / DAP 2020 / DD-250 compliance |

---

### System Architecture

```
ContractCommand/
├── contractcommand/       # Django project config (settings, urls, wsgi)
├── core/                  # Users, custom roles, security clearances, audit trail
├── vendors/               # Defense contractor registry, evaluations, CAGE/DUNS
├── procurement/           # Requisitions, Tenders/RFPs, bids, item catalog
├── contracts/             # Contract lifecycle, milestones, amendments, logs
├── invoicing/             # DD-250 inspections, invoices, 3-way match, disbursements
├── templates/             # Bootstrap 5 military-themed HTML templates
├── static/css/            # Custom defense.css styling
├── requirements.txt       # Python dependencies
├── .gitlab-ci.yml         # GitLab CI/CD pipeline
├── Jenkinsfile            # Jenkins pipeline definition
└── populate_data.py       # Sample realistic defense data seeder
```

---

### Quick Start

```powershell
# 1. Install dependencies
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. Run database migrations
python manage.py migrate

# 3. Load sample defense data
python populate_data.py

# 4. Start development server
python manage.py runserver
```

Access the portal at **http://127.0.0.1:8000/**

---

### Demo Login Accounts (Password: `Admin@1234`)

| Username | Role | Security Clearance |
|---|---|---|
| `admin` | System Administrator | TOP SECRET (TS/SCI) |
| `rajesh_sharma` | Defense Procurement Officer | SECRET |
| `vikram_malhotra` | Contracting & Approving Officer | TOP SECRET |
| `sunita_rao` | Quality & Defense Inspector (DGQA) | SECRET |
| `ajay_mehra` | Finance & Disbursement Officer (PCDA) | SECRET |
| `amitabh_sen` | Defense Compliance Auditor | TOP SECRET |

---

### Core Modules

#### 1. Contract Repository & Lifecycle Management
- Defense contract drafting (DAP 2020, ITAR, Strategic Partnership)
- Security classifications: Unclassified → Top Secret (TS/SCI)
- Lifecycle state machine: Draft → Legal Review → Active → Amended → Completed
- Contract amendments (cost revision, timeline extension, spec upgrade)
- Cryptographically-sealed lifecycle audit trail

#### 2. Procurement Planning
- Defense procurement requisitions with operational priority matrix
- Equipment catalog with NATO Stock Numbers (NSN) and Mil-Spec codes
- Tender / RFP management: Open competitive, Limited, Single-source
- Multi-vendor bid evaluation, L1 commercial selection & award workflow

#### 3. Vendor Evaluation
- Defense contractor registry with CAGE / NCAGE / DUNS codes
- Facility security clearance tracking with expiry dates
- ITAR / EAR export control compliance flags
- Multi-criteria weighted performance evaluation (Technical 25% + Quality 25% + Delivery 20% + Compliance 15% + Cost 15%)
- Tier classification: Prime → Sub-system Integrator → Component Supplier

#### 4. Invoice & Payment Processing
- Milestone-based payment claims with DD-250 inspection linkage
- Three-way match verification: Contract + DD-250 + Invoice
- 5% warranty retention calculation (DAP 2020 standard)
- Defense treasury disbursement via PCDA RTGS / SBI Gov / Escrow / LC
- Printable DD-250 military inspection forms with SHA-256 digital seal
- CSV export for external audit & PCDA ledger reconciliation

---

### MySQL Configuration

Edit `.env` and set `USE_MYSQL=True` to switch from SQLite to MySQL:

```env
USE_MYSQL=True
DB_NAME=contract_command_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

---

### CI/CD Pipeline

**GitLab**: `.gitlab-ci.yml` — 3 stages: `test → build → deploy`  
**Jenkins**: `Jenkinsfile` — 6 stages with manual production gate & CAB approval

---

### Admin Interface

Access Django Admin at: **http://127.0.0.1:8000/admin/**  
Login with `admin` / `Admin@1234`
