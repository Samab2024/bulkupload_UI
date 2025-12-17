# Use official Python 3.12 slim image
FROM python:3.12-slim

WORKDIR /app

# Copy app code
COPY . .

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 2000

# Run the app
CMD ["python", "app.py"]