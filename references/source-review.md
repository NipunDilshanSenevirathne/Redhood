# Source-assisted depth

Use source access to reduce network uncertainty. Do not install or run an unfamiliar repository automatically. Inspect dependency manifests and build hooks before any local execution; use an isolated environment for untrusted code.

Map entry points, authentication middleware, authorization helpers, tenant context, serializers, background queues, and sensitive sinks. Search using the project framework's real conventions. Trace one promising route end to end before broad keyword scanning. A dangerous function without attacker-controlled reachable input is not a confirmed vulnerability.

Check disagreements across layers: validation before decoding; authorization before object resolution; worker execution after membership revocation; serializer behavior differing by object type; signed content differing from consumed content; safe API bypassed by an alternate helper. Capture exact file/line/commit references.

Build a minimal local regression test expressing the violated invariant. Use a positive and negative fixture, document required feature flags, and avoid executing application startup hooks with production credentials. SAST findings are leads; establish source → transformations → controls → sink, and explain missing information.

When reviewing a patch, identify the root cause and search for equivalent sinks/entry points, not merely the fixed string. Record whether the fix centralizes enforcement or protects only one caller. Variant analysis can scale a well-understood code pattern; it cannot prove every match is exploitable. [GitHub Security Lab](https://securitylab.github.com/research/one-year-of-security-lab/).

## Specialist routing

For mobile, separate backend authorization from on-device storage, inter-app communication, deep links, platform permissions, and transport behavior. Use a company-owned test device/emulator and applicable MASTG cases. Client hardening gaps are not automatically backend compromise. [OWASP MASTG](https://mas.owasp.org/MASTG/).

For native memory safety, use a bounded local harness, sanitizers, and minimized crashing inputs; distinguish crash, memory corruption, and demonstrated security consequence. Never claim arbitrary execution from a crash alone. For hardware, cryptographic protocol design, kernel, or embedded targets, explicitly obtain the specialist environment and testing constraints. The supplied report index includes these categories; the web/API playbooks do not replace specialist expertise.
