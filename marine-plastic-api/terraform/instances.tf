# CloudEco: Marine Plastic Detection System
# Author: Devesh Gurusinghe ()
# Purpose: GCP VM instances for Kubernetes master and worker nodes
# Date: 2026-04-30

# ============================================
# BOOT IMAGE
# ============================================
// Resolves the latest Ubuntu 22.04 image for the family name so rebuilds get security patches without hard-coding image IDs.
data "google_compute_image" "ubuntu" {
  family  = var.image_family
  project = "ubuntu-os-cloud"
}

# ============================================
# STATIC EXTERNAL IPs
# ============================================
// One reserved public IP per VM so Terraform destroy/recreate or VM replace does not change your NodePort/LB endpoint unexpectedly.
resource "google_compute_address" "node_ip" {
  count  = var.vm_count
  name   = "${var.vm_names[count.index]}-ip"
  region = var.region
}

# ============================================
# INSTANCES (MASTER + WORKERS)
# ============================================
// Provisions 1 control-plane + 2 workers in the same zone; count/index 0 is master. allow_stopping_for_update permits machine-type changes without replace.
resource "google_compute_instance" "node" {
  count                     = var.vm_count
  name                      = var.vm_names[count.index]
  zone                      = var.zone
  machine_type              = var.machine_type
  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = data.google_compute_image.ubuntu.self_link
      size  = 50
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.cloudeco_subnet.id
    // Stable internal IPs: .11 master, .12 worker-1, .13 worker-2 when subnet is 10.0.1.0/24
    network_ip = cidrhost(var.subnet_cidr, 10 + count.index)

    access_config {
      nat_ip = google_compute_address.node_ip[count.index].address
    }
  }

  // Must match firewall target_tags so SSH/NodePort rules apply to these VMs.
  tags = ["k8s", "kubernetes"]

  labels = {
    environment  = var.environment
    node_type    = count.index == 0 ? "master" : "worker"
    cluster_role = count.index == 0 ? "master" : "worker"
  }
}
