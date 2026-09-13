# Security policy

## Supported versions

Security fixes target the latest released version. v0.1.0 is the initial alpha;
there are no older supported release lines or service-level guarantees.

## Reporting a vulnerability

Report vulnerabilities privately to the maintainer at
ramirez.ruiz.eliezer.reuven@gmail.com. Include the affected version, reproduction
steps, and impact using synthetic credentials. Do not put tokens, private data,
or exploit details in public issues. Coordinate disclosure with the maintainer;
no response-time commitment is currently offered.

## Credential handling

Use HTTPS and explicit CKAN tokens with the minimum necessary permissions.
Never commit `.env` files or tokens. Revoke and rotate exposed credentials at the
issuing CKAN site. Removing a token from a later commit does not revoke it.

The SDK excludes tokens from configuration repr, redacts SDK error context,
disables redirects, and does not retry generic actions. It cannot protect tokens
that applications print directly or sensitive data returned in successful results.
Custom transports and application logging remain the caller's responsibility.

Generic actions can mutate data. A network timeout does not prove that a write
failed; inspect server state before retrying. Use local/staging CKAN instances for
write tests. The library does not execute or download resource files in v0.1.0.
