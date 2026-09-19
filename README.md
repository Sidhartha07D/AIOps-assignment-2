# AIOps Assignment 2
**Course:** DA3408 | **Student:** Sidhartha Durgam (Roll Number: DA24B003)

---

##  Overview

This assignment focuses on using Docker, Docker Compose, Redis, and Kubernetes.



##  Repository Structure

```text
AIops-assignment-2/
├── README.md
├── AI_Ops_Assignment_2_Report.pdf
│  
│
├── question1/
│   ├── Dockerfile.multistage
│   ├── Dockerfile.naive
│   ├── app.py
│   ├── model.joblib
│   ├── requirements.txt
│   ├── spam_dataset.csv
│   ├── train.py
│   ├── q1_docker_images_size.png
│   ├── q1_healthz_endpoint.png
│   ├── q1_multi_build_and_run.png
│   ├── q1_naive_build_and_run.png
│   ├── q1_predict_endpoint_ham.png
│   └── q1_predict_endpoint_spam.png
│
├── question2/
│   ├── Dockerfile.multistage
│   ├── app.py
│   ├── docker-compose.yml
│   ├── model.joblib
│   ├── requirements.txt
│   ├── spam_dataset.csv
│   ├── train.py
│   ├── q2_cache_hit.png
│   └── q2_cache_miss.png
│
├── question3/
│   ├── shards/
│   │   ├── shard_0.csv
│   │   ├── shard_1.csv
│   │   ├── shard_2.csv
│   │   ├── shard_3.csv
│   │   ├── shard_4.csv
│   │   ├── shard_5.csv
│   │   ├── shard_6.csv
│   │   └── shard_7.csv
│   ├── Dockerfile.validator
│   ├── collect_results.py
│   ├── generate_shards.py
│   ├── job-validator.yaml
│   ├── q3_api_results.png
│   ├── q3_execution_evidence.png
│   └── validate_worker.py
│
└── question4/
    ├── Dockerfile.multistage
    ├── api-deployment.yaml
    ├── app.py
    ├── model.joblib
    ├── q4_rolling_update.png
    ├── q4_self_healing.png
    └── requirements.txt
```

##  How to Read This Assignment

### **Question 1: Single-Stage vs. Multi-Stage Docker**

**Files:** `Dockerfile` / `Dockerfile.multistage`  
**Evidence:** `screenshots/`

**Summary:** Built and tested both a naive single-stage Docker image and an optimized multi-stage image for the spam-detection API.

