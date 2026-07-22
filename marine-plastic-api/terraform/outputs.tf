# CloudEco: Marine Plastic Detection System
# Author: Devesh Gurusinghe ()
# Purpose: Terraform outputs for cluster IPs and SSH access commands
# Date: 2026-04-30

# ============================================
# NETWORK — MASTER
# ============================================
// Private IP used in kubeadm join commands and internal API URLs; not reachable from the internet.
output "master_internal_ip" {
  description = "Internal IP of the Kubernetes master node"
  value       = google_compute_instance.node[0].network_interface[0].network_ip
  sensitive   = false
}

// Public IP you use for SSH to master and (with NodePort) often the same host IP you curl for :30080.
output "master_external_ip" {
  description = "Static external IP of the Kubernetes master node"
  value       = google_compute_address.node_ip[0].address
  sensitive   = false
}

# ============================================
# NETWORK — WORKERS
# ============================================
// Worker-only RFC1918 addresses; pods route via CNI; useful when debugging service endpoints from inside the VPC.
output "worker_internal_ips" {
  description = "Internal IPs of worker nodes"
  value = [
    google_compute_instance.node[1].network_interface[0].network_ip,
    google_compute_instance.node[2].network_interface[0].network_ip
  ]
  sensitive = false
}

// Worker public IPs if you SSH to workers directly or run diagnostics from outside the cluster.
output "worker_external_ips" {
  description = "Static external IPs of worker nodes"
  value = [
    google_compute_address.node_ip[1].address,
    google_compute_address.node_ip[2].address
  ]
  sensitive = false
}

# ============================================
# CLUSTER SUMMARY
# ============================================
// Single structured output for reports: name, both IPs, zone, role—handy for inventory or README tables.
output "all_nodes" {
  description = "Complete information for all cluster nodes"
  value = [
    for i in range(var.vm_count) : {
      name        = var.vm_names[i]
      internal_ip = google_compute_instance.node[i].network_interface[0].network_ip
      external_ip = google_compute_address.node_ip[i].address
      zone        = var.zone
      node_type   = i == 0 ? "master" : "worker"
    }
  ]
  sensitive = false
}

# ============================================
# SSH HELPERS
# ============================================
// Copy-paste from terraform output into terminal to open a shell on the control plane.
output "ssh_master_command" {
  description = "Command to SSH into the master node"
  value       = "gcloud compute ssh ${var.vm_names[0]} --zone=${var.zone}"
  sensitive   = false
}

// Same as master helper but for every node—speeds up parallel bootstrap when pasting into three terminals.
output "ssh_all_commands" {
  description = "SSH commands for all nodes"
  value = {
    master   = "gcloud compute ssh ${var.vm_names[0]} --zone=${var.zone}"
    worker-1 = "gcloud compute ssh ${var.vm_names[1]} --zone=${var.zone}"
    worker-2 = "gcloud compute ssh ${var.vm_names[2]} --zone=${var.zone}"
  }
  sensitive = false
}
