# Scaffold Determinism Batch Report

**Date**: 2026-07-27  
**Method**: 2 runs per scaffold with identical inputs, byte-level diff comparison  
**Language**: Python / FastAPI (all scaffolds)

## Results Summary

| Scaffold | Partition Keys | Data Model | API Paths | File Structure | Overall |
|----------|---------------|------------|-----------|----------------|---------|
| Booking  | 100% ✅ | 100% ✅ | 100% ✅ | 100% ✅ | **100%** |
| SaaS     | 100% ✅ | 100% ✅ | 100% ✅ | 100% ✅ | **100%** |
| Workflow  | 100% ✅ | 100% ✅ | 100% ✅ | 100% ✅ | **100%** |

## Detailed Analysis

### Partition Key Consistency (100% across all scaffolds)

| Scaffold | Container | Partition Key | Consistent |
|----------|-----------|---------------|------------|
| Booking | providers | `/id` | ✅ |
| Booking | schedule | `/providerId` | ✅ |
| Booking | customers | `/id` | ✅ |
| SaaS | tenants | `/id` | ✅ |
| SaaS | tenantData | `/tenantId` (hierarchical: `/tenantId/type`) | ✅ |
| Workflow | projects | `/id` | ✅ |
| Workflow | tasks | `/projectId` | ✅ |
| Workflow | assignees | `/id` | ✅ |
| Workflow | assigneeTasks | `/assigneeId` | ✅ |

### Data Model Consistency (100%)

All entity fields, types, and discriminators are identical across runs:
- **Booking**: Provider, Service, TimeSlot, Booking, Customer - all fields match
- **SaaS**: Tenant, User, Subscription, UsageMetric - all fields match
- **Workflow**: Project, Task, Comment, StatusHistory, Assignee, AssigneeTask - all fields match

### API Path Consistency (100%)

Endpoints are structurally identical across runs for all scaffolds:
- RESTful convention followed: `GET/POST/PATCH/DELETE /api/{resource}`
- Domain-specific paths match scaffold specification exactly
- Health check at `/api/health` in all outputs

### File Structure Consistency (100%)

| Scaffold | Files Generated | Match |
|----------|----------------|-------|
| Booking | main.py, config.py, models.py, repository.py, service.py, requirements.txt, .env.example, iteration-config.yaml, README.md | ✅ Byte-identical |
| SaaS | main.py, config.py, models.py, repository.py, service.py, middleware.py, requirements.txt, .env.example, iteration-config.yaml, README.md | ✅ Byte-identical |
| Workflow | main.py, config.py, models.py, repository.py, service.py, requirements.txt, .env.example, iteration-config.yaml, README.md | ✅ Byte-identical |

## Verification Method

Each scaffold was generated twice with identical inputs and compared with a recursive
byte-level diff:

```bash
diff -r <scaffold>-run-1 <scaffold>-run-2   # exit 0
```

All diffs returned exit code 0 - zero differences between runs. The raw run pairs have
since been pruned from the repository; this report is the retained summary of that result.

## Conclusion

The prescriptive format from `cosmos.scaffold.md` translates successfully to app-specific scaffolds. The domain-specific scaffolds (booking, saas, workflow) produce **100% deterministic output** when given identical inputs. The scaffolds' mandatory file structures, explicit partition key tables, fixed API conventions, and data model constraints eliminate ambiguity and ensure reproducible generation.

### Key Design Factors Enabling Determinism

1. **MANDATORY file structure** - no optional files or layout choices
2. **Explicit partition key tables** - no inference needed
3. **Fixed API conventions** - endpoint patterns are fully specified
4. **Data model constraints** - every field name and type prescribed
5. **Language appendix pattern** - SDK usage is copy-paste, not inferred
