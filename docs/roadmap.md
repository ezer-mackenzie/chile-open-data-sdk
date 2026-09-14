# Roadmap

The current implemented checkpoint is v0.2.0: synchronous core and typed catalog
services. The asynchronous interfaces below are planned, not available in that
version. Milestones describe acceptance criteria rather than promised dates.

## One SDK, two explicit client families

Keep one distribution, `chile-open-data-sdk`, and one import package,
`chile_open_data_sdk`. Synchronous and asynchronous users share models,
configuration, errors, and documented behavior.

| Purpose | Synchronous | Asynchronous (planned for 0.3.0) |
| --- | --- | --- |
| Generic CKAN site | `CKANClient` | `AsyncCKANClient` |
| Chile default endpoint | `ChileOpenDataClient` | `AsyncChileOpenDataClient` |
| Connection lifetime | `with client` / `client.close()` | `async with client` / `await client.aclose()` |
| Single request | `client.datasets.search(...)` | `await client.datasets.search(...)` |
| Dataset iteration | `for item in client.datasets.iter_search(...)` | `async for item in client.datasets.iter_search(...)` |
| Page iteration | `for page in client.datasets.iter_pages(...)` | `async for page in client.datasets.iter_pages(...)` |

Existing synchronous names remain compatible. Async request methods resolve to
the same result types. Async iterator factories return `AsyncIterator[T]` directly:
use `async for`, without awaiting the factory. No runtime `async_mode` switch or
method returning a union of a result and an awaitable is planned.

## Delivery sequence

Async parity moves ahead of DataStore so every new service can ship in both modes.
This revises the previous order, where DataStore was 0.3.0 and async was 0.4.0.

| Version | Capability and completion criteria |
| --- | --- |
| 0.1.0 | Implemented sync core, configuration, generic actions, errors, tests, documentation |
| 0.2.0 | Implemented typed catalog discovery, metadata models, dataset pagination |
| 0.3.0 | Native async clients, generic actions, all catalog services and iterators; shared sync/async contract suite and lifecycle tests |
| 0.4.0 | Typed DataStore search, SQL wrappers, and record iteration in both modes; shared serialization and dynamic-record models |
| 0.5.0 | Conservative read retries, backoff/jitter, Retry-After, deadlines, and cancellation-aware async waits; equivalent retry decisions in both modes |
| 0.6.0 | Explicit authenticated DataStore write services in both modes, with documented replay risks and write safeguards |
| 0.7.0 | Sync/async streaming downloads with credential isolation and cleanup; optional pandas/Polars conversion separated from network I/O |
| 0.8.0 | Expand paired examples, framework integration guides, CI and publishing verification; complete pending automation rather than recreate existing workflows |
| 0.9.0 | Audit public sync/async signatures, compatibility fixtures and typed record adapters; document and resolve parity gaps |
| 1.0.0rc1 | Freeze the candidate API and pass the support matrix, lifecycle, security, packaging, and migration checks |
| 1.0.0 | Stable API after user review and approval; published compatibility and deprecation policy |

## v0.3.0 implementation plan

1. Inventory the existing generic actions and catalog methods. Define paired
   signatures, fixtures, expected requests, results, and errors before refactoring.
2. Extract only duplicated network-independent request preparation and pagination
   state into public modules. Keep models, constants, types, validation, response
   parsing, and redaction shared. Retain the current synchronous behavior.
3. Add `AsyncCKANClient`, `AsyncChileOpenDataClient`, and `AsyncActionService`, using
   one owned HTTPX AsyncClient per SDK instance. Implement async context management,
   idempotent `aclose`, closed-client failures, and explicit transport injection.
4. Add async dataset, resource, organization, group, and tag services. Each exposes
   the same service attribute, method name, parameters, defaults, and resolved
   result type as its synchronous counterpart. Share preparation, not HTTP clients.
5. Implement lazy async page/item iteration with the existing stopping rules,
   initial-count bound, server page-cap handling, max_items behavior, and repeated
   page errors. Keep one page buffered and no implicit prefetch or fan-out.
6. Verify cancellation and concurrent calls: propagate cancellation unchanged,
   release response resources, preserve caller-owned task lifetime, and keep
   request state isolated. Never translate cancellation into a connection error.
7. Add paired runnable examples, API references, migration guidance, benchmarks,
   and release evidence. Ship the milestone only when the parity matrix passes.

## Parity requirements for v0.3.0 and later

| Area | Required evidence |
| --- | --- |
| Public API | Matching service/method coverage, parameter defaults, model types, and exception classes |
| Wire contract | Identical action URLs, JSON bodies, headers, and query semantics for paired fixtures |
| Validation | Matching invalid-input behavior before I/O and safe typed-result errors |
| Credentials | Redaction and exception-chain tests in both paths; no token forwarding to resource hosts |
| Pagination | Empty/capped/repeated pages, changing counts, early exit, zero/max item limits, and no prefetch |
| Lifetime | Pool reuse, closure on normal/error paths, idempotent close, and failure after closure |
| Async behavior | No synchronous HTTP calls or loop creation; cancellation propagation and overlapping requests with independent payloads |
| Compatibility | Python 3.11?3.14, locked and minimum runtime dependencies, and preserved sync behavior |
| Documentation | Paired examples execute offline; unavailable features are labeled as planned |

Use the same response fixtures and request assertions for both modes, with small
mode-specific test runners. Keep dedicated async tests for scheduling, cancellation,
and cleanup rather than treating matching return values as sufficient parity.
Use deterministic synchronization in concurrency tests instead of wall-clock speed
thresholds. Start with asyncio as the tested async backend; do not claim SDK-level
Trio support until it has its own CI coverage.

From v0.3.0 onward, each new network feature needs both implementations and tests
in the same milestone. Any deliberate exception must have a documented reason,
impact, and completion target. Pure model parsing and dataframe conversion remain
ordinary synchronous functions; async network access must not disguise blocking
file or CPU work. Downloads will need explicit nonblocking file-I/O handling.

See [Architecture](architecture.md) for module boundaries and planned usage.
Existing token handling, timeouts, pooling, redaction, and publishing workflows
remain foundations to extend. Version changes and tags follow completed,
validated work; this roadmap update does not implement or release async support.
