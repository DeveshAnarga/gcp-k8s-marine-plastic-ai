# Marine Plastic API — Operations cheat sheet

Quick reference for running the CloudEco marine plastic detection stack on GCP.

| Item | Value |
|------|-------|
| Region / zone | `australia-southeast1` / `australia-southeast1-b` |
| API port | NodePort `30080` |
| Docker image | `dgur0007/marine-api:jpeg-optimized` |
| App folder | `marine-plastic-api/` |

## Typical ops flow

1. Start VMs (`terraform apply` or `gcloud compute instances start …`)
2. SSH to the master node and confirm nodes are Ready
3. Scale the Deployment as needed
4. Hit the API / run Locust from your laptop against `http://<MASTER_IP>:30080`

The published Docker image is pulled by Kubernetes (`imagePullPolicy: Always`). Rebuild and push only when application code or model weights change.

## Static external IPs

VMs use Terraform `google_compute_address` resources, so stop/start keeps the same IPs. A full `terraform destroy` + `apply` may allocate new addresses — update `inventory.ini` and any docs accordingly.

```bash
gcloud compute instances describe k8s-master --zone=australia-southeast1-b \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

cd marine-plastic-api/terraform
terraform output master_external_ip
```

## Useful kubectl commands

```bash
kubectl get nodes
kubectl get pods -o wide
kubectl scale deployment marine-plastic-api --replicas=4
kubectl rollout status deployment/marine-plastic-api
curl http://<MASTER_IP>:30080/health
```

## Load testing

```bash
locust -f marine-plastic-api/locustfile.py \
  --host http://<MASTER_IP>:30080 -u 5 -r 1 -t 60 --headless
```
