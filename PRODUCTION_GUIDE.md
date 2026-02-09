# Production Deployment Checklist & Optimization Guide

## ✅ Pre-Launch Checklist

### Environment Setup
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Generate strong database password
- [ ] Generate strong Redis password (optional)
- [ ] Configure `NEW_RELIC_LICENSE_KEY`
- [ ] Update `CORS_ORIGINS` with production domain

### Database
- [ ] Create PostgreSQL superuser with strong password
- [ ] Enable SSL connections to database
- [ ] Configure PostgreSQL `max_connections` = 100 + buffer
- [ ] Enable PostgreSQL logging for slow queries
- [ ] Set `shared_buffers` = 25% of RAM
- [ ] Set `effective_cache_size` = 50% of RAM
- [ ] Run `ANALYZE` on all tables
- [ ] Verify backup strategy

### Redis
- [ ] Set `maxmemory = 4GB` (adjust for your system)
- [ ] Set `maxmemory-policy = allkeys-lru`
- [ ] Enable persistence (`appendonly yes`)
- [ ] Configure regular backups

### Backend
- [ ] Set `API_WORKERS = CPU_COUNT * 2`
- [ ] Configure `DB_POOL_SIZE = 20`
- [ ] Enable CORS for your domain only
- [ ] Review and enable rate limiting
- [ ] Configure logging to syslog/ELK

### Frontend
- [ ] Build for production: `npm run build`
- [ ] Configure CDN (CloudFlare, AWS CloudFront)
- [ ] Enable GZIP compression in Nginx
- [ ] Set cache headers for static assets
- [ ] Configure SSL/TLS certificate

### Monitoring
- [ ] Configure New Relic alerts
- [ ] Set up APM monitoring
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring (Pingdom, Uptime.com)
- [ ] Configure error tracking (Sentry)

### Security
- [ ] Enable HTTPS/TLS
- [ ] Configure CSRF protection
- [ ] Set security headers (HSTS, X-Frame-Options, etc.)
- [ ] Enable rate limiting per IP
- [ ] Configure WAF rules

---

## 🚀 Performance Tuning

### PostgreSQL Optimization

```sql
-- For production systems with 16GB RAM and 8 CPU cores

-- Connection pooling
ALTER SYSTEM SET max_connections = 400;
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '8GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '10MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Apply changes
SELECT pg_reload_conf();

-- Verify settings
SELECT name, setting FROM pg_settings 
WHERE name LIKE 'max_connections' OR name LIKE 'shared_buffers';
```

### Index Maintenance

```sql
-- Monitor index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan as index_scans,
  idx_tup_read as tuples_read,
  idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Remove unused indexes
SELECT 
  schemaname,
  tablename,
  indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0;

-- Rebuild fragmented indexes
REINDEX INDEX CONCURRENTLY idx_leaderboard_score_rank;

-- Analyze tables
ANALYZE;

-- Vacuum tables (removes dead rows)
VACUUM (ANALYZE, VERBOSE) leaderboard;
```

### Connection Pool Optimization

```python
# In backend/app/core/database.py

# For 100+ concurrent users:
DB_POOL_SIZE = 30
MAX_OVERFLOW = 20
DB_POOL_RECYCLE = 3600

# Monitor pool usage:
# pool.size() = number of total connections
# pool.checkedout() = active connections
# Aim for: checkedout < size/2
```

### Redis Optimization

```bash
# Set maximum memory usage
CONFIG SET maxmemory 4gb
CONFIG SET maxmemory-policy allkeys-lru

# Monitor memory
INFO memory

# Check eviction stats
INFO stats

# Optimize for your use case
CONFIG SET hash-max-ziplist-entries 512
CONFIG SET hash-max-ziplist-value 64
CONFIG REWRITE
```

---

## 📊 Scaling Strategies

### Horizontal Scaling (Multiple Backend Instances)

