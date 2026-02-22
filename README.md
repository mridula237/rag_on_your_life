# RAG on Your Life
### Cloud-Deployed Retrieval-Augmented Generation System

A production ready Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and perform semantic search with source grounded AI responses.

Deployed on AWS EC2 using FastAPI, ChromaDB, and OpenAI embeddings.

---

## Overview

RAG on Your Life enables users to:

- Upload PDF documents
- Automatically chunk and embed text
- Store embeddings in a vector database
- Perform semantic similarity search
- Generate grounded AI responses
- View document sources for transparency

This project demonstrates full stack AI system design and cloud deployment.

---

## System Architecture
User Browser

↓

FastAPI Backend (AWS EC2)

↓

Document Chunking Pipeline

↓

OpenAI Embeddings API

↓

ChromaDB Vector Store

↓

Similarity Search + Response Generation

---

## Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn
- LangChain
- ChromaDB (Vector Database)

### AI Layer
- OpenAI Embeddings API
- Retrieval-Augmented Generation (RAG)

### Infrastructure
- AWS EC2 (Ubuntu)
- SSH-based deployment
- Environment variable management
- Security group configuration

### Frontend
- HTML
- CSS
- JavaScript

---

##  How It Works

### 1. Upload
Users upload PDF documents through the web interface.

### 2.  Chunking
Documents are split into semantically meaningful chunks.

### 3.  Embedding
Each chunk is converted into a vector representation using OpenAI embeddings.

### 4. Indexing
Vectors are stored in ChromaDB for similarity search.

### 5. Querying
User queries are embedded and matched against stored vectors.

### 6.  Response Generation
Relevant chunks are retrieved and used to generate grounded AI responses with source citations.

---

## ☁️ Deployment

The application is deployed on:

- AWS EC2 (Ubuntu server)
- FastAPI served via Uvicorn
- Public access through EC2 public IP
- Configured via SSH and security groups

Key deployment steps included:

- Provisioning EC2 instance
- SSH configuration
- Cloning GitHub repository
- Virtual environment setup
- Dependency installation
- Environment variable configuration
- Production debugging and server management

---

## 🚀 Running Locally

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/rag_on_your_life.git
cd rag_on_your_life
```
### 2. Create a Virtual Environment
``` bash
python -m venv venv
source venv/bin/activate
```
### 3. Install Dependencies
``` bash
pip install -r requirements.txt
```
### 4. Set Environment Variable
``` bash
export OPENAI_API_KEY="your_api_key_here"
```
### 5. Start the Server
``` bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Then open:

http://localhost:8000
Environment Variables

Create a .env file or export:

OPENAI_API_KEY=your_key_here

Do not commit your .env file to version control.

## Key Features

Multi-document semantic search

Source citation tracking

Persistent vector storage

Cloud deployment on AWS EC2

Modular backend architecture

Production debugging and environment management

 ## Future Improvements

Dockerized deployment

HTTPS with Nginx + Let's Encrypt

Streaming response support

Document deletion endpoint

Multi-user authentication

Horizontal scaling with load balancer

## Skills Demonstrated

AI system architecture

Vector database integration

Backend API development

Cloud deployment and infrastructure management

Production debugging

End-to-end system engineering

## Author
Mridula Kalaiselvan

University of Arizona
