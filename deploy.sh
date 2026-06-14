#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
#   XENO ORACLE — PRODUCTION DEPLOY TO AWS EC2
#   Run from project root (Git Bash / WSL on Windows, or bash on Linux/Mac):
#     bash deploy.sh
#   Or with custom PEM: PEM_KEY=/path/to/key.pem bash deploy.sh
# ═══════════════════════════════════════════════════════════════════════════════
set -e

EC2_IP="3.87.12.186"
EC2_USER="ec2-user"
REMOTE_DIR="/home/ec2-user/xeno-oracle"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Detect PEM key path (Windows-aware) ────────────────────────────────────
if [ -n "$PEM_KEY" ]; then
  : # Use whatever the caller supplied
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Git Bash on Windows
    PEM_KEY="C:/Users/Win11/OneDrive/Desktop/Xeno.pem"
elif [ -f "/mnt/c/Users/Win11/OneDrive/Desktop/Xeno.pem" ]; then
    # WSL
    cp /mnt/c/Users/Win11/OneDrive/Desktop/Xeno.pem /tmp/Xeno.pem
    chmod 400 /tmp/Xeno.pem
    PEM_KEY="/tmp/Xeno.pem"
elif [ -f "$HOME/Documents/xeno-oracle.pem" ]; then
  PEM_KEY="$HOME/Documents/xeno-oracle.pem"
else
  echo "❌ Could not find Xeno.pem. Set PEM_KEY=/path/to/key.pem and re-run."
  echo "   Example: PEM_KEY=~/Desktop/Xeno.pem bash deploy.sh"
  exit 1
fi

chmod 400 "$PEM_KEY" 2>/dev/null || true

echo "════════════════════════════════════════════════════════════════"
echo "  XENO ORACLE v2.0 — Deploying to EC2 $EC2_IP"
echo "  PEM key: $PEM_KEY"
echo "════════════════════════════════════════════════════════════════"

# ── Sync project files to EC2 ─────────────────────────────────────────────
echo ""
echo "📦 Syncing project files to EC2..."
rsync -avz --progress \
  --exclude '.git' \
  --exclude 'node_modules' \
  --exclude '.next' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude '*.db' \
  --exclude '*.db-shm' \
  --exclude '*.db-wal' \
  --exclude '.env' \
  -e "ssh -i $PEM_KEY -o StrictHostKeyChecking=no" \
  "$PROJECT_DIR/" \
  "$EC2_USER@$EC2_IP:$REMOTE_DIR/"
echo "✅ Files synced."

# ── Upload .env.production as .env on remote ──────────────────────────────
echo ""
echo "🔑 Uploading production environment variables..."
scp -i "$PEM_KEY" -o StrictHostKeyChecking=no \
  "$PROJECT_DIR/.env.production" \
  "$EC2_USER@$EC2_IP:$REMOTE_DIR/.env"
echo "✅ .env uploaded."

