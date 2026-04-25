# Specification Patterns Reference

## Specification Types

### Feature Specification

For new features or capabilities.

```markdown
# Feature: [Feature Name]

## Overview
Brief description of the feature and its value.

## Problem Statement
What problem does this solve? Why is it needed?

## Goals
- Primary goal
- Secondary goals

## User Stories
As a [user type], I want [action] so that [benefit].

## Functional Requirements
| ID | Priority | Description |
|----|----------|-------------|
| FR-01 | MUST | ... |

## Non-Functional Requirements
| ID | Category | Description |
|----|----------|-------------|
| NFR-01 | Performance | ... |

## Acceptance Criteria
### AC-01: [Scenario]
Given... When... Then...

## UI/UX (if applicable)
Wireframes, mockups, user flows.

## Data Model
Entity definitions, relationships.

## API Specification
Endpoints, request/response formats.

## Dependencies
Internal and external dependencies.

## Out of Scope
What this feature explicitly does NOT include.

## Security Considerations
Authentication, authorization, data handling.

## Migration Strategy (if applicable)
How to migrate existing data/users.

## Rollback Plan
How to revert if issues arise.
```

### Technical Design Document (TDD)

For complex technical implementations.

```markdown
# Technical Design: [Component/System Name]

## Overview
What is being designed and why.

## Background
Context, history, current state.

## Goals
- What we're trying to achieve
- Success metrics

## Non-Goals
What we're explicitly NOT trying to achieve.

## Proposed Solution

### Architecture
High-level architecture description.

```
[Architecture diagram]
```

### Components
| Component | Responsibility |
|-----------|---------------|
| Component A | ... |
| Component B | ... |

### Data Flow
How data moves through the system.

### Data Model
```sql
-- Schema definitions
CREATE TABLE ...
```

### API Design
```yaml
paths:
  /api/resource:
    get:
      summary: Get resource
```

### Security Design
Authentication, authorization, encryption.

## Alternatives Considered

### Option A: [Name]
- Pros: ...
- Cons: ...
- Why rejected: ...

### Option B: [Name]
- Pros: ...
- Cons: ...
- Why rejected: ...

## Implementation Plan
Phased approach to implementation.

## Testing Strategy
How this will be tested.

## Monitoring & Observability
Metrics, logging, alerting.

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| ... | ... |

## Open Questions
Items needing resolution.

## References
Related documents, RFCs, standards.
```

### API Specification

For API-first development.

```markdown
# API Specification: [API Name]

## Overview
Purpose and scope of this API.

## Base URL
```
Production: https://api.example.com/v1
Staging: https://api.staging.example.com/v1
```

## Authentication
How clients authenticate.

## Rate Limiting
Request limits and quotas.

## Endpoints

### Resource: [Name]

#### Create Resource
```http
POST /resources
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "string",
  "type": "string"
}
```

**Response: 201 Created**
```json
{
  "id": "uuid",
  "name": "string",
  "type": "string",
  "createdAt": "ISO8601"
}
```

**Errors:**
| Code | Description |
|------|-------------|
| 400 | Invalid request body |
| 401 | Unauthorized |
| 409 | Resource already exists |

#### Get Resource
```http
GET /resources/{id}
Authorization: Bearer {token}
```

**Response: 200 OK**
```json
{
  "id": "uuid",
  "name": "string",
  "type": "string"
}
```

## Data Models

### Resource
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique identifier |
| name | String | Yes | Resource name |
| type | Enum | Yes | One of: A, B, C |

## Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message",
    "details": []
  }
}
```

## Versioning
How API versions are managed.

## Changelog
Version history and changes.
```

## Requirement Formats

### MoSCoW Prioritization

| Priority | Description |
|----------|-------------|
| **MUST** | Non-negotiable, required for MVP |
| **SHOULD** | Important, include if possible |
| **COULD** | Desirable, nice to have |
| **WON'T** | Explicitly out of scope (this version) |

### Requirement ID Conventions

```
FR-[NN]   - Functional Requirement
NFR-[NN]  - Non-Functional Requirement
SR-[NN]   - Security Requirement
DR-[NN]   - Data Requirement
IR-[NN]   - Integration Requirement
```

### Good vs Bad Requirements

| Bad | Good |
|-----|------|
| System should be fast | Response time < 200ms at p95 |
| Handle errors appropriately | Display user-friendly error messages |
| Support many users | Support 10,000 concurrent users |
| Secure authentication | Use OAuth 2.0 with PKCE flow |
| Easy to use interface | Form completion in < 60 seconds |

## Acceptance Criteria Formats

### Given-When-Then (BDD)

```gherkin
Scenario: User login with valid credentials
  Given a registered user with email "user@example.com"
  And the user is on the login page
  When the user enters valid email and password
  And clicks the login button
  Then the user is redirected to the dashboard
  And a session token is created
```

### Checklist Format

```markdown
### AC: User Registration

- [ ] User can enter email address
- [ ] User can enter password (min 8 chars)
- [ ] Password strength indicator shown
- [ ] Validation errors displayed inline
- [ ] Success message shown on completion
- [ ] Confirmation email sent within 30 seconds
```

### Rule-Based

```markdown
### AC: Order Pricing

**Rules:**
1. Base price = sum of item prices
2. If order total > $100, apply 10% discount
3. Shipping free for orders > $50, else $5.99
4. Tax calculated based on shipping address
5. Final price = (base - discount) + shipping + tax
```

## Non-Functional Requirement Categories

### Performance

```markdown
| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time (p50) | < 100ms | API latency |
| Response Time (p95) | < 200ms | API latency |
| Response Time (p99) | < 500ms | API latency |
| Throughput | 1000 req/s | Load test |
| Page Load | < 3s | Lighthouse |
```

### Scalability

```markdown
| Metric | Target |
|--------|--------|
| Concurrent Users | 10,000 |
| Data Volume | 100M records |
| Growth Rate | 2x yearly |
```

### Availability

```markdown
| Metric | Target |
|--------|--------|
| Uptime SLA | 99.9% |
| RTO | 1 hour |
| RPO | 15 minutes |
| MTTR | 30 minutes |
```

### Security

```markdown
| Requirement | Standard |
|-------------|----------|
| Authentication | OAuth 2.0 / OIDC |
| Authorization | RBAC |
| Encryption (transit) | TLS 1.3 |
| Encryption (rest) | AES-256 |
| Password Storage | bcrypt/Argon2 |
| Session Management | Secure cookies, 24h expiry |
```

## Dependency Documentation

### Internal Dependencies

```markdown
## Dependencies

### Required (blocking)
- **Auth Service v2** - For user authentication
  - Status: In development
  - Expected: Q2 2024
  - Contact: @auth-team

### Optional (non-blocking)
- **Analytics Service** - For usage tracking
  - Can implement stub, replace later
```

### External Dependencies

```markdown
## External Dependencies

| Service | Purpose | Version | Fallback |
|---------|---------|---------|----------|
| Stripe | Payments | API v2023-10 | None (critical) |
| SendGrid | Email | API v3 | Queue + retry |
| Auth0 | SSO | Current | Internal auth |
```

## Out of Scope Template

```markdown
## Out of Scope

The following are explicitly NOT included in this specification:

### Deferred to Future
- Mobile app support (planned for v2)
- Internationalization (planned for v2)
- Advanced analytics dashboard

### Will Not Do
- Support for IE11
- Self-hosted deployment option
- Custom branding per tenant

### Handled Elsewhere
- Infrastructure provisioning (see infra-spec.md)
- CI/CD pipeline (see devops-spec.md)
```
