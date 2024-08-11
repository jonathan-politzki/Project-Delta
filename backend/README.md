Backend File Structure (latest)

backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── analysis.py
│   │       └── routes/
│   │           └── api.py
│   ├── core/
│   │   ├── config.py (new file for configurations)
│   │   ├── error_handlers.py
│   │   └── vector_db.py
│   ├── models/
│   ├── schemas/
│   │   └── analysis.py
│   ├── services/
│   │   ├── analysis_service.py
│   │   ├── csv_analysis.py
│   │   ├── embedding_service.py
│   │   ├── llm_service.py
│   │   └── text_processor.py
│   └── utils/
│       └── scraper.py (moved from root)
├── tests/
│   ├── conftest.py (for shared pytest fixtures)
│   ├── test_analysis.py (new file)
│   └── test_scraper.py (moved from root)
├── .env
├── .env.example
├── main.py (moved from app/)
├── requirements.txt
└── README.md