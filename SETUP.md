# Setup & Running Instructions

## ⚡ Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose installed
- Git
- ~500MB disk space

### 1. Clone & Navigate
```bash
cd /Users/sahilsingh/Desktop/GoComet
```

### 2. Configure Environment
```bash
# Copy example env
cp backend/.env.example backend/.env

# Optional: Edit environment variables
# vi backend/.env
```

### 3. Start All Services
```bash
# Production deployment
docker-compose up -d

# Wait for services to initialize (30-60 seconds)
docker-compose ps

# Check logs
docker-compose logs -f backend
```

### 4. Verify Setup
```bash
# Test Backend
curl http://localhost:8000/health
# Expected: {"status":"healthy","environment":"development"}

# Test Frontend
open http://localhost:80
# Or: http://localhost:3000
```

### 5. Create Sample Data
```bash
# Connect to backend container
docker-compose exec backend python

# Run in Python:
from app.core import db_manager
from app.models import User, Leaderboard
from sqlalchemy.orm import Session

db_manager.init_sync_engine()
db = db_manager.get_sync_session()

# Create users
users = [
    User(username=f"player_{i}", email=f"p{i}@game.com", is_active=1)
    for i in range(1, 51)
]
db.add_all(users)
db.commit()

# Create leaderboard entries
entries = [
    Leaderboard(
        user_id=user.id,
        total_score=5000 - (i * 50),
        rank=i,
        games_played=10 + i,
        win_rate=0.8 - (i * 0.01)
    )
    for i, user in enumerate(users, 1)
]
db.add_all(entries)
db.commit()
print("✓ Sample data created!")
```

---

## 🎮 Using the Application

### Submit a Score
1. Open UI at `http://localhost:3000`
2. Fill in "Player ID" (1-50 for sample data)
3. Enter a score (any positive number)
4. Select game mode
5. Click "Submit Score"
6. See your rank update instantly

### View Leaderboard
- **All Rankings**: Top 100 displayed by default
- **Top 10**: Click "Top 10" filter
- **Top 50**: Click "Top 50" filter

### Check Your Rank
- Click any player card to view their full rank info
- See percentile tier and detailed stats

### Real-Time Updates
- Open leaderboard in multiple browser tabs
- Submit a score in one tab
- Watch other tabs update in real-time

---

## 🛠 Development Setup

### Backend Development
```bash
# Install dependencies
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
python migrations/init_db.py

# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest --cov=app tests/
```

### Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check
```

---

## 📋 Database Management

### Connect to PostgreSQL
```bash
# Via container
docker-compose exec postgres psql -U user -d leaderboard_db

# Via local psql
psql postgresql://user:password@localhost:5432/leaderboard_db
```

### Useful SQL Queries
```sql
-- Check leaderboard size
SELECT COUNT(*) as total_entries FROM leaderboard;

-- Get top 10
SELECT rank, user_id, total_score FROM leaderboard 
ORDER BY rank LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public';

-- Monitor connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'leaderboard_db';
```

### Backup & Restore
```bash
# Backup
docker-compose exec postgres pg_dump -U user leaderboard_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U user leaderboard_db < backup.sql
```

---

## 🔍 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Performance Monitoring
```bash
# Check PostgreSQL queries
docker-compose exec postgres psql -U user leaderboard_db
> SELECT query, mean_time FROM pg_stat_statements 
  ORDER BY mean_time DESC LIMIT 10;

# Check Redis memory
docker-compose exec redis redis-cli INFO memory

# Check Redis keys
docker-compose exec redis redis-cli KEYS "leaderboard:*"
```

---

## 🐳 Docker Commands

### Common Operations
```bash
# Start services
docker-compose up -d

# Stop services (keep data)
docker-compose stop

# Stop and remove (keep volumes)
docker-compose down

# Remove everything including data
docker-compose down -v

# View running services
docker-compose ps

# View container logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend python -c "import app; print('OK')"

# Rebuild images
docker-compose build --no-cache
```

### Development with Hot Reload
```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up -d

# Backend auto-reloads on code changes
# Frontend: npm run dev in separate terminal
```

---

## 🌐 Network Ports

```
Service     | Port | URL
------------|------|---------------------------
Frontend    | 80   | http://localhost
Frontend    | 3000 | http://localhost:3000
Backend     | 8000 | http://localhost:8000
PostgreSQL  | 5432 | postgres://localhost:5432
Redis       | 6379 | redis://localhost:6379
```

---

## 🧪 Testing

### Run Backend Tests
```bash
cd backend

# All tests
pytest tests/ -v

# Specific test
pytest tests/test_leaderboard.py::TestScoreSubmission -v

# With coverage
pytest --cov=app --cov-report=html tests/

# Open coverage report
open htmlcov/index.html
```

### API Testing
```bash
# Test health check
curl http://localhost:8000/health

