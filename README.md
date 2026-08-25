# Patient Document Management System

A full-stack web application for securely managing patient documents and extracting structured medical data from uploaded documents using Google Gemini.

The system provides separate workflows for **Patients** and **Administrators**. Patients can upload and manage their medical documents, while administrators can view patients and access their uploaded documents.

Uploaded medical documents are processed by Google Gemini to extract structured medical information such as laboratory test names, values, units, reference ranges, and abnormality indicators.

---

## Features

### Patient

- Upload one or multiple medical documents
- View uploaded document metadata
- View document status
- View AI-extracted medical data
- Display extracted medical information in a structured table
- View field values, units, reference ranges, and abnormality status

### Administrator

- View registered patients
- View documents uploaded by a specific patient
- View document metadata
- Access extracted medical information from patient documents

### AI-Powered Extraction

- Google Gemini integration
- Direct document processing
- Structured JSON responses
- Pydantic schema validation
- Canonical medical field mapping
- Duplicate-field detection
- Empty field filtering
- Abnormality detection when explicitly indicated by the document

---

## Technology Stack

### Frontend

- React
- TypeScript
- Vite
- React Router
- Axios
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Google Gemini API
- python-dotenv

### Database

- SQLAlchemy ORM
- Relational database

### AI

- Google Gemini
- Structured medical data extraction

---

## System Architecture

```
                         ┌─────────────────────┐
                         │      Frontend       │
                         │ React + TypeScript  │
                         └──────────┬──────────┘
                                    │
                                    │ HTTP / REST API
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │      Backend        │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
             ┌───────────────┐             ┌───────────────┐
             │   Database    │             │ Google Gemini │
             │               │             │      API      │
             │ Users         │             │               │
             │ Documents     │             │ Extraction    │
             │ Extracted     │             │ Structured    │
             │ Medical Data  │             │ Data          │
             └───────────────┘             └───────────────┘
```
  
## Project Structure

patient-document-management/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database.py
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── admin/
│   │   │   └── documents/
│   │   ├── pages/
│   │   │   ├── admin/
│   │   │   └── patient/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── .env.example
│
├── .gitignore
└── README.md
