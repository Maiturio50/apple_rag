# 🌐 Deep Multi-Page Web RAG Crawler & AI Assistant

A production-grade Retrieval-Augmented Generation (RAG) system built with **Python**, **LangChain**, and **ChromaDB**. This application allows users to input any public URL, recursively crawl its internal sub-links, convert messy web text into mathematical vector embeddings, and conduct an infinite semantic chat session via a clean **Streamlit** dashboard interface.

---

## 🚀 Key Features

* **Recursive Site-Wide Crawler:** Automatically scans a root domain, avoids infinite loops using visited url mapping, and prevents domain bleed.
* **Firewall Spoofing Protection:** Integrates customized human desktop browser headers to bypass automated scraper blockades.
* **In-Memory Vector Math Store:** Utilizes local ChromaDB instances running strictly in RAM to eliminate operating system file-locking conflicts and enable blazing-fast lookups.
* **Semantic Vector Embedding Math:** Uses OpenAI's `text-embedding-3-small` model to map sentence context, enabling the AI to answer intent questions even if exact text strings do not match.
* **Dynamic Streamlit Web UI:** Replaces rigid terminal boxes with a responsive browser-based dashboard interface.

---

## 🛠️ Technology Stack

* **Language:** Python 3.14
* **AI Orchestration Framework:** LangChain (LangChain-Chroma, LangChain-OpenAI, LangChain-Classic)
* **LLM Engine:** OpenAI `gpt-4o-mini` (Temperature: 0 for absolute factual calibration)
* **Vector Database:** ChromaDB (Local RAM Execution)
* **Scraping Architecture:** Requests + BeautifulSoup4

---

## 📦 Project Directory Structure

```text
📁 apple_rag/
 ├── 📄 app.py               # Production Streamlit Web UI Dashboard
 ├── 📄 rag_bot.py           # Core Backend CLI Ingestion & Evaluation Engine
 ├── 📄 apple_policy.txt     # Local Target Data Sample (Standard Evaluation)
 └── 📄 README.md            # Professional Portfolio Documentation
```

---

## ⚙️ Local Deployment Installation Guide

Follow these steps to clone and execute this application framework locally on your machine:

### 1. Pre-requisites & Package Installation
Open your terminal environment inside the project directory folder and run the installation modules:
```bash
pip3 install streamlit requests beautifulsoup4 langchain-chroma langchain-text-splitters langchain-openai langchain-classic
```

### 2. Authenticate Your Environment Credentials
Configure your secure secret OpenAI API access token credentials:
```bash
export OPENAI_API_KEY="sk-proj-yourActualKeyHere..."
```

### 3. Launch the Application Interface Server
Boot up the Streamlit engine to spin up the local server connection:
```bash
streamlit run app.py
```
*Your browser will automatically launch a tab at `http://localhost:8501` to initiate the session.*

---

## 🎓 Core Engineering Insights Learned

1. **Context Window Optimization:** Solved data truncation and AI hallucination exceptions by shifting chunk size mapping configurations to an 8,000-character vision threshold.
2. **State Management Locks:** Overcame local SQLite file corruption bottlenecks by completely decoupling disk storage and routing vector database embeddings instantly through active system memory (RAM).
3. **Decoupled System Architecture:** Successfully separated core mathematical backend execution scripts (`rag_bot.py`) from interactive front-facing interface skins (`app.py`).