# Submit score
curl -X POST http://localhost:8000/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "score": 1500,
    "game_mode": "classic"
  }'

# Get top leaderboard
curl "http://localhost:8000/api/leaderboard/top?limit=10"

# Get user rank
curl http://localhost:8000/api/leaderboard/rank/1

# Test WebSocket
websocat ws://localhost:8000/ws/leaderboard/1
```

---

## 🚀 Production Deployment

### Pre-deployment Checklist
```bash
# 1. Set production environment
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=INFO

# 2. Update .env with secure values
cp backend/.env.example backend/.env
# Edit: DATABASE_URL, REDIS_URL, NEW_RELIC_LICENSE_KEY

# 3. Build images
docker-compose build

# 4. Run migrations
docker-compose run backend python -m migrations.init_db

# 5. Start services
docker-compose up -d

# 6. Verify health
curl https://your-domain.com/health
```

### New Relic Setup
```bash
# 1. Get license key from New Relic
# 2. Set in environment
export NEW_RELIC_LICENSE_KEY=your_license_key
export NEW_RELIC_APP_NAME=gaming-leaderboard-prod

# 3. Restart backend
docker-compose restart backend

# 4. View in New Relic dashboard
# Navigate to: one.newrelic.com/nr1-core
```

### Performance Tuning for Production

#### PostgreSQL
```bash
# Connect to container
docker-compose exec postgres psql -U user -d leaderboard_db

# Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM leaderboard 
WHERE is_active = 1 
ORDER BY total_score DESC 
LIMIT 100;

# Vacuum and analyze
VACUUM ANALYZE;
```

#### Redis
```bash
# Monitor Redis
docker-compose exec redis redis-cli MONITOR

# Check memory usage
docker-compose exec redis redis-cli INFO memory

# Adjust maxmemory policy if needed
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Scaling Considerations

**For 100K+ concurrent users:**

1. **Database Replication**
   - Primary: writes (score submissions)
   - Replicas: reads (leaderboard queries)

2. **Load Balancer**
   - Nginx upstream backend servers
   - Sticky sessions for WebSocket

3. **Redis Cluster**
   - Multiple Redis nodes
   - Automatic failover

4. **CDN for Frontend**
   - Cloudflare or AWS CloudFront
   - Cache static assets

---

## 🔧 Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready: Wait 30 seconds
# 2. Port in use: docker-compose down && docker-compose up
# 3. Missing .env: cp backend/.env.example backend/.env
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U user -d leaderboard_db -c "SELECT 1"

# Reset database
docker-compose down -v
docker-compose up -d postgres
sleep 30
docker-compose exec backend python -m migrations.init_db
```

### WebSocket Not Connecting
```bash
# Check backend WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost:8000/ws/leaderboard/1

# Check proxy configuration in frontend/nginx.conf
# Ensure Upgrade and Connection headers are passed
```

### Cache Issues
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Clear all cache
docker-compose exec redis redis-cli FLUSHALL

# Monitor Redis operations
docker-compose exec redis redis-cli MONITOR
```

---

## 📊 Performance Optimization Tips

### Database
```sql
-- Run ANALYZE regularly
ANALYZE;

-- Check slow query log
SELECT query, mean_time FROM pg_stat_statements 
WHERE mean_time > 100 
ORDER BY mean_time DESC;

-- Create partial indexes for active players
CREATE INDEX idx_leaderboard_active_only 
ON leaderboard(rank) 
WHERE is_active = 1;
```

### Caching
```python
# Cache hit rate monitoring
cache_hits = await redis_client.get("cache:hits")
cache_misses = await redis_client.get("cache:misses")
hit_rate = cache_hits / (cache_hits + cache_misses) * 100
# Target: >80% hit rate
```

### Backend
```python
# Connection pool monitoring
pool = db_manager.engine.pool
print(f"Pool size: {pool.size()}")
print(f"Checked out: {pool.checkedout()}")

# Aim for: <50% utilization
```

---

## 📚 Additional Resources

- **Backend API Docs**: http://localhost:8000/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Redis Docs**: https://redis.io/documentation
- **FastAPI Guide**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

---

## 🎓 Learning Points

This system demonstrates:

1. ✅ **Database Optimization**
   - Strategic indexing
   - Query optimization
   - Denormalization for performance

2. ✅ **Real-Time Systems**
   - WebSocket implementation
   - Message broadcasting
   - State synchronization

3. ✅ **Caching Strategies**
   - TTL-based invalidation
   - Pattern-based clearing
   - Cache-aside pattern

4. ✅ **Concurrency Control**
   - Row-level locking
   - Transaction isolation
   - Race condition prevention

5. ✅ **Modern UI**
   - Component-based architecture
   - State management
   - Animation & interactivity

---

**Happy Leaderboarding! 🎮🏆**
