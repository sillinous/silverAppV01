# 🚀 Production Deployment Guide - Arbitrage OS

This guide walks you through deploying Arbitrage OS to production with enterprise-grade quality standards.

## 📋 Prerequisites

Before deploying to production, ensure you have:

1. **Server Requirements**
   - Ubuntu 20.04+ or similar Linux distribution
   - Docker and Docker Compose installed
   - Minimum 2GB RAM, 2 CPU cores
   - 20GB available disk space

2. **Domain & DNS**
   - Registered domain name
   - DNS A record pointing to your server's IP address

3. **Required API Keys** (see `.env.example`)
   - OpenAI API key
   - Mapbox API key
   - Ximilar API token, workspace ID, and task ID

4. **GitHub Configuration**
   - GitHub repository secrets configured (see GitHub Actions section)

---

## 🔐 Step 1: Configure GitHub Secrets

In your GitHub repository, navigate to **Settings > Secrets and variables > Actions** and add the following secrets:

### Server Access
- `PROD_SERVER_HOST`: Your production server IP or hostname
- `PROD_SERVER_USERNAME`: SSH username for deployment
- `PROD_SERVER_SSH_KEY`: Private SSH key for server access

### Application Secrets
- `SECRET_KEY`: Strong random secret for JWT tokens (generate with `openssl rand -hex 32`)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed frontend origins (e.g., `https://yourdomain.com,https://www.yourdomain.com`)

### Database Credentials
- `POSTGRES_USER`: Database username (e.g., `arbitrage_user`)
- `POSTGRES_PASSWORD`: Strong database password
- `POSTGRES_DB`: Database name (e.g., `arbitrage_db`)

### External API Keys
- `OPENAI_API_KEY`: Your OpenAI API key
- `MAPBOX_API_KEY`: Your Mapbox API key
- `XIMILAR_API_TOKEN`: Your Ximilar API token
- `XIMILAR_WORKSPACE_ID`: Your Ximilar workspace ID
- `XIMILAR_TASK_ID`: Your Ximilar recognition task ID

---

## 🖥️ Step 2: Prepare Your Production Server

### 2.1 Install Docker

```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (optional, for non-root usage)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2.2 Configure Firewall

```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2.3 Set Up SSH Key Access

On your local machine, generate an SSH key if you don't have one:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Add the public key to your server's `~/.ssh/authorized_keys`.

Store the **private key** in GitHub Secrets as `PROD_SERVER_SSH_KEY`.

---

## 🔒 Step 3: Configure SSL/HTTPS (Recommended)

### Option A: Let's Encrypt (Recommended)

After your first deployment, SSH into your server and run:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain and install SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot will automatically configure nginx for HTTPS
```

### Option B: Manual SSL Configuration

If you have your own SSL certificates:

1. Copy your certificate files to the server
2. Uncomment the SSL section in `frontend/nginx.conf`
3. Update the certificate paths to match your files

---

## 🚢 Step 4: Deploy via GitHub Actions

The CD workflow is already configured. Deployment happens automatically when you push to the `main` branch.

### How It Works

1. **Build**: Docker images for backend and frontend are built
2. **Push**: Images are pushed to GitHub Container Registry (GHCR)
3. **Deploy**: SSH into your server, pull images, run migrations, restart services

### Manual Deployment Trigger

You can also manually trigger deployment from the GitHub Actions tab.

---

## 🗄️ Step 5: Database Setup

The deployment workflow automatically runs database migrations. For manual setup:

```bash
# SSH into your server
cd /opt/silverAppV01

# Run migrations
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# Create your first admin user (via Django admin or custom script)
# You'll need to register via the /register endpoint first
```

---

## 👤 Step 6: Create Your First User

After deployment, navigate to your domain:

1. Visit `https://yourdomain.com/register`
2. Create an admin account
3. Login at `https://yourdomain.com/login`

---

## 📊 Step 7: Monitoring & Maintenance

### View Logs

