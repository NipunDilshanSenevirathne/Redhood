# Infrastructure, caches, cloud, and supply chain

## Cache boundaries

Map CDN, proxy, application, and browser caches separately. Identify which request properties influence the key and which influence the response. For deception, use private synthetic content and a second controlled unauthenticated context; establish storage and cross-context retrieval. A HIT header or odd extension does not prove leakage. [Web cache deception](https://portswigger.net/web-security/web-cache-deception).

For poisoning or cache-key discrepancies, use an isolated cache namespace and harmless marker only under method-specific permission. Verify a unique path/key is actually isolated before testing; a presumed cache buster can be ignored. Shared caches can affect unrelated users and tenants. If isolation cannot be established, use a local reproducer or configuration review.

## Request desynchronization

Inspect actual frontend-to-backend protocol behavior; client-facing HTTP/2 does not imply HTTP/2 upstream. Parser discrepancies, message boundaries, early responses, and downgrades require specialized validation. A timeout or differential status is a lead, not proof of request smuggling. Use a dedicated lab/owner-approved isolated connection path; never contaminate other users' requests to demonstrate impact. [HTTP/1.1 research](https://portswigger.net/research/http1-must-die).

## Cloud and secrets

Review company-supplied IAM, bucket policies, workload identities, signed URL rules, and resource ownership. A public bucket name, key-shaped string, exposed login page, or cloud error is not itself a vulnerability. Verify intended access and use synthetic objects. Never download unrelated data to count impact.

For a discovered credential, preserve a redacted fingerprint and source location. Ask the owner to establish validity/scope, or use only a specifically permitted minimal verification action. Do not use it to enumerate unrelated accounts, repositories, or cloud resources. Report 1087489 illustrates release-artifact secret exposure; the transferable audit target is the packaging process and credential boundary.

## DNS and takeover

Distinguish DNS record presence, dangling service reference, provider-specific claimability, and actual ownership. Provider fingerprints age; verify current behavior. Do not register external resources or claim namespaces without express permission covering the claim and cleanup. A CNAME to a third party does not authorize testing that provider.

## Dependencies and CI

Review registry selection, private namespace routing, lockfiles, provenance, build secrets, untrusted PR handling, workflow permissions, and artifact publication. Demonstrate resolution mistakes with an isolated local registry or owner-side logs. Do not publish lookalike packages or inject code into public package ecosystems as a default test. Report 925585 is a precedent for checking private/public registry assumptions.

For exposed developer services, verify access expectations using minimal metadata or owner-controlled fixtures. Avoid triggering builds, debug execution, destructive API calls, and costly workloads without method-specific permission. Banner/version matches should be checked against vendor advisories and reachable features before reporting.
