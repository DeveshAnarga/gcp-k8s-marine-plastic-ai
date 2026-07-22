# CloudEco — GCP Kubernetes Marine Plastic Detection AI

**Production-style computer vision API on GCP — Terraform, Kubernetes, Docker, YOLOv8**

[![GCP](https://img.shields.io/badge/GCP-Compute%20Engine%20%7C%20VPC-4285F4?style=flat&logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![YOLO](https://img.shields.io/badge/ML-YOLOv8m-FF6F00?style=flat)](https://docs.ultralytics.com/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

> University project (FIT5225) building an **end-to-end cloud ML pipeline** to detect marine plastic pollution in images — from infrastructure provisioning through load-tested Kubernetes deployment.

**Author:** Devesh Gurusinghe · Monash University

---

## Why this project matters (for recruiters)

This project demonstrates **full-stack cloud engineering for ML inference**, not just a notebook model:

| Layer | Technology | What it shows |
|-------|------------|---------------|
| **Infrastructure** | Terraform | GCP VPC, firewall rules, VM provisioning (IaC) |
| **Cluster bootstrap** | Ansible + kubeadm | Self-managed Kubernetes on Compute Engine |
| **Containerisation** | Docker | Multi-stage build, non-root user, baked model weights |
| **Orchestration** | Kubernetes | Deployments, NodePort service, probes, horizontal scaling |
| **API** | FastAPI | Async endpoints, thread-pool inference, OpenAPI docs |
| **ML** | YOLOv8m | Object detection for marine plastic pollution |
| **Performance** | Locust | Load testing, latency analysis, pod scaling benchmarks |

**Key engineering highlights:**

- **Infrastructure as Code** — entire GCP stack reproducible via Terraform + Ansible
- **Self-managed K8s cluster** — 1 master + 2 worker nodes (`e2-custom-4-8192`, Sydney region)
- **Async FastAPI design** — CPU-bound YOLO inference offloaded to `ThreadPoolExecutor`
- **Production probes** — liveness/readiness on `/health`; model loaded at startup
- **Load tested at scale** — benchmarked 1→8 pod replicas with Locust (breaking points documented)
- **Optimised annotate path** — JPEG encoding reduced response size under concurrent load
- **Published Docker image** — `dgur0007/marine-api:jpeg-optimized` on Docker Hub

---

## Architecture

```text
                    ┌─────────────────────────────────────────┐
                    │           GCP (australia-southeast1)       │
                    │  ┌─────────┐  Terraform + Ansible         │
                    │  │   VPC   │  → k8s-master + 2 workers     │
                    │  └────┬────┘                               │
                    │       │                                    │
                    │  ┌────▼──────────────────────────────┐    │
                    │  │     Kubernetes Cluster (v1.29)     │    │
                    │  │  ┌─────────────────────────────┐  │    │
                    │  │  │  marine-plastic-api pods    │  │    │
                    │  │  │  FastAPI + YOLOv8m (Docker) │  │    │
                    │  │  └──────────────┬──────────────┘  │    │
                    │  │                 │ NodePort :30080   │    │
                    │  └─────────────────┼───────────────────┘    │
                    └────────────────────┼────────────────────────┘
                                         │
                              POST /api/predict
                              POST /api/annotate
                                         │
                                    Client / Locust
```

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Live service banner |
| `GET` | `/health` | Kubernetes probe endpoint |
| `GET` | `/docs` | Swagger UI |
| `POST` | `/api/predict` | Detect plastic — JSON bounding boxes |
| `POST` | `/api/annotate` | Detect + return annotated JPEG (base64) |

**Example predict request:**

```bash
curl -X POST http://<NODE_IP>:30080/api/predict \
  -H "Content-Type: application/json" \
  -d '{"uuid":"demo-1","image":"<base64_image>"}'
```

---

## Performance (Locust benchmarks)

| Pods | Stable users | Breaking point | Avg latency |
|------|-------------|----------------|-------------|
| 1 | u=4 | u=5 (88% fail) | ~23s |
| 2 | u=5 | u=7 (92% fail) | ~17s |
| 4 | u=8 | u=10 (24% fail) | ~18s |
| 8 | u=15 | u=16+ (13% fail) | ~17.5s |

---

## Repository layout

```text
marine-plastic-api/
├── app/                 FastAPI application (main, inference, schemas)
├── k8s/                 Kubernetes Deployment + NodePort Service
├── terraform/           GCP VPC, VMs, firewall (Terraform)
│   └── k8s-bootstrap.yml  Ansible kubeadm bootstrap
├── Dockerfile           Container image definition
├── locustfile.py        Load testing scenarios
└── README.md            Detailed deployment & ops guide
```

---

## Quick start

### Deploy to existing cluster

```bash
kubectl apply -f marine-plastic-api/k8s/deployment.yaml
kubectl apply -f marine-plastic-api/k8s/service.yaml
curl http://<NODE_IP>:30080/health
```

### Rebuild infrastructure (Terraform)

```bash
cd marine-plastic-api/terraform
terraform init && terraform apply
# Then run Ansible bootstrap per terraform/k8s-bootstrap.yml
```

### Load test

```bash
locust -f marine-plastic-api/locustfile.py --host http://<NODE_IP>:30080 -u 5 -r 1 -t 60 --headless
```

---

## Docker image

Pre-built image with model weights included:

```text
dgur0007/marine-api:jpeg-optimized
```

---

## Tech stack

**Cloud:** GCP Compute Engine, VPC, Firewall  
**IaC:** Terraform, Ansible  
**Orchestration:** Kubernetes (kubeadm, Calico CNI)  
**Backend:** Python, FastAPI, Uvicorn  
**ML:** Ultralytics YOLOv8m  
**Testing:** Locust  
**Container:** Docker  

---

## Related project

See also [**aws-gcp-ecolens-ai**](https://github.com/DeveshAnarga/aws-gcp-ecolens-ai) — multi-cloud serverless wildlife detection (AWS Lambda + GCP Cloud Run).

---

## License

MIT — see [LICENSE](LICENSE).
