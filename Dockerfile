FROM python:3.9.12

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend directory
COPY backend ./backend

# Copy nltk.txt and download NLTK data
COPY nltk.txt .
RUN python -m nltk.downloader -d /usr/local/share/nltk_data $(cat nltk.txt)

# Set the working directory to the backend folder
WORKDIR /app/backend

# Command to run the application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