```yaml
# Use with load balancer
services:
  backend-1:
    image: gaming-leaderboard:latest
    environment:
      NODE_ID: 1
  
  backend-2:
    image: gaming-leaderboard:latest
    environment:
      NODE_ID: 2
  
  backend-3:
    image: gaming-leaderboard:latest
    environment:
      NODE_ID: 3
  
  # All backends share: PostgreSQL, Redis
```

### Database Replication

```bash
# Primary: Handles writes
# Replica-1: Handles reads (leaderboard queries)
# Replica-2: Handles reads (historical queries)

# Connection string for backend
DATABASE_URL=postgresql://user:pass@primary:5432/leaderboard_db

# Connection string for read-only queries
READ_REPLICA_URL=postgresql://user:pass@replica-1:5432/leaderboard_db
```

### Redis Cluster

```bash
# For 10K+ concurrent connections
# Set up 3 Redis cluster nodes with replication

docker run -p 6379:6379 redis:7 redis-server --cluster-enabled yes
docker run -p 6380:6379 redis:7 redis-server --cluster-enabled yes
docker run -p 6381:6379 redis:7 redis-server --cluster-enabled yes

# Connect to cluster
redis-cli --cluster create 127.0.0.1:6379 127.0.0.1:6380 127.0.0.1:6381
```

---

## 🔍 Monitoring & Observability

### Key Metrics to Track

```
Application Performance:
├── Request Rate (req/s)
├── P50/P95/P99 Latency (ms)
├── Error Rate (%)
├── CPU Usage (%)
└── Memory Usage (GB)

Database Performance:
├── Query Execution Time (ms)
├── Slow Query Count
├── Index Hit Ratio (%)
├── Connection Pool Usage (%)
└── Cache Hit Ratio (%)

Business Metrics:
├── Active Users (concurrent)
├── Scores Submitted/min
├── Leaderboard Updates/sec
└── Rank Changes/min
```

### New Relic Queries

```sql
-- Average response time
SELECT average(duration) FROM Transaction WHERE appId='YOUR_APP_ID'

-- Slowest endpoints
SELECT average(duration) FROM Transaction 
WHERE appId='YOUR_APP_ID' 
GROUP BY name 
ORDER BY average(duration) DESC

-- Error rate
SELECT percentage(count(*), WHERE error = true) FROM Transaction 
WHERE appId='YOUR_APP_ID'

-- Database performance
SELECT average(databaseDuration) FROM Transaction 
WHERE appId='YOUR_APP_ID'
```

### Alerting Thresholds

```
Set up alerts for:
├── Response time > 1000ms (critical)
├── Error rate > 5% (warning), > 10% (critical)
├── CPU usage > 80% (warning), > 95% (critical)
├── Memory usage > 90% (warning), > 95% (critical)
├── Database connections > 80% of max (warning)
└── Cache hit rate < 70% (warning)
```

---

## 🛡 Security Hardening

### Network Security

```bash
# Firewall rules
# Allow:
# - 443 (HTTPS) from anywhere
# - 80 (HTTP redirect) from anywhere
# - 5432 (PostgreSQL) only from backend servers
# - 6379 (Redis) only from backend servers

# SSH access
# - Key-based authentication only
# - No password authentication
# - Port 22 access from limited IPs
```

### Database Security

```sql
-- Create application user (not superuser)
CREATE USER leaderboard_app WITH PASSWORD 'secure_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE leaderboard_db TO leaderboard_app;
GRANT USAGE ON SCHEMA public TO leaderboard_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO leaderboard_app;

-- Revoke dangerous permissions
REVOKE SUPERUSER ON leaderboard_app;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
```

### API Security

```python
# In backend/app/core/config.py

# Rate limiting
RATE_LIMIT = RateLimitConfig(
    submissions_per_minute=60,
    rank_lookups_per_minute=300,
    leaderboard_queries_per_minute=600,
)

# CORS
CORS_ORIGINS = ["https://your-domain.com"]
CORS_ALLOW_CREDENTIALS = True

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}
```

---

