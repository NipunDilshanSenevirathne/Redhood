# Authorization, identity, and sessions

## Authorization matrix

Use at least two controlled users and, where relevant, two controlled tenants. Label the sessions and fixtures explicitly. Test unauthenticated, owner, same-tenant non-owner, other-tenant user, delegated user, and revoked member when available. Missing identities are recorded gaps.

For each sensitive object/action, establish normal owner access and a meaningful non-owner control. Substitute only an identifier belonging to another **owned test fixture**. Check read, update, delete only when approved, share, export, clone, download, and job status separately. Include nested parent/child mismatches, batch operations, secondary-user assignment, and server-computed fields. A UUID is not an authorization control.

Check actual returned private canaries or persisted effects. A 200 may contain an error; a 302 may contain leaked data; a 403 can follow an already-completed operation. Confirm the access is contrary to intended sharing and permissions. [Access control](https://portswigger.net/web-security/access-control), [OWASP authorization guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

Extend the matrix across lifecycle transitions: invitation issued/accepted/revoked; membership removed; role downgraded; object transferred; project archived; signed link expired. Compare immediate and delayed access against documented revocation expectations. Do not confuse an intentionally durable share link with an undocumented session bypass.

## Authentication and recovery

Model registration, verification, login, MFA, recovery, account linking, email change, device enrollment, and session revocation as separate transitions. Identify which principal each token is bound to and which operation consumes it. Test replay and cross-session binding with your own tokens and accounts, with bounded attempts. Avoid password guessing and sending messages to other people.

Verify login/MFA completion on the server, not only in the UI. Check that security changes invalidate the appropriate sessions and that recovery does not silently reduce the required identity assurance. Prove an unauthorized account transition, not merely a different response or missing UI prompt. Treat user enumeration as a separate, program-dependent issue rather than automatic account takeover.

## OAuth and OIDC

Draw the complete browser redirect sequence and identify client, authorization server, redirect URI, state, nonce where applicable, PKCE, issuer, audience, and account-linking decision. Test with controlled identities and registered test clients. Check exact binding at each hop and whether the final account differs from the intended principal. Do not follow a third-party redirect as an active security test unless that service is authorized. [OAuth testing](https://portswigger.net/web-security/oauth).

## JWT and SAML

For JWTs, distinguish decoding from verification. Review accepted algorithms, key selection, issuer/audience, expiration, and token-purpose separation. An altered token must be accepted by a protected server operation to establish a verification failure; a decoded payload proves nothing. Never brute-force production keys. [JWT guidance](https://portswigger.net/web-security/jwt).

For SAML, compare what is signed, what is validated, and what supplies the consumed identity. Include issuer, audience, recipient, destination, request correlation, validity, and replay rules. Use local fixtures/test IdP and inspect library/version/patch differences. Signature success on one XML element does not prove that the consumed assertion is authenticated. GitHub's parser-differential research illustrates why parsing and signature validation must agree. [GitHub research](https://github.blog/security/sign-in-as-anyone-bypassing-saml-sso-authentication-with-parser-differentials/).

## Exit criteria

Keep a role × action × lifecycle table with evidence references. Report the least privilege needed, the exact controlled boundary crossed, and any required victim interaction. A missing account, blocked SSO provider, or unreadable response is not a negative security result.
