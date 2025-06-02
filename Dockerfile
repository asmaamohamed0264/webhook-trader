# Build stage for Vite app
FROM node:22-bullseye-slim AS ui-builder

# Set the working directory
WORKDIR /ui

# Copy the project files into the Docker image
COPY ui/ .

# Install the required dependencies
RUN npm i
# build the image
RUN npm run build

# Runtime stage
FROM python:3.12-slim-bookworm

# install the required dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the project files into the Docker image
COPY . /app

# Copy the built UI files from the builder stage
COPY --from=ui-builder /ui/dist /app/public

# Install the required dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the FastAPI server using uvicorn
CMD ["fastapi", "run", "app.py", "--port", "8000"]