| Image | Size(disk space) |(for the other space comparison look at the screenshot evidence in repo
|------|------:|
| Naive | 2.28 GB |
| Multi-stage | 715 MB |

Approximate image-size reduction: **68-69%**

The multi-stage build uses `python:3.14-slim` as the runtime image and keeps the builder environment out of the final image.

Both images were tested successfully using:

- `GET /healthz`
- `POST /predict`
- Spam classification
- Ham classification

---

### **Question 2: Multi-Container Orchestration with Docker Compose**

 **Files:** `docker-compose.yml`, `app.py`  
 **Evidence:** `screenshots/`

**Summary:** Extended the spam-detection API with a Redis caching layer and orchestrated the application using Docker Compose.

The Compose stack contains:

- `api` — FastAPI application
- `cache` — official `redis:7-alpine` image



The exact input text is used as the Redis cache key and cached predictions have a **60-second TTL**.

### Cache Performance

| Request | Result | Time |
|---------|--------|-----:|
| First request | Cache MISS | 14.25 ms |
| Second identical request | Cache HIT | 0.36 ms |

The recorded cache hit was approximately **39.6× faster** than the cache miss.

---

### **Question 3: Kubernetes Indexed Job**

 **Files:** `job-validator.yaml`, `validate_worker.py`, `collect_results.py`, `generate_shards.py`  
 **Evidence:** `screenshots/`

**Summary:** Implemented a Kubernetes Indexed Job to validate 8 partitioned CSV shards.

Cluster resources:

```text
2 nodes × 2 CPUs = 4 CPUs
```

Job configuration:

```text
Completions: 8
Parallelism: 4
CPU per pod: 1 CPU
Completion mode: Indexed
```

Four pods were demonstrated running concurrently across the available nodes.

Each Indexed Job completion processes exactly one shard using `JOB_COMPLETION_INDEX`.

### Validation Results

| Shard | Invalid Rows |
|------:|-------------:|
| 0 | 11 |
| 1 | 9 |
| 2 | 9 |
| 3 | 8 |
| 4 | 10 |
| 5 | 12 |
| 6 | 5 |
| 7 | 13 |
| **Total** | **77** |

Results were collected through the Kubernetes API by reading pod logs rather than using a shared volume.

---

### **Question 4: Kubernetes Deployment — Self-Healing & Rolling Updates**

 **File:** `deployment.yaml`  
 **Evidence:** `screenshots/`

**Summary:** Deployed the spam-detection API using a Kubernetes Deployment with 2 replicas and a ClusterIP Service.

The Deployment includes:

- 2 replicas
- CPU and memory requests/limits
- `/healthz` readiness probe
- ClusterIP Service

### Self-Healing

A running API pod was manually deleted and Kubernetes automatically recreated the pod through the Deployment/ReplicaSet mechanism while maintaining the desired replica count.

### Rolling Update

The API was updated from:

```text
spam-api-multi:v1
```

to:

```text
spam-api-multi:v2
```

The rollout was verified using:

```bash
kubectl set image deployment/spam-api worker=spam-api-multi:v2
kubectl rollout status deployment/spam-api
kubectl rollout history deployment/spam-api
```

The v2 application exposes its version through `/healthz`:

```json
{
  "status": "OK",
  "version": "v2"
}
```

---

##  Evidence

The repository contains execution evidence for:

- Docker single-stage build
- Docker multi-stage build
- Docker image size comparison
- `/healthz` and `/predict` testing
- Docker Compose deployment
- Redis cache MISS/HIT behavior
- Cache performance measurements
- Kubernetes Indexed Job execution
- Pod concurrency and node placement
- Per-shard validation results
- Kubernetes self-healing
- Kubernetes rolling update
- Rollout status and history

A separate assignment video contains the working demonstration and execution walkthrough.

##  Quick Start ;; LOOK AT THE VIDEO FOR BETTER UNDERSTANDING AND IF ANY MISTAKES BELOW FOLLOW WHATEVER IS DONE IN VIDEO

Each question is self-contained in its own directory. Run the commands from the repository root unless otherwise specified.

---

### Question 1 — Single-Stage vs Multi-Stage Docker

Go to the Question 1 directory:

```bash
cd question1
```

Generate the dataset and model:

```bash
python train.py
```

Build the naive single-stage image:

```bash
docker build -t spam-api-naive -f Dockerfile.naive .
```

Run the naive image:

```bash
docker run --rm -p 8000:8000 --name naive-run spam-api-naive
```

Build the multi-stage image:

```bash
docker build -t spam-api-multi -f Dockerfile.multistage .
```

Run the multi-stage image:

```bash
docker run --rm -p 8000:8000 --name multi-run spam-api-multi
```

Check image sizes:

```bash
docker images | grep spam-api
```

API endpoints:

```text
GET  http://localhost:8000/healthz
POST http://localhost:8000/predict
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

### Question 2 — Docker Compose + Redis

Go to the Question 2 directory:

```bash
cd question2
```

Generate the dataset and model if required:

```bash
python train.py
```

Start the API and Redis services:

```bash
docker compose up --build
```

The stack contains:

```text
api    → FastAPI application
cache  → Redis 7 Alpine
```



Open Swagger UI:

```text
http://localhost:8000/docs
```

Send the same prediction request twice to demonstrate:

```text
First request  → cache_miss
Second request → cache_hit
```

The recorded test showed:

```text
Cache MISS → 14.25 ms
Cache HIT  → 0.36 ms
```

Stop the Compose stack:

```bash
docker compose down
```

---

### Question 3 — Kubernetes Indexed Job

Go to the Question 3 directory:

```bash
cd question3
```

Generate the eight validation shards:

```bash
python generate_shards.py
```

Ensure Minikube is running:

```bash
minikube start
```

Make the validator image available to the Minikube cluster and build it using:

```bash
minikube image build -t shard-validator:latest -f Dockerfile.validator .
```

Apply the Indexed Job:

```bash
kubectl apply -f job-validator.yaml
```

Monitor the Job pods:

```bash
kubectl get pods -o wide -w
```

After completion, collect the results through the Kubernetes API:

```bash
python collect_results.py
```

The Job configuration is:

```text
Completions  : 8
Parallelism  : 4
Completion   : Indexed
CPU per pod  : 1 CPU
```

The validation results are:

```text
Shard 0 → 11 invalid rows
Shard 1 →  9 invalid rows
Shard 2 →  9 invalid rows
Shard 3 →  8 invalid rows
Shard 4 → 10 invalid rows
Shard 5 → 12 invalid rows
Shard 6 →  5 invalid rows
Shard 7 → 13 invalid rows

Total → 77 invalid rows
```

---

### Question 4 — Kubernetes Deployment, Self-Healing & Rolling Update

Go to the Question 4 directory:

```bash
cd question4
```

Ensure Minikube is running:

```bash
minikube start
```

The Kubernetes manifest is:

```text
api-deployment.yaml
```

The Deployment uses:

```text
2 replicas
CPU and memory requests/limits
/healthz readiness probe
ClusterIP Service
```

Apply the Deployment:

```bash
kubectl apply -f api-deployment.yaml
```

Check the Deployment and pods:

```bash
kubectl get deployment
kubectl get pods
kubectl get service
```

For the self-healing demonstration, delete one running API pod:

```bash
kubectl delete pod <pod-name>
```

Then monitor the replacement:

```bash
kubectl get pods -w
```

For the rolling update, update the Deployment image to the v2 image:

```bash
kubectl set image deployment/spam-api worker=spam-api-multi:v2
```

Check rollout completion:

```bash
kubectl rollout status deployment/spam-api
```

Check rollout history:

```bash
kubectl rollout history deployment/spam-api
```

The updated v2 application exposes the version through:

```text
GET /healthz
```

with a response containing:

```json
{
  "status": "OK",
  "version": "v2"
}
```

---

### Evidence

Execution evidence for all four questions is included in the corresponding question directories:

```text
question1/  → Docker build, image size, API evidence
question2/  → Redis cache MISS/HIT evidence
question3/  → Indexed Job execution and API results
question4/  → Self-healing and rolling-update evidence
```

The complete working demonstration is also included in the submitted assignment video.

##  AI Disclosure
**How they were used:**  
I used AI mainly to understand the existing concepts better that were taught in class and also to learn newer ones which were required for this assignment better and faster.I also used them for writing codes and also cross verifying it with both AI and also by me, I even used to solve some terminal errors that I was getting while running the commands .Also took help for formatting the report (also some part of readme in here but this particular section is not written by AI but written by me ) in latex but before that I had to give my written answers for everything with the screenshots as evidence of what I did and also my code for better understanding , still many technical decisions had to be made by me .And everything done by AI was verified by me in this assignment.

**Tools used:** ChatGPT and Gemini

**Impact:**  
The tools helped speed up learning, debugging, and documentation. All reported results and measurements are from my actual executions, and I reviewed and verified the final code and configurations before submission.

---

##  Where to Find Everything

| What | Where |
|------|-------|
| **Q1 Docker** | `Dockerfile` + `Dockerfile.multistage` |
| **Q2 Docker Compose + Redis** | `docker-compose.yml` + `app.py` |
| **Q3 Indexed Job** | `job-validator.yaml` + `validate_worker.py` + `collect_results.py` + `generate_shards.py` |
| **Q4 Deployment** | `deployment.yaml` |
| **Execution Evidence** | `screenshots/` |
| **Demonstration** | `video/` |
| **ML Model** | `model.joblib` |
| **Dataset** | `spam_dataset.csv` |

---

*For complete implementation details and execution evidence, refer to the source files, screenshots, and demonstration video included in the repository.*
