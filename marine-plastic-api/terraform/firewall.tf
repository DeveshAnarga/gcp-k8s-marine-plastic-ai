# CloudEco: Marine Plastic Detection System
# Author: Devesh Gurusinghe ()
# Purpose: Firewall rules for K8s API, kubelet, application, and internal traffic
# Date: 2026-04-30

# ============================================
# SSH
# ============================================
// Lets you gcloud ssh into VMs from the internet; scoped to instances tagged k8s (same tags on compute instances).
resource "google_compute_firewall" "allow_ssh" {
  name      = "${var.network_name}-allow-ssh"
  network   = google_compute_network.cloudeco_vpc.name
  direction = "INGRESS"
  priority  = 1000

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["k8s"]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

# ============================================
# KUBERNETES API (6443)
# ============================================
// Allows kube-apiserver port only from inside the VPC so workers can join and kubectl can reach the control plane privately.
resource "google_compute_firewall" "allow_k8s_api" {
  name      = "${var.network_name}-allow-k8s-api"
  network   = google_compute_network.cloudeco_vpc.name
  direction = "INGRESS"
  priority  = 1001

  source_ranges = [var.subnet_cidr]
  target_tags   = ["k8s"]

  allow {
    protocol = "tcp"
    ports    = ["6443"]
  }
}

# ============================================
# KUBELET (10250)
# ============================================
// Kubelet API between nodes (metrics, exec paths); restricted to subnet so it is not world-exposed.
resource "google_compute_firewall" "allow_kubelet" {
  name      = "${var.network_name}-allow-kubelet"
  network   = google_compute_network.cloudeco_vpc.name
  direction = "INGRESS"
  priority  = 1002

  source_ranges = [var.subnet_cidr]
  target_tags   = ["k8s"]

  allow {
    protocol = "tcp"
    ports    = ["10250"]
  }
}

# ============================================
# APP / NODEPORT RANGE
# ============================================
// Exposes HTTP/HTTPS and Kubernetes NodePort range (30000–32767) so LoadBalancer/NodePort services (e.g. 30080) reach pods from outside.
resource "google_compute_firewall" "allow_app" {
  name      = "${var.network_name}-allow-app"
  network   = google_compute_network.cloudeco_vpc.name
  direction = "INGRESS"
  priority  = 1003

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["k8s"]

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "30000-32767"]
  }
}

# ============================================
# INTERNAL (POD / NODE MESH)
# ============================================
// Wide internal allow within subnet so Calico/CNI, NodePort hairpin, and control-plane↔worker chatter work without per-port tuning.
resource "google_compute_firewall" "allow_internal" {
  name      = "${var.network_name}-allow-internal"
  network   = google_compute_network.cloudeco_vpc.name
  direction = "INGRESS"
  priority  = 1004

  source_ranges = [var.subnet_cidr]
  target_tags   = ["k8s"]

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
}
