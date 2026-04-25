# Compliance Patterns Reference

Framework-specific patterns for matching spec requirements to codebase implementations.

---

## Requirement Type → Code Pattern Mapping

### Authentication & Authorization

| Requirement Keywords | File Patterns | Code Patterns |
|---------------------|---------------|---------------|
| `auth`, `login`, `authentication` | `*auth*`, `*login*`, `*session*` | `@login_required`, `authenticate()`, `passport.use()`, `Depends(get_current_user)` |
| `jwt`, `token` | `*jwt*`, `*token*` | `jwt.encode`, `jwt.decode`, `sign()`, `verify()`, `createToken` |
| `oauth`, `sso` | `*oauth*`, `*sso*` | `OAuth2PasswordBearer`, `passport.authenticate('oauth2')` |
| `rbac`, `roles`, `permissions` | `*role*`, `*permission*`, `*rbac*` | `has_permission`, `@require_role`, `can()`, `authorize()` |
| `registration`, `signup` | `*register*`, `*signup*` | `create_user`, `register()`, `signUp()` |

### CRUD Operations

| Requirement Keywords | File Patterns | Code Patterns |
|---------------------|---------------|---------------|
| `create`, `add`, `new` | `*controller*`, `*view*`, `*handler*` | `POST /`, `create()`, `insert()`, `save()`, `.create()` |
| `read`, `view`, `list`, `get` | `*controller*`, `*view*`, `*handler*` | `GET /`, `find()`, `get()`, `list()`, `all()`, `.findAll()` |
| `update`, `edit`, `modify` | `*controller*`, `*view*`, `*handler*` | `PUT /`, `PATCH /`, `update()`, `save()`, `.update()` |
| `delete`, `remove` | `*controller*`, `*view*`, `*handler*` | `DELETE /`, `destroy()`, `remove()`, `.delete()` |

### Database & Storage

| Requirement Keywords | File Patterns | Code Patterns |
|---------------------|---------------|---------------|
| `database`, `db`, `persistence` | `*model*`, `*schema*`, `*migration*` | `class.*Model`, `CREATE TABLE`, `Schema(`, `Base.metadata` |
| `migration` | `*migration*`, `alembic/`, `migrations/` | `upgrade()`, `downgrade()`, `migrate` |
| `cache`, `caching` | `*cache*`, `*redis*` | `cache.get`, `cache.set`, `@cached`, `Redis()` |
| `search`, `query` | `*search*`, `*query*`, `*filter*` | `search()`, `filter()`, `where()`, `$text`, `LIKE` |

### API & Endpoints

| Requirement Keywords | File Patterns | Code Patterns |
|---------------------|---------------|---------------|
| `api`, `endpoint`, `rest` | `*route*`, `*api*`, `*endpoint*` | `@app.route`, `router.get`, `@api_view`, `app.use()` |
| `pagination` | `*paginate*`, `*pagination*` | `paginate()`, `limit`, `offset`, `page`, `per_page` |
| `validation`, `input validation` | `*validator*`, `*schema*` | `validate()`, `@validates`, `Joi.object()`, `Pydantic` |
| `rate limit`, `throttle` | `*rate*`, `*throttle*`, `*limit*` | `@rate_limit`, `throttle()`, `RateLimit`, `express-rate-limit` |

### Docker & Infrastructure

| Requirement Keywords | File Patterns | Code Patterns |
|---------------------|---------------|---------------|
| `docker`, `container` | `Dockerfile*`, `docker-compose*`, `compose*` | `FROM`, `EXPOSE`, `services:`, `build:` |
| `healthcheck`, `health` | `*health*`, `docker-compose*` | `healthcheck:`, `/health`, `ready()` |
| `environment`, `env`, `config` | `.env*`, `*config*`, `*settings*` | `os.environ`, `process.env`, `config.get()` |
| `ci/cd`, `pipeline`, `deploy` | `.github/workflows/*`, `.gitlab-ci*`, `Jenkinsfile` | `on: push`, `stages:`, `deploy:` |

---

## Framework-Specific Route Discovery

