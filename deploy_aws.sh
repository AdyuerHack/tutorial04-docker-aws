#!/bin/bash
# Script de despliegue automatizado para Tutorial 04 en AWS EC2 (Amazon Linux 2023)
set -e

echo "=========================================================="
echo "   Iniciando Despliegue de Tienda API (Tutorial 04)"
echo "=========================================================="

echo ">>> 1. Actualizando paquetes del sistema..."
sudo dnf update -y

echo ">>> 2. Instalando Docker y Git..."
sudo dnf install git docker -y

echo ">>> 3. Habilitando e iniciando Docker..."
sudo systemctl enable --now docker
sudo usermod -a -G docker $USER

echo ">>> 4. Verificando Docker Compose y Buildx..."
if ! docker buildx version >/dev/null 2>&1; then
    echo "Instalando Docker Buildx..."
    sudo mkdir -p /usr/local/lib/docker/cli-plugins /usr/libexec/docker/cli-plugins ~/.docker/cli-plugins
    BUILDX_URL="https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64"
    sudo curl -sSL "$BUILDX_URL" -o /usr/local/lib/docker/cli-plugins/docker-buildx
    sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx
    sudo cp /usr/local/lib/docker/cli-plugins/docker-buildx /usr/libexec/docker/cli-plugins/docker-buildx
    cp /usr/local/lib/docker/cli-plugins/docker-buildx ~/.docker/cli-plugins/docker-buildx 2>/dev/null || true
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "Instalando Docker Compose standalone..."
    sudo curl -sSL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    DOCKER_COMPOSE_CMD="docker-compose"
else
    DOCKER_COMPOSE_CMD="docker compose"
fi

echo ">>> 5. Construyendo y levantando contenedores con Docker Compose..."
sudo $DOCKER_COMPOSE_CMD up -d --build

echo ">>> 6. Esperando 6 segundos a que PostgreSQL este listo..."
sleep 6

echo ">>> 7. Ejecutando migraciones de Django..."
sudo $DOCKER_COMPOSE_CMD exec -T web python manage.py migrate --noinput

echo ">>> 8. Verificando contenedores activos..."
sudo docker ps

echo "=========================================================="
echo "    ¡Despliegue finalizado con éxito en AWS EC2!         "
echo "=========================================================="
echo "Pasos siguientes:"
echo "1. En la consola de AWS EC2 -> Security Groups:"
echo "   Abre la regla de entrada (Inbound Rule):"
echo "   - Tipo: Custom TCP"
echo "   - Puerto: 8000"
echo "   - Origen: 0.0.0.0/0 (Anywhere IPv4)"
echo "2. Abre en tu navegador:"
echo "   http://<IP-PUBLICA-EC2>:8000/api/v1/comprar/"
echo "=========================================================="
