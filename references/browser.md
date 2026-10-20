# Browser-observable boundaries

Use a clean browser context with controlled accounts and explicit origin tracking. Proxy traffic alone cannot prove browser exploitability. Record relevant browser version and security headers.

## XSS and DOM flows

Identify the precise source, transformations, context, and sink. Start with an inert unique marker, then a harmless execution demonstration in an owned fixture when allowed. Determine reflected/stored/DOM behavior and whether another controlled account reaches it through a realistic flow. Distinguish HTML injection, self-XSS, sandboxed execution, and execution in the protected origin. Record CSP and Trusted Types effects; do not claim bypass merely because a scanner prints a payload. [DOM vulnerability model](https://portswigger.net/web-security/dom-based).

## Cross-origin state and data

For CORS, verify a real browser can read the sensitive synthetic response from the controlled test origin with the actual credential behavior. Reflected ACAO alone is insufficient; wildcard origin plus credentials is not automatically exploitable. For CSRF, demonstrate an unintended state change in the controlled victim account with the browser's actual cookie/SameSite behavior and request constraints. CORS does not substitute for CSRF protection. [CORS](https://portswigger.net/web-security/cors), [CSRF](https://portswigger.net/web-security/csrf).

For postMessage, trace sender, target window, exact origin checks, message schema, and downstream effect. For clickjacking, show a meaningful protected action can be reached through the framing condition; missing headers alone are weak evidence. For cross-site leaks, use synthetic private states and repeatable browser controls; avoid turning an oracle into extraction of real private information.

## Prototype pollution

Separate a writable prototype path from a reachable behavior-changing consumer. Demonstrate an inert marker in a disposable context and identify the gadget through source tracing. Do not claim RCE from pollution alone. Avoid server-global pollution on shared production workers; local reproduction is preferable. Report 998398 connects a fragment parser to a separate JavaScript execution consumer. [Prototype pollution](https://portswigger.net/web-security/prototype-pollution).

## Report

Include origin, user interaction, account roles, browser behavior, execution/state oracle, and clean-session reproduction. Do not use another person's session, steal cookies, or deliver payloads to real users. Clear stored test content and close controlled callback listeners after verification.
