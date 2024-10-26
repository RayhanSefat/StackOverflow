# StackOverflow

A web application built with React, Flask, MongoDB, and MinIO.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Node.js** (v14 or above)
- **Python** (v3.8 or above)
- **MongoDB** (v4 or above)
- **MinIO** (latest version)
- **Docker and Docker Compose** (recommended for local services)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/RayhanSefat/StackOverflow
cd StackOverflow
```

# Flask configuration
FLASK_ENV=development
SECRET_KEY=rayhan123

# MongoDB configuration
MONGO_URI=mongodb://localhost:27017/stack-overflow

# MinIO configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=stack-overflow

