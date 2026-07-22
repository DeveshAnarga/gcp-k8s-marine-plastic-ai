# CloudEco: Marine Plastic Detection System

## Overview
Kubernetes-orchestrated YOLOv8m inference API for marine plastic pollution detection.
Deployed on GCP e2 infrastructure with horizontal pod autoscaling and comprehensive benchmarking.

## Cluster Information
- **Region:** australia-southeast1-b (Sydney)
- **Public API base URL:** `http://34.151.142.31:30080` (HTTP, **not** HTTPS; port **30080** required)
- **Kubernetes Version:** v1.29.15
- **CNI:** Calico v3.26.1
- **Worker Nodes:** 2× e2-custom-4-8192 (4 vCPU, 8GB RAM each)

**Availability:** The public URL is only active while GCP VMs are running. VMs may be **stopped** or **removed** when not in use to **save cost**, so this URL **may be unreachable** at marking time. The submission includes Terraform, Kubernetes manifests, and Docker assets to **redeploy** the same stack; use `curl` on `/` or `/health` once the cluster is up.

## Docker image (canonical)

- **`dgur0007/marine-api:jpeg-optimized`** — same tag as `k8s/deployment.yaml`; use this for builds, pushes, and `kubectl set image`. Includes JPEG encoding for annotated images.

## Quick Start

### Prerequisites
- `kubectl` configured with cluster access
- `docker` (for building images)
- `locust` (for load testing)

### Deploy to Cluster
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get pods -l app=marine-plastic-api

# Check health
curl http://34.151.142.31:30080/health
```

### API Endpoints

**Browser-friendly:** `GET /` (live banner JSON) · `GET /health` · `GET /docs` (Swagger). **POST** only for `/api/predict` and `/api/annotate` (GET in browser → 405).

**POST /api/predict** - Detection only (JSON response)
```bash
curl -X POST http://34.151.142.31:30080/api/predict \
  -H "Content-Type: application/json" \
  -d '{"uuid":"test-1","image":"<base64_image>"}'
```

**POST /api/annotate** - Detection + annotated image (base64 response)
```bash
curl -X POST http://34.151.142.31:30080/api/annotate \
  -H "Content-Type: application/json" \
  -d '{"uuid":"test-1","image":"<base64_image>"}'
```

## Load Testing

### Run Benchmark
```bash
# Single user baseline
locust -f locustfile.py --host http://34.151.142.31:30080 -u 1 -r 1 -t 60 --headless

# Concurrent load test
locust -f locustfile.py --host http://34.151.142.31:30080 -u 5 -r 1 -t 60 --headless

# Interactive web UI
locust -f locustfile.py --host http://34.151.142.31:30080 --web
# Then visit http://localhost:8089
```

## Scaling

### Scale Pod Count
```bash
# 1 pod (baseline)
kubectl scale deployment marine-plastic-api --replicas=1

# 2 pods
kubectl scale deployment marine-plastic-api --replicas=2

# 4 pods
kubectl scale deployment marine-plastic-api --replicas=4

# 8 pods (maximum on 16Gi total memory)
kubectl scale deployment marine-plastic-api --replicas=8

# Verify scaling
kubectl get pods -l app=marine-plastic-api -o wide
```

## Architecture

### Infrastructure as Code
- **Terraform:** `terraform/` - GCP resources (VPC, instances, networking)
- **Ansible:** `terraform/k8s-bootstrap.yml` - Kubernetes bootstrap (kubeadm, kubelet, containerd)

### Application
- **FastAPI:** Async request handling with ThreadPoolExecutor for CPU-bound inference
- **YOLO:** YOLOv8m (220M parameters) for plastic detection
- **Docker:** Multi-stage build, non-root user, optimized layers

### Kubernetes
- **Deployment:** Rolling updates, readiness/liveness probes, resource limits
- **Service:** NodePort (port 30080) routing to pod port 8000
- **Resource Limits:** 1000m CPU, 2Gi memory per pod

## Performance Characteristics

| Pods | Stable Users | Breaking Point | Avg Latency |
|------|--------------|---|---|
| 1 | u=4 | u=5 (88% fail) | 23,000ms |
| 2 | u=5 | u=7 (92% fail) | 16,900ms |
| 4 | u=8 | u=10 (24% fail) | 18,100ms |
| 8 | u=15 | u=16+ (13% fail) | 17,500ms |

See `devesh_gurusinghe_.pdf` for detailed analysis.

## Docker image

Submission includes the **Dockerfile** and application source. The running cluster uses the published image:

- **`dgur0007/marine-api:jpeg-optimized`** (weights baked into the image; not shipped in this ZIP)

To redeploy the same tag on Kubernetes:

```bash
kubectl set image deployment/marine-plastic-api marine-plastic=dgur0007/marine-api:jpeg-optimized
kubectl rollout restart deployment/marine-plastic-api
```

## Support

For benchmarking details, see: `devesh_gurusinghe_.pdf`

---
**Assignment:** FIT5225 S1 2026 A1
**Student ID:** 
**Model:** YOLOv8m - Marine Plastic Pollution Detection
