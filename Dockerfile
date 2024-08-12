FROM python:3.9.12

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the backend directory
COPY backend ./backend

# Copy nltk.txt and download NLTK data
COPY nltk.txt .
RUN python -c "import nltk; nltk.download([line.strip() for line in open('nltk.txt')], quiet=True)"

# Set the working directory to the backend folder
WORKDIR /app/backend

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
