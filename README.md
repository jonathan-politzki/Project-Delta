# Project Delta: Writer Analysis Tool

Project Delta is an advanced web application designed to analyze writing styles and provide insights into authors' works. It uses natural language processing and machine learning techniques to extract meaningful information from Medium and Substack articles.

## Features

- Analyze writing styles from Medium and Substack URLs
- Extract key themes, sentiment, and readability scores
- Generate insights using advanced language models
- Compare different authors' writing styles

## Project Structure

```
project-delta/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── styles/
│   ├── public/
│   └── package.json
├── .gitignore
└── README.md
```

## Technologies Used

- Backend: FastAPI, Python
- Frontend: Next.js, React, Tailwind CSS
- Database: PostgreSQL (planned)
- Vector Database: Milvus (current), Pinecone (planned)
- Deployment: Vercel (frontend), Heroku (backend) - planned

## Setup Instructions

### Backend

1. Navigate to the backend directory:
   ```
   cd backend
   ```
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables (create a `.env` file based on `.env.example`)
5. Run the backend server:
   ```
   uvicorn main:app --reload
   ```

### Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```
3. Run the development server:
   ```
   npm run dev
   ```

## Usage

1. Start both the backend and frontend servers.
2. Open your browser and navigate to `http://localhost:3000`.
3. Enter a Medium or Substack URL in the input field.
4. Click "Analyze" to see the results.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.