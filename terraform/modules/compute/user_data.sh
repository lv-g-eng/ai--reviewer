#!/bin/bash
# User Data Script for EC2 Instances
# AI-Based Code Reviewer Infrastructure

set -e

# Update system packages
yum update -y

# Install required packages
yum install -y \
    docker \
    git \
    python3 \
    python3-pip \
    amazon-cloudwatch-agent \
    amazon-ssm-agent

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Add ec2-user to docker group
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Configure CloudWatch Agent with comprehensive metrics
# Collects CPU, memory, disk, network metrics (Requirement 7.4)
cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json <<EOF
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/app/*.log",
            "log_group_name": "/aws/ec2/${project_name}/${environment}/app",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30
          },
          {
            "file_path": "/var/log/docker/*.log",
            "log_group_name": "/aws/ec2/${project_name}/${environment}/docker",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30
          },
          {
            "file_path": "/var/log/messages",
            "log_group_name": "/aws/ec2/${project_name}/${environment}/system",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "AICodeReviewer/${environment}",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {
            "name": "cpu_usage_idle",
            "rename": "CPU_IDLE",
            "unit": "Percent"
          },
          {
            "name": "cpu_usage_iowait",
            "rename": "CPU_IOWAIT",
            "unit": "Percent"
          },
          {
            "name": "cpu_usage_system",
            "rename": "CPU_SYSTEM",
            "unit": "Percent"
          },
          {
            "name": "cpu_usage_user",
            "rename": "CPU_USER",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60,
        "resources": ["*"],
        "totalcpu": true
      },
      "disk": {
        "measurement": [
          {
            "name": "used_percent",
            "rename": "DISK_USED_PERCENT",
            "unit": "Percent"
          },
          {
            "name": "free",
            "rename": "DISK_FREE",
            "unit": "Gigabytes"
          },
          {
            "name": "used",
            "rename": "DISK_USED",
            "unit": "Gigabytes"
          },
          {
            "name": "inodes_free",
            "rename": "DISK_INODES_FREE",
            "unit": "Count"
          }
        ],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "diskio": {
        "measurement": [
          {
            "name": "io_time",
            "rename": "DISKIO_TIME",
            "unit": "Milliseconds"
          },
          {
            "name": "write_bytes",
            "rename": "DISKIO_WRITE_BYTES",
            "unit": "Bytes"
          },
          {
            "name": "read_bytes",
            "rename": "DISKIO_READ_BYTES",
            "unit": "Bytes"
          },
          {
            "name": "writes",
            "rename": "DISKIO_WRITES",
            "unit": "Count"
          },
          {
            "name": "reads",
            "rename": "DISKIO_READS",
            "unit": "Count"
          }
        ],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "mem": {
        "measurement": [
          {
            "name": "mem_used_percent",
            "rename": "MEMORY_USED_PERCENT",
            "unit": "Percent"
          },
          {
            "name": "mem_available",
            "rename": "MEMORY_AVAILABLE",
            "unit": "Megabytes"
          },
          {
            "name": "mem_used",
            "rename": "MEMORY_USED",
            "unit": "Megabytes"
          },
          {
            "name": "mem_total",
            "rename": "MEMORY_TOTAL",
            "unit": "Megabytes"
          }
        ],
        "metrics_collection_interval": 60
      },
      "net": {
        "measurement": [
          {
            "name": "bytes_sent",
            "rename": "NETWORK_BYTES_SENT",
            "unit": "Bytes"
          },
          {
            "name": "bytes_recv",
            "rename": "NETWORK_BYTES_RECEIVED",
            "unit": "Bytes"
          },
          {
            "name": "packets_sent",
            "rename": "NETWORK_PACKETS_SENT",
            "unit": "Count"
          },
          {
            "name": "packets_recv",
            "rename": "NETWORK_PACKETS_RECEIVED",
            "unit": "Count"
          },
          {
            "name": "drop_in",
            "rename": "NETWORK_PACKETS_DROPPED_IN",
            "unit": "Count"
          },
          {
            "name": "drop_out",
            "rename": "NETWORK_PACKETS_DROPPED_OUT",
            "unit": "Count"
          },
          {
            "name": "err_in",
            "rename": "NETWORK_ERRORS_IN",
            "unit": "Count"
          },
          {
            "name": "err_out",
            "rename": "NETWORK_ERRORS_OUT",
            "unit": "Count"
          }
        ],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "netstat": {
        "measurement": [
          {
            "name": "tcp_established",
            "rename": "TCP_ESTABLISHED",
            "unit": "Count"
          },
          {
            "name": "tcp_time_wait",
            "rename": "TCP_TIME_WAIT",
            "unit": "Count"
          },
          {
            "name": "tcp_close_wait",
            "rename": "TCP_CLOSE_WAIT",
            "unit": "Count"
          }
        ],
        "metrics_collection_interval": 60
      },
      "processes": {
        "measurement": [
          {
            "name": "running",
            "rename": "PROCESSES_RUNNING",
            "unit": "Count"
          },
          {
            "name": "sleeping",
            "rename": "PROCESSES_SLEEPING",
            "unit": "Count"
          },
          {
            "name": "dead",
            "rename": "PROCESSES_DEAD",
            "unit": "Count"
          },
          {
            "name": "total",
            "rename": "PROCESSES_TOTAL",
            "unit": "Count"
          }
        ],
        "metrics_collection_interval": 60
      }
    },
    "append_dimensions": {
      "AutoScalingGroupName": "\$${aws:AutoScalingGroupName}",
      "InstanceId": "\$${aws:InstanceId}",
      "InstanceType": "\$${aws:InstanceType}",
      "Environment": "${environment}",
      "Project": "${project_name}"
    }
  }
}
EOF

# Start CloudWatch Agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json

# Create application directories
mkdir -p /opt/app
mkdir -p /var/log/app
mkdir -p /var/log/docker

# Set permissions
chown -R ec2-user:ec2-user /opt/app
chown -R ec2-user:ec2-user /var/log/app

# Create health check endpoint script
cat > /opt/app/health_check.sh <<'HEALTH_EOF'
#!/bin/bash
# Simple health check that returns 200 OK
echo "HTTP/1.1 200 OK"
echo "Content-Type: application/json"
echo ""
echo '{"status":"healthy","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'
HEALTH_EOF

chmod +x /opt/app/health_check.sh

# Create systemd service for health check endpoint
cat > /etc/systemd/system/health-check.service <<'SERVICE_EOF'
[Unit]
Description=Health Check Endpoint
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/app
ExecStart=/bin/bash -c 'while true; do echo -e "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"status\":\"healthy\"}" | nc -l -p 8000 -q 1; done'
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Enable and start health check service
systemctl daemon-reload
systemctl enable health-check.service
systemctl start health-check.service

# Signal completion
echo "User data script completed successfully" > /var/log/user-data-complete.log
