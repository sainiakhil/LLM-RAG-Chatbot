# --- Stage 1: Base Image ---
# Start from an official, lightweight Python runtime.
FROM python:3.11-slim

# --- Stage 2: Set Working Directory ---
# Create and set the working directory inside the container.
WORKDIR /app

# --- Stage 3: Install Dependencies ---
# Copy the UI-specific requirements file first to leverage Docker's layer caching.
COPY requirements-ui.txt .

# Install the packages from the requirements file.
RUN pip install --no-cache-dir -r requirements-ui.txt

# --- Stage 4: Copy Application Code ---
# Copy the Streamlit script into the working directory.
COPY chatbot_ui.py .

# --- Stage 5: Expose the Port ---
# Inform Docker that the container listens on Streamlit's default port, 8501.
EXPOSE 8501

# --- Stage 6: Healthcheck (Recommended for Production) ---
# This command periodically checks if the Streamlit app is still healthy.
# Cloud platforms like Google Cloud Run can use this to restart unhealthy containers.
HEALTHCHECK --interval=15s --timeout=5s \
  CMD curl -f http://localhost:8501/_stcore/health

# --- Stage 7: Define the Runtime Command ---
# This is the command that will be executed when the container starts.
# It's the equivalent of 'streamlit run chatbot_ui.py'.
CMD ["streamlit", "run", "chatbot_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]