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

## Installation

1. Clone the repository:
