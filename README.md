# Job Scraper and Matcher

An automated system for scraping and filtering software engineering job postings from major tech companies. The system uses both text-based pattern matching and AI-powered analysis to identify suitable entry-level positions.

## Features

- **Multi-Company Support**: Scrapes job listings from:
  - Meta
  - Microsoft
  - Apple
  - More companies planned (Google, Amazon, etc.)

- **Smart Filtering**: 
  - Text-based pattern matching to identify entry-level positions
  - AI-powered job matching using local LLM (via Ollama)
  - Qualification analysis
  - Location filtering

- **Privacy & Security**:
  - Built-in Tor support for anonymous scraping
  - Rate limiting and request rotation
  - Browser impersonation

- **Data Storage**:
  - SQLite database for job storage
  - Efficient caching system
  - Tracks application status and match quality

## Prerequisites

- Python 3.x
- Tor (optional, for anonymous scraping)
- Ollama (for AI-powered matching)

## Ollama Setup

1. Install Ollama:
   - **Mac/Linux**:
     ```bash
     curl -fsSL https://ollama.com/install.sh | sh
     ```
   - **Windows**:
     - Download and install from [Ollama.com](https://ollama.com)

2. Start the Ollama service:
   ```bash
   ollama serve
   ```

3. In a new terminal, pull and run the model:
   ```bash
   # Pull the model (only needed once)
   ollama pull mistral

   # Test the model
   ollama run mistral "Hello, how are you?"
   ```

4. For development, you can interact with Ollama via HTTP:
   ```bash
   curl http://localhost:11434/api/generate -d '{
     "model": "mistral",
     "prompt": "Why is the sky blue?"
   }'
   ```

### Troubleshooting

- **Port in Use**: If port 11434 is already in use, check for existing Ollama processes:
  ```bash
  ps aux | grep ollama
  # or
  lsof -i :11434
  ```

- **Permission Issues**: On Linux/Mac, you might need to run with sudo:
  ```bash
  sudo ollama serve
  ```

- **Model Download Issues**: If model download fails, try:
  ```bash
  ollama pull mistral --insecure
  ```
