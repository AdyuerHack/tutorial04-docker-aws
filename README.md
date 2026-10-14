# Tutorial 04: Dockerización y Despliegue en AWS
**Arquitectura de Software - Universidad EAFIT 2026**  
**Estudiante:** Adyuer Ojeda  
**Profesor:** Nicolás Ramírez Vélez  

---

## 📌 Objetivo del Laboratorio
Empaquetar la arquitectura de la aplicación **Tienda API** (creada en el Tutorial 03 con Django REST Framework y Service Layer) en contenedores **Docker** y desplegarla en una instancia real de **AWS EC2** utilizando **AWS Academy Learner Lab**.

---

## 🏗️ Arquitectura de la Solución
* **Servicio Web (`web`)**: Contenedor Docker basado en `python:3.11-slim` ejecutando la API de Django en el puerto `8000`.
* **Servicio Base de Datos (`db`)**: Contenedor Docker oficial de `postgres:15` con volumen persistente `postgres_data`.
* **Orquestación**: Docker Compose (`docker-compose.yml`) conectando la aplicación con la base de datos a través de una red interna y variables de entorno (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).

---

## 🚀 Guía Rápida de Ejecución

### 1. Ejecución Local (Opcional - Pruebas en tu PC)
1. Abre **Docker Desktop** en tu computadora.
2. Abre una terminal en esta carpeta y ejecuta:
   ```bash
   docker compose up --build
   ```
3. En otra terminal, aplica las migraciones:
   ```bash
   docker compose exec web python manage.py migrate
   ```
4. Abre en tu navegador:
   * **Endpoint Requerido:** `http://localhost:8000/api/v1/comprar/`
   * **Catálogo de Libros:** `http://localhost:8000/api/v1/libros/`

---

### 2. Subir el Proyecto a tu GitHub
Ejecuta en tu terminal local:
```bash
git add .
git commit -m "feat: dockerizacion y configuracion de despliegue AWS Tutorial 04"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

---

### 3. Despliegue en AWS Academy (EC2)

#### Paso A: Crear la instancia EC2
1. Ingresa a **AWS Academy** -> **Learner Lab** y haz clic en **Start Lab**.
2. Cuando el punto esté en verde, haz clic en **AWS**.
3. Ve a **EC2** -> **Launch Instance**:
   * **Name:** `Servidor-Django`
   * **AMI:** `Amazon Linux 2023 AMI` (Free tier eligible)
   * **Instance Type:** `t2.micro`
   * **Key pair:** Selecciona `vockey` (o `Proceed without a key pair`)
   * **Network Settings:** Marca `Allow SSH`, `Allow HTTP` y `Allow HTTPS`.
4. Haz clic en **Launch Instance**.

#### Paso B: Conectarse y Desplegar
1. En el listado de instancias de EC2, selecciona `Servidor-Django` y haz clic en **Connect** -> pestaña **EC2 Instance Connect** -> **Connect**.
2. En la terminal que se abre en el navegador, clona tu repositorio y ejecuta el script automático:
   ```bash
   git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   cd TU_REPOSITORIO
   bash deploy_aws.sh
   ```
   *(El script `deploy_aws.sh` actualiza el sistema, instala Docker, inicia los contenedores con Docker Compose y ejecuta las migraciones automáticamente).*

#### Paso C: Exponer el Puerto 8000 en el Security Group de AWS
1. En la consola de AWS -> **EC2** -> **Instances**.
2. Selecciona tu instancia `Servidor-Django` y ve a la pestaña **Security**.
3. Haz clic en el nombre del **Security Group** (ej. `launch-wizard-1`).
4. Haz clic en **Edit inbound rules** -> **Add rule**:
   * **Type:** `Custom TCP`
   * **Port range:** `8000`
   * **Source:** `Anywhere-IPv4` (`0.0.0.0/0`)
5. Haz clic en **Save rules**.

---

## 📸 Validación y Entrega de Resultados
1. Copia la **Dirección IPv4 pública** de tu instancia EC2.
2. Abre en tu navegador:
   ```text
   http://<IP-PUBLICA-EC2>:8000/api/v1/comprar/
   ```
3. Toma la captura de pantalla donde se evidencie:
   * La barra de direcciones con la IP pública de AWS y el puerto `:8000`.
   * La respuesta JSON del API con código `200 OK`.
