# Roadmap

Milestones describe real usable checkpoints; dates are not promised. This task
stops at v0.1.0. Documentation, CI, and security basics are included early so the
first release can be reviewed and built.

| Version | Planned capability |
| --- | --- |
| 0.1.0 | Sync core, configuration, generic actions, errors, tests, documentation |
| 0.2.0 | Typed dataset/resource/catalog models and discovery, catalog pagination |
| 0.3.0 | Typed DataStore search and SQL wrappers, record iteration |
| 0.4.0 | Async clients, services, and iterator parity |
| 0.5.0 | Conservative read retries, backoff/jitter, Retry-After, resilience hardening |
| 0.6.0 | Explicit authenticated DataStore write services and write safeguards |
| 0.7.0 | Streaming downloads with credential isolation, optional pandas/Polars |
| 0.8.0 | Documentation and automation expansion, publishing integration |
| 0.9.0 | Public API review, compatibility fixtures, typed record adapters |
| 1.0.0rc1 | Release candidate after full feature and compatibility review |
| 1.0.0 | Stable API only after user review and approval |

Token transport, granular timeouts, pool settings, and redaction are already in
the foundation because they support a safe reusable core. Later milestones extend
them; they must not create artificial commits or tags for work already completed.