### Python (Django)
```
# URL patterns
grep -rn "path\|re_path\|url(" --include="*.py" "$ROOT/*/urls.py" 2>/dev/null
# Views
grep -rn "class.*View\|def.*view\|@api_view" --include="*.py" "$ROOT" 2>/dev/null
# Models
grep -rn "class.*models\.Model\|class.*Model.*Base" --include="*.py" "$ROOT" 2>/dev/null
```

### Python (FastAPI)
```
# Routes
grep -rn "@app\.\(get\|post\|put\|patch\|delete\)\|@router\." --include="*.py" "$ROOT" 2>/dev/null
# Models (Pydantic)
grep -rn "class.*BaseModel\|class.*SQLModel" --include="*.py" "$ROOT" 2>/dev/null
# Dependencies
grep -rn "Depends(" --include="*.py" "$ROOT" 2>/dev/null
```

### Python (Flask)
```
# Routes
grep -rn "@app\.route\|@bp\.route\|@blueprint\.route" --include="*.py" "$ROOT" 2>/dev/null
# Models (SQLAlchemy)
grep -rn "class.*db\.Model" --include="*.py" "$ROOT" 2>/dev/null
```

### Node.js (Express)
```
# Routes
grep -rn "router\.\(get\|post\|put\|patch\|delete\)\|app\.\(get\|post\|put\)" --include="*.js" --include="*.ts" "$ROOT" 2>/dev/null
# Models (Sequelize/Mongoose)
grep -rn "sequelize\.define\|mongoose\.model\|Schema(" --include="*.js" --include="*.ts" "$ROOT" 2>/dev/null
# Middleware
grep -rn "app\.use\|router\.use" --include="*.js" --include="*.ts" "$ROOT" 2>/dev/null
```

### Node.js (Next.js)
```
# API routes (file-based)
find "$ROOT/app/api" -name "route.ts" -o -name "route.js" 2>/dev/null
find "$ROOT/pages/api" -name "*.ts" -o -name "*.js" 2>/dev/null
# Pages
find "$ROOT/app" -name "page.tsx" -o -name "page.jsx" 2>/dev/null
```

---

## Docker Service Patterns

### Common Services

| Service | Default Port | Health Check |
|---------|-------------|-------------|
| PostgreSQL | 5432 | `pg_isready -U postgres` |
| MySQL | 3306 | `mysqladmin ping` |
| MongoDB | 27017 | `mongosh --eval "db.runCommand('ping')"` |
| Redis | 6379 | `redis-cli ping` |
| Nginx | 80, 443 | `curl -f http://localhost/` |
| Node.js app | 3000 | `curl -f http://localhost:3000/health` |
| Python app | 5000, 8000 | `curl -f http://localhost:8000/health` |
| RabbitMQ | 5672, 15672 | `rabbitmq-diagnostics check_running` |
| Elasticsearch | 9200 | `curl -f http://localhost:9200/_cluster/health` |
| MinIO | 9000 | `curl -f http://localhost:9000/minio/health/live` |

### Compose File Indicators

| Feature | Compose Pattern |
|---------|----------------|
| Persistent storage | `volumes:` section with named volumes |
| Networking | `networks:` section or `expose:` ports |
| Dependencies | `depends_on:` with `condition: service_healthy` |
| Environment config | `environment:` or `env_file:` |
| Build from source | `build:` context instead of `image:` |
| Resource limits | `deploy.resources.limits` |

---

## Evidence Quality Tiers

| Tier | Evidence Type | Confidence |
|------|-------------|------------|
| **Strong** | Implementation file + test file + route/endpoint defined | HIGH → PASS |
| **Moderate** | Implementation file exists, no tests | MEDIUM → PARTIAL |
| **Weak** | Only keyword matches in comments or docs | LOW → PARTIAL |
| **None** | Zero matches across all search strategies | — → MISSING |
| **Broken** | Files exist but contain TODO/placeholder/broken imports | — → FAIL |

## Placeholder Detection

Code that matches keywords but contains these patterns should be flagged as PARTIAL or FAIL, not PASS:

```
TODO, FIXME, HACK, PLACEHOLDER, NotImplementedError, pass  # (empty function body)
raise NotImplementedError, throw new Error("Not implemented")
return None  # placeholder, return {}  # stub
// TODO: implement, # FIXME: complete this
```