```bash
# SSH into your server
cd /opt/silverAppV01

# View all service logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f worker
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Restart Services

```bash
docker-compose -f docker-compose.prod.yml restart
```

### Update Application

Simply push your changes to the `main` branch on GitHub. The CD workflow will handle the rest.

### Backup Database

A backup script is included at `scripts/backup_db.sh`. Set up a cron job:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/silverAppV01/scripts/backup_db.sh
```

---

## 🔍 Step 8: Health Checks

### Verify Services Are Running

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Health check endpoint
curl https://yourdomain.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-30T00:00:00.000000",
  "service": "arbitrage-os"
}
```

### Verify Authentication

```bash
# Test registration
curl -X POST https://yourdomain.com/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
  }'

# Test login
curl -X POST https://yourdomain.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=securepassword123"
```

---

## 🛡️ Security Checklist

Before going live, verify:

- [ ] All GitHub Secrets are configured
- [ ] SSL/HTTPS is enabled
- [ ] Firewall is configured (only ports 22, 80, 443 open)
- [ ] Database password is strong and unique
- [ ] SECRET_KEY is a strong random value
- [ ] ALLOWED_ORIGINS is set to your production domain(s)
- [ ] `/metrics` endpoint requires authentication
- [ ] Rate limiting is enabled (100 requests/minute default)
- [ ] Database backups are automated
- [ ] All API keys are kept secret (never in version control)

---

## 🔧 Troubleshooting

### Deployment Failed

Check GitHub Actions logs for errors. Common issues:

1. **SSH connection failed**: Verify `PROD_SERVER_HOST` and `PROD_SERVER_SSH_KEY`
2. **Docker pull failed**: Ensure GitHub token has package read permissions
3. **Migration failed**: Check database credentials and connectivity

### Application Not Accessible

1. Check service logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify DNS is configured correctly
3. Ensure firewall allows HTTP/HTTPS traffic
4. Check nginx configuration

### Authentication Issues

1. Verify SECRET_KEY is set in environment variables
2. Check that CORS is configured correctly (ALLOWED_ORIGINS)
3. Ensure frontend is using correct API_URL

### Database Connection Errors

1. Verify PostgreSQL container is running
2. Check DATABASE_URL format: `postgresql://user:password@db:5432/dbname`
3. Ensure database migrations have run

---

## 📈 Performance Optimization

### Redis Caching

Redis is already configured for Celery. To add application-level caching, update your code to use the redis connection.

### Database Indexing

Indexes are already created on frequently queried fields (usernames, URLs). Monitor slow queries and add indexes as needed.

### Load Balancing

For high traffic, consider:
- Running multiple backend instances behind a load balancer
- Using a managed PostgreSQL service (AWS RDS, Google Cloud SQL)
- Implementing CDN for static frontend assets

---

## 🆘 Getting Help

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review application logs
3. Consult FastAPI and React documentation
4. Open an issue on GitHub with:
   - Detailed error description
   - Relevant log excerpts
   - Steps to reproduce

---

## 📝 Post-Deployment Notes

### Environment Variables

The application uses environment-based configuration. Key variables:

- **Backend**: Reads from environment (see `.env.example`)
- **Frontend**: Uses `REACT_APP_API_URL` for API endpoint

Update these as needed for your production environment.

### API Documentation

FastAPI provides automatic API documentation:
- Interactive docs: `https://yourdomain.com/docs`
- ReDoc: `https://yourdomain.com/redoc`

### Metrics

Prometheus metrics are available at `https://yourdomain.com/metrics` (requires authentication).

---

## 🎉 You're Live!

Congratulations! Your Arbitrage OS instance is now running in production.

**Next Steps:**
1. Monitor logs for any errors
2. Test all features end-to-end
3. Set up monitoring alerts (optional)
4. Configure backup retention policy
5. Plan for regular updates and maintenance

**Remember:**
- Keep your API keys secure
- Regularly update dependencies
- Monitor resource usage
- Back up your database regularly

Happy arbitraging! 🚀
