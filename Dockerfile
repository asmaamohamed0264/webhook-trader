# Use the official Python 3.12 image as the base image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy the project files into the Docker image
COPY . /app

# Install the required dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the FastAPI server using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
