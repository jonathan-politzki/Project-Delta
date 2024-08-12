# Project Delta: Writer Analysis Tool

## Purpose

Project Delta is an advanced web application designed to analyze writing styles and provide insights into authors' works. Our tool uses cutting-edge natural language processing and machine learning techniques to extract meaningful information from Medium and Substack articles.

The primary goal of this tool is to help writers understand their unique voice and compare it with others in the literary world. By analyzing various aspects of writing, including style, themes, sentiment, and readability, we aim to provide valuable insights that can help writers improve their craft and stand out in a sea of content.

## Key Features

- Analyze writing styles from Medium and Substack URLs
- Extract key themes, sentiment, and readability scores
- Generate insights using advanced language models
- Compare different authors' writing styles
- Provide a user-friendly interface for easy analysis and result interpretation

## Project Structure

The project is divided into two main parts: the backend (FastAPI) and the frontend (React).

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
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── tailwind.config.js
├── .gitignore
└── README.md
```

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

## Technologies Used

- Backend: FastAPI, Python
- Frontend: React, Tailwind CSS
- Natural Language Processing: NLTK, OpenAI GPT
- Deployment: Vercel (frontend), Heroku (backend)

## Contributing

We welcome contributions to Project Delta! If you have suggestions for improvements or new features, please feel free to submit a pull request or open an issue on our GitHub repository.

## License

This project is licensed under the MIT License.

## Contact

For any questions or feedback, please reach out to us at [contact@projectdelta.com](mailto:contact@projectdelta.com).

---

"To know thyself is the beginning of wisdom." - Socrates

Project Delta aims to help writers on their journey of self-discovery and improvement. Happy writing!