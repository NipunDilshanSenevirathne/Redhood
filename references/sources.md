# Source register

Accessed during 2026-10-19/20; user-facing completion date 2026-10-20 (Asia/Colombo). Documentation may change after this package. Each linked source has a specific role; these are not claims that all linked subpages or techniques were read or tested.

## Format and corpus

1. [Claude Code skills](https://code.claude.com/docs/en/skills) — native folder layout, discovery, invocation, supporting files.
2. [codebygk collection](https://github.com/codebygk/hackerone-bug-bounty-reports) — supplied metadata snapshot; commit `cb5d63cd158c4601978fee9687d65385853019b5`.
3. [Critical index](https://github.com/codebygk/hackerone-bug-bounty-reports/blob/cb5d63cd158c4601978fee9687d65385853019b5/results/based_on_severity/critical.md) — critical report leads.
4. [Marco collection](https://github.com/bugbountywithmarco/bugbounty-disclosed-reports) — Markdown report corpus; commit `b6c76d1437e08a0ef77b7fbed612791c71cc4aa5`.

## Frameworks

5. [OWASP WSTG 4.2](https://wstg.owasp.org/v4.2/) — versioned web testing coverage reference.
6. [OWASP ASVS](https://owasp.org/projects/asvs) — security control verification framework.
7. [OWASP API Security 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/) — API risk distinctions.
8. [OWASP authorization cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) — authorization invariants.
9. [OWASP MASTG](https://mas.owasp.org/MASTG/) — specialist mobile routing reference.
10. [OWASP LLM project](https://owasp.org/projects/top-10-for-large-language-model-applications) — AI application security context.
11. [FIRST CVSS v4.0](https://www.first.org/cvss/v4.0/specification-document) — scoring semantics, when requested.

## Tool documentation

12. [Subfinder usage](https://docs.projectdiscovery.io/opensource/subfinder/usage).
13. [Subfinder running](https://docs.projectdiscovery.io/opensource/subfinder/running).
14. [httpx usage](https://docs.projectdiscovery.io/opensource/httpx/usage).
15. [Katana running](https://docs.projectdiscovery.io/opensource/katana/running).
16. [Nuclei running](https://docs.projectdiscovery.io/opensource/nuclei/running).
17. [Nuclei repository](https://github.com/projectdiscovery/nuclei).
18. [gau](https://github.com/lc/gau).
19. [waybackurls](https://github.com/tomnomnom/waybackurls).
20. [ffuf](https://github.com/ffuf/ffuf).

## Testing methods and original research

21. [Access control](https://portswigger.net/web-security/access-control).
22. [OAuth](https://portswigger.net/web-security/oauth).
23. [JWT](https://portswigger.net/web-security/jwt).
24. [API testing](https://portswigger.net/web-security/api-testing).
25. [GraphQL](https://portswigger.net/web-security/graphql).
26. [SSRF](https://portswigger.net/web-security/ssrf).
27. [File uploads](https://portswigger.net/web-security/file-upload).
28. [NoSQL injection](https://portswigger.net/web-security/nosql-injection).
29. [Template injection](https://portswigger.net/web-security/server-side-template-injection).
30. [DOM vulnerabilities](https://portswigger.net/web-security/dom-based).
31. [CORS](https://portswigger.net/web-security/cors).
32. [CSRF](https://portswigger.net/web-security/csrf).
33. [Prototype pollution](https://portswigger.net/web-security/prototype-pollution).
34. [Cache deception](https://portswigger.net/web-security/web-cache-deception).
35. [Race-condition state machines](https://portswigger.net/research/smashing-the-state-machine).
36. [HTTP/1.1 desync endgame](https://portswigger.net/research/http1-must-die).
37. [2025 research roundup](https://portswigger.net/research/top-10-web-hacking-techniques-of-2025) — discovery map; not independent reproduction of every finalist.
38. [ORM leaks](https://www.elttam.com/blog/leaking-more-than-you-joined-for).
39. [Next.js cache chains](https://zhero-web-sec.github.io/research-and-things/nextjs-cache-and-chains-the-stale-elixir).
40. [Redirect-loop SSRF](https://www.slcyber.io/research/novel-ssrf-technique-involving-http-redirect-loops).
41. [SAML parser differentials](https://github.blog/security/sign-in-as-anyone-bypassing-saml-sso-authentication-with-parser-differentials/).
42. [GitHub variant-analysis context](https://securitylab.github.com/research/one-year-of-security-lab/).

The individually reviewed HackerOne reports and the evidence level for each are enumerated in `data/reviewed-cases.json`. Their public JSON representations were read where available; fetching stopped after a 429 response. The supplied Markdown corpus supplies further local research material without additional HackerOne requests.

## Agentic systems and Redhood additions

The [agentic research register](agentic-research.md) adds 15 primary sources covering XBOW, NodeZero, Pentera, Hai, Shannon, Strix, PentestGPT and evaluation research. The [structured cards](test-cards.md) cite their additional topical primary sources. These sources informed design; they do not certify Redhood or establish a product ranking.

- [Claude subagents](https://code.claude.com/docs/en/sub-agents) — optional verifier format.
- [Claude security](https://code.claude.com/docs/en/security) — host permission context.
- [Claude hooks](https://code.claude.com/docs/en/hooks) — integration context only; no enforcement hook is bundled.
- [HackerOne agentic PTaaS architecture](https://www.hackerone.com/blog/agentic-ptaas-security-architecture) — stateful orchestration and validation architecture; vendor metrics are not cross-product scores.
- [OWASP GenAI risk taxonomy](https://genai.owasp.org/llm-top-10/) and [agentic threats](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/) — additional AI trust-boundary context.

The user-supplied Pashupatastra archive is the third corpus source. Its CSV provenance is recorded as `company-zip`, including its archive/data hashes. It attributes its upstream metadata to reddelexc/hackerone-reports; that upstream repository was not independently fetched for this merge.
