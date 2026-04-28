# 🧠 AI Microservice (FastAPI + LLM + RAG Engine)

A production-ready AI microservice built with **FastAPI** that powers an intelligent tutoring system with multi-LLM support, retrieval-augmented generation (RAG), caching, and multi-tenant architecture.

---

## 🚀 Features

- 🔌 Multi-LLM Provider Support
  - OpenAI
  - Google Gemini
  - Vertex AI (extensible)
  - Mock fallback (safe mode)

- 🧠 RAG (Retrieval-Augmented Generation)
  - Vector search using Qdrant
  - Context-aware tutoring responses

- ⚡ High Performance API
  - FastAPI async architecture
  - Streaming support (LLM responses)
  - Low-latency caching layer

- 🗄️ Redis Caching
  - Response caching for faster replies
  - Reduces LLM cost and latency

- 🔐 Multi-Tenant Design
  - Tenant isolation via request headers
  - Scalable SaaS-ready architecture

- 📊 Quota Management
  - Token-based usage tracking
  - Basic rate limiting per tenant

- 🧩 Extensible Architecture
  - Clean service-layer design
  - Easy to plug new LLM providers

---

## 🏗️ System Architecture

```text
Client
  ↓
FastAPI Gateway
  ↓
Tutor API (/api/v1/tutor/explain)
  ↓
LLM Service (OpenAI / Gemini / Vertex)
  ↓
RAG Service (Qdrant Vector DB)
  ↓
Redis Cache + Quota Service