# ── Remote setup + Docker deploy ──────────────────────────────────────────
echo ""
echo "🐳 Setting up Docker on EC2 and starting containers..."
ssh -i "$PEM_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" << 'REMOTE_SCRIPT'
  set -e
  cd /home/ec2-user/xeno-oracle

  # ── Install Docker if missing ────────────────────────────────────────
  if ! command -v docker &>/dev/null; then
    echo "  Installing Docker..."
    sudo dnf install -y docker
    sudo usermod -aG docker ec2-user
    sudo systemctl enable docker
    sudo systemctl start docker
    # Reload group membership for this session
    newgrp docker || true
  fi

  # ── Install docker compose plugin if missing ─────────────────────────
  if ! docker compose version &>/dev/null 2>&1; then
    echo "  Installing docker compose CLI plugin..."
    mkdir -p ~/.docker/cli-plugins/
    curl -SL https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
    chmod +x ~/.docker/cli-plugins/docker-compose
  fi

  # ── Install buildx plugin if missing ─────────────────────────────────
  if ! docker buildx version &>/dev/null 2>&1; then
    echo "  Installing docker-buildx CLI plugin..."
    mkdir -p ~/.docker/cli-plugins/
    curl -SL https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx
    chmod +x ~/.docker/cli-plugins/docker-buildx
  fi

  COMPOSE="docker compose"
  echo "  Using: $COMPOSE"

  echo ""
  echo "🔄 Stopping any existing containers..."
  $COMPOSE down --remove-orphans 2>/dev/null || true

  echo ""
  echo "🏗  Building Docker images (takes a few minutes on first run)..."
  $COMPOSE build --no-cache

  echo ""
  echo "🚀 Starting all services..."
  $COMPOSE up -d

  echo ""
  echo "⏳ Waiting 30 seconds for services to initialise..."
  sleep 30

  echo ""
  echo "🩺 Health checks:"
  curl -sf http://localhost:8000/health && echo "  ✅ Backend (8000): OK" || echo "  ❌ Backend (8000): FAIL"
  curl -sf http://localhost:8001/health && echo "  ✅ Channel (8001): OK" || echo "  ❌ Channel (8001): FAIL"
  curl -sf http://localhost:3000 && echo "  ✅ Frontend (3000): OK" || echo "  ❌ Frontend (3000): may need more time — check: docker compose logs frontend"

  echo ""
  echo "📋 Running containers:"
  $COMPOSE ps

  # ── Systemd service for auto-restart on EC2 reboot ───────────────────
  echo ""
  echo "⚙  Setting up systemd auto-restart on EC2 reboot..."
  sudo tee /etc/systemd/system/xeno-oracle.service > /dev/null << 'SYSTEMD'
[Unit]
Description=Xeno Oracle Docker Compose Stack
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ec2-user/xeno-oracle
ExecStart=/bin/bash -c 'docker compose up -d 2>/dev/null || docker-compose up -d'
ExecStop=/bin/bash -c 'docker compose down 2>/dev/null || docker-compose down'
TimeoutStartSec=300
User=ec2-user

[Install]
WantedBy=multi-user.target
SYSTEMD

  sudo systemctl daemon-reload
  sudo systemctl enable xeno-oracle.service
  echo "  ✅ Systemd service enabled — stack will restart after every EC2 reboot."

REMOTE_SCRIPT

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ DEPLOYMENT COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  🌐 Frontend (open this first):  http://$EC2_IP:3000"
echo "  🔌 Backend API:                  http://$EC2_IP:8000"
echo "  📖 Swagger Docs:                 http://$EC2_IP:8000/docs"
echo "  📡 Channel Service:              http://$EC2_IP:8001"
echo "  🩺 Health Check:                 http://$EC2_IP:8000/health"
echo "  ☁  AWS Status (admin only):      http://$EC2_IP:8000/api/v1/aws/status"
echo ""
echo "  🔑 Demo logins:"
echo "     [⚡ Admin]    admin@xeno.in    / admin123"
echo "     [🎯 Marketer] marketer@xeno.in / marketer123"
echo "     [👁 Viewer]   viewer@xeno.in   / viewer123"
echo ""
echo "  📝 Smoke test checklist:"
echo "     1. Open http://$EC2_IP:3000 → redirects to /login"
echo "     2. Click [⚡ Admin] pill → lands on Oracle Command"
echo "     3. Type campaign intent → verify 10 agent steps stream live"
echo "     4. Open campaign detail → Approve & Launch → verify 'completed'"
echo "     5. Click 'Export to S3' → presigned URL returned"
echo "     6. Sidebar → AWS Services → all 5 show green dots"
echo "     7. GET http://$EC2_IP:8000/api/v1/aws/status → connected:true for all"
echo ""
echo "  🔧 Useful commands (SSH in first):"
echo "     ssh -i $PEM_KEY $EC2_USER@$EC2_IP"
echo "     cd xeno-oracle && docker compose logs -f"
echo "     docker compose ps"
echo "════════════════════════════════════════════════════════════════"
