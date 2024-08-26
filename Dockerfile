FROM python:3.9.12

WORKDIR /app

# Copy the entire project
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download([line.strip() for line in open('nltk.txt')], quiet=True)"

# Set the working directory to the backend folder
WORKDIR /app/backend

# Command to run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT