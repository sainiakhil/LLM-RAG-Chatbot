# --- Stage 1: Base Image ---
# Use an official, lightweight Python runtime as the parent image.
# Using a specific version like 3.11 is better for reproducibility than using 'latest'.
# The 'slim' variant is smaller and great for production.
FROM python:3.11-slim

# --- Stage 2: Set Environment Variables ---
# Prevents Python from writing .pyc files to disc (improves performance in containers)
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# --- Stage 3: Set Working Directory ---
# Create and set the working directory inside the container.
WORKDIR /app

# --- Stage 4: Install Dependencies ---
# Copy the requirements file *first* to leverage Docker's layer caching.
# This crucial step means the 'pip install' command will only re-run if
# your requirements.txt file changes, making subsequent builds much faster.
COPY requirements.txt .

# Upgrade pip and install the packages from requirements.txt
# --no-cache-dir reduces the image size.
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 5: Copy Application Code ---
# Now copy the rest of your application's source code into the working directory.
COPY . .

# --- Stage 6: Expose the Port ---
# Inform Docker that the container listens on port 8000 at runtime.
# This does not actually publish the port.
EXPOSE 8001

# --- Stage 7: Define the Runtime Command ---
# This is the command that will be executed when the container starts.
# We use '0.0.0.0' to make the server accessible from outside the container.
# Using '127.0.0.1' would only allow connections from within the container itself.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]