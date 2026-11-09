
# Use a lightweight Python 3.9 base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy frontend application files
COPY . .

# Install required Python libraries
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the Streamlit application port
EXPOSE 8501

# Start the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