## 📈 Capacity Planning

### Resource Estimation for Different User Counts

**50K Active Users:**
- CPU: 4 cores
- RAM: 8GB (backend: 2GB, PostgreSQL: 4GB, Redis: 1GB)
- Storage: 50GB
- Network: 100Mbps

**500K Active Users:**
- CPU: 16 cores (4 servers × 4 cores)
- RAM: 64GB (backend: 8GB × 4, PostgreSQL: 32GB, Redis: 4GB)
- Storage: 500GB
- Network: 1Gbps

**5M Active Users:**
- CPU: 64 cores (16 servers × 4 cores)
- RAM: 512GB (distributed across cluster)
- Storage: 2TB (with replication)
- Network: 10Gbps
- Database: Primary + 2-3 replicas

---

## 🔄 Disaster Recovery

### Backup Strategy

```bash
# Daily automated backups
# 1. PostgreSQL: Full backup
pg_dump -h localhost -U user leaderboard_db | gzip > backup_$(date +%Y%m%d).sql.gz

# 2. Redis: RDB snapshot
redis-cli --rdb /backups/redis_$(date +%Y%m%d).rdb

# 3. Store in S3 with 30-day retention
aws s3 cp backup_$(date +%Y%m%d).sql.gz s3://my-backups/

# 4. Test restoration monthly
pg_restore -d test_leaderboard backup_latest.sql
```

### Recovery Procedures

**Database Corruption:**
```bash
# 1. Stop backend services
docker-compose stop backend

# 2. Restore from backup
pg_restore -d leaderboard_db backup_latest.sql

# 3. Verify data integrity
psql -d leaderboard_db -c "SELECT COUNT(*) FROM leaderboard;"

# 4. Start services
docker-compose start backend
```

**Complete Server Failure:**
```bash
# 1. Spin up new server
# 2. Install Docker and Docker Compose
# 3. Clone application code
# 4. Restore database backup
# 5. Restore Redis data
# 6. Start services
docker-compose up -d
```

---

## 🎓 Load Testing

### Simulating Production Load

```bash
# Using Apache Bench
ab -n 100000 -c 1000 http://localhost/api/leaderboard/top

# Using wrk
wrk -t12 -c400 -d30s \
  -s submit_score.lua \
  http://localhost:8000/api/leaderboard/submit

# Using locust (Python)
locust -f locustfile.py --host=http://localhost:8000 -u 10000 -r 500
```

### Expected Results (at Scale)

```
Configuration: 8 CPU, 16GB RAM, SSD storage

Load: 10,000 concurrent users

Results:
├── Request/sec: 15,000-20,000
├── Average Response Time: 15-30ms
├── P99 Response Time: 100-200ms
├── Error Rate: <0.1%
├── Database Connections Used: ~25/30
├── Redis Evictions: <1/sec
└── CPU Usage: 60-70%
```

---

## 🚨 Incident Response

### High Latency
```
1. Check CPU and memory usage
2. Run EXPLAIN ANALYZE on slow queries
3. Check index fragmentation
4. Check Redis memory usage
5. Monitor network latency
6. Scale horizontally if needed
```

### High Error Rate
```
1. Check application logs
2. Check database connectivity
3. Check Redis connectivity
4. Run health checks
5. Check recent deployments
6. Rollback if necessary
```

### Database Connection Pool Exhaustion
```
1. Increase DB_POOL_SIZE
2. Optimize query performance
3. Close idle connections
4. Add connection pooling middleware (PgBouncer)
5. Scale horizontally
```

---

## 📚 References

- **PostgreSQL Performance**: https://wiki.postgresql.org/wiki/Performance_Optimization
- **Redis Optimization**: https://redis.io/topics/optimization
- **New Relic Docs**: https://docs.newrelic.com/
- **FastAPI Performance**: https://fastapi.tiangolo.com/deployment/
- **React Performance**: https://react.dev/reference/react/useMemo

---

**Ready for Production! 🚀**
