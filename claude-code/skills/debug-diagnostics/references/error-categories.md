# Error Categories Reference

Decision tree and pattern catalog for error classification in the debug-diagnostics skill.

---

## Decision Tree

```
Is the error from Docker (container exit, build fail, compose error)?
  YES → docker
  NO  ↓

Is the error a syntax/parse error (code won't compile/interpret)?
  YES → syntax
  NO  ↓

Is the error about a missing module/package/dependency?
  YES → dependency
  NO  ↓

Is the error about file/directory permissions or access denied?
  YES → permission
  NO  ↓

Is the error about a database (connection, query, migration)?
  YES → database
  NO  ↓

Is the error about network connectivity (connection refused, timeout, DNS)?
  Is the target a known database port (5432, 3306, 27017, 6379)?
    YES → database (not network)
    NO  → network
  NO  ↓

Is the error about configuration (env vars, config files, settings)?
  YES → configuration
  NO  ↓

Default → runtime
```

---

## Category Patterns by Language

### Python

| Category | Error Patterns |
|----------|---------------|
| `syntax` | `SyntaxError`, `IndentationError`, `TabError`, `invalid syntax` |
| `runtime` | `TypeError`, `ValueError`, `AttributeError`, `KeyError`, `IndexError`, `ZeroDivisionError`, `RuntimeError`, `StopIteration`, `RecursionError`, `MemoryError`, `OverflowError` |
| `configuration` | `KeyError` on config dict, `configparser.Error`, `yaml.YAMLError`, `toml.TomlDecodeError`, `os.environ` KeyError |
| `dependency` | `ImportError`, `ModuleNotFoundError`, `pkg_resources.DistributionNotFound`, `pip._vendor` errors |
| `docker` | `docker.errors.*`, `requests.exceptions.ConnectionError` to Docker socket |
| `network` | `ConnectionRefusedError`, `TimeoutError`, `socket.gaierror`, `urllib3.exceptions.*`, `requests.exceptions.ConnectionError` (non-Docker), `ssl.SSLError` |
| `database` | `psycopg2.OperationalError`, `sqlalchemy.exc.*`, `django.db.utils.*`, `pymongo.errors.*`, `redis.exceptions.*`, `alembic.util.exc.*` |
| `permission` | `PermissionError`, `OSError: [Errno 13]`, `subprocess.CalledProcessError` with permission message |

### Node.js / JavaScript

| Category | Error Patterns |
|----------|---------------|
| `syntax` | `SyntaxError`, `Unexpected token`, `Unexpected identifier`, `Cannot use import` |
| `runtime` | `TypeError`, `ReferenceError`, `RangeError`, `Error`, `UnhandledPromiseRejection`, `ERR_*` |
| `configuration` | `Error: Missing required`, `ENOENT` on config files, `dotenv` errors |
| `dependency` | `Cannot find module`, `MODULE_NOT_FOUND`, `ERR_MODULE_NOT_FOUND`, `ERESOLVE`, `npm ERR!` |
| `docker` | Same as universal Docker patterns |
| `network` | `ECONNREFUSED`, `ETIMEDOUT`, `ENOTFOUND`, `ECONNRESET`, `ERR_SOCKET_*`, `fetch failed` |
| `database` | `SequelizeConnectionError`, `MongoServerError`, `PrismaClientKnownRequestError`, `PROTOCOL_CONNECTION_LOST` |
| `permission` | `EACCES`, `EPERM`, `Error: EACCES: permission denied` |

### Go

| Category | Error Patterns |
|----------|---------------|
| `syntax` | `syntax error`, `unexpected`, `expected` (compiler errors) |
| `runtime` | `panic:`, `runtime error:`, `goroutine`, `fatal error:`, `signal SIGSEGV` |
| `configuration` | `flag provided but not defined`, `missing required`, config parse errors |
| `dependency` | `cannot find module`, `go: module`, `missing go.sum entry`, `ambiguous import` |
| `network` | `dial tcp`, `connection refused`, `i/o timeout`, `no such host`, `TLS handshake` |
| `database` | `pq:`, `sql:`, `gorm`, `mongo`, `redis` connection/query errors |
| `permission` | `permission denied`, `operation not permitted` |

### Shell / Bash

| Category | Error Patterns |
|----------|---------------|
| `syntax` | `syntax error`, `unexpected token`, `unexpected EOF` |
| `runtime` | Non-zero exit code, `command not found`, `segmentation fault`, `killed`, `illegal instruction` |
| `configuration` | `unbound variable`, missing env var errors, `source: not found` on config files |
| `dependency` | `command not found` (for expected tools), `No such file or directory` on binaries |
| `permission` | `Permission denied`, `Operation not permitted`, `cannot create`, `Read-only file system` |

### Docker (Universal)

| Pattern | Sub-Category |
|---------|-------------|
| `failed to build`, `COPY failed`, `RUN` step error | Build failure |
| `Exited (N)`, `OOMKilled`, `container died` | Container crash |
| `port is already allocated`, `address already in use` | Port conflict |
| `healthcheck: unhealthy`, `health_check failed` | Health failure |
| `network not found`, `could not connect to` | Network issue |
| `no space left on device`, `disk quota exceeded` | Resource exhaustion |
| `image not found`, `manifest unknown`, `pull access denied` | Image issue |
| `permission denied while trying to connect to Docker daemon` | Daemon access |
| `ERROR: Couldn't connect to Docker daemon` | Daemon not running |

---

## Cascading Error Detection

Some errors are symptoms of upstream failures. Check for these patterns:

| Reported Error | Often Caused By | Check |
|----------------|----------------|-------|
| `ConnectionRefused` on app port | Container crashed | `docker compose ps` — is the service running? |
| `ImportError` after deploy | Missing dependency in Docker image | Check Dockerfile `RUN pip install` / `COPY requirements.txt` |
| `ECONNRESET` on API call | Backend crashed during request | Backend container logs for panic/exception |
| `502 Bad Gateway` from nginx | Upstream service down | Check upstream container health |
| `Migration failed` | Database not ready | Check DB container health, startup order |
| Multiple `TypeError` | Wrong library version | Check installed vs expected versions |

**Rule**: Always check logs for errors **before** the reported error timestamp. The first error is often the root cause.

---

## Confidence Scoring

| Confidence | When to Assign |
|------------|---------------|
| **HIGH** | Error message directly matches a known pattern, category is unambiguous |
| **MEDIUM** | Error matches a pattern but could fit multiple categories, or is a cascading symptom |
| **LOW** | Error is unfamiliar, doesn't match known patterns, or is too generic to classify |

When confidence is **LOW**, always flag for research escalation in the diagnostic report.
