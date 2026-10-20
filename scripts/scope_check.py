#!/usr/bin/env python3
"""Conservative offline URL preflight. No networking; not a runtime traffic guard."""
import argparse
import ipaddress
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

def host_name(value):
    if not isinstance(value,str) or not value or value != value.strip():
        raise ValueError('Invalid host')
    if value.endswith('.') or any(c in value for c in '/\\@%?#'):
        raise ValueError('Ambiguous host')
    try:return str(ipaddress.ip_address(value)).lower()
    except ValueError:pass
    host=value.encode('idna').decode('ascii').lower()
    if len(host)>253 or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',part) for part in host.split('.')):
        raise ValueError('Invalid DNS name')
    # Browser-style alternate numeric IP encodings require manual review.
    if re.fullmatch(r'[0-9.]+',host) or any(p.startswith('0x') for p in host.split('.')):
        raise ValueError('Ambiguous numeric host')
    return host

def matches(host,pattern):
    if pattern.startswith('*.'):
        base=host_name(pattern[2:])
        return host != base and host.endswith('.'+base)
    return host==host_name(pattern)

def prefix_match(path,prefix):
    if prefix=='/':return True
    return path==prefix.rstrip('/') or path.startswith(prefix.rstrip('/')+'/')

def clean_path(path):
    # Preserve raw URL bytes; reject normalization-sensitive paths for manual review.
    if not path.startswith('/') or '\\' in path or '%' in path or ';' in path or '//' in path:
        raise ValueError('Ambiguous path: manual review required')
    if any(x in ('.','..') for x in path.split('/')):
        raise ValueError('Dot segment: manual review required')
    if any(ord(c)<33 or ord(c)>126 for c in path):
        raise ValueError('Noncanonical path: manual review required')
    return path

def validate_contract(c):
    if not isinstance(c,dict):
        raise ValueError('Contract must be an object')
    reference=c.get('authorization_reference')
    if c.get('authorization_confirmed') is not True or not isinstance(reference,str) or not reference.strip():
        raise ValueError('Authorization is not recorded')
    if not isinstance(c.get('allowed'),list) or not c['allowed']:
        raise ValueError('No allowlist')
    for rule in c['allowed']:
        if not isinstance(rule,dict) or not isinstance(rule.get('host'),str):
            raise ValueError('Invalid allow rule')
        host_name(rule['host'][2:] if rule['host'].startswith('*.') else rule['host'])
        if not isinstance(rule.get('schemes'),list) or not rule['schemes'] or any(s not in ('http','https') for s in rule['schemes']):
            raise ValueError('Invalid schemes')
        if not isinstance(rule.get('ports'),list) or not rule['ports'] or any(type(n) is not int or not 1<=n<=65535 for n in rule['ports']):
            raise ValueError('Invalid ports')
        if not isinstance(rule.get('path_prefixes'),list) or not rule['path_prefixes']:raise ValueError('Missing path constraints')
        for prefix in rule['path_prefixes']:clean_path(prefix)
    if not isinstance(c.get('excluded_hosts',[]),list) or not isinstance(c.get('excluded_paths',[]),list):
        raise ValueError('Exclusions must be lists')
    for pattern in c.get('excluded_hosts',[]):host_name(pattern[2:] if pattern.startswith('*.') else pattern)
    for rule in c.get('excluded_paths',[]):
        if not isinstance(rule,dict) or not isinstance(rule.get('host'),str) or not isinstance(rule.get('prefixes'),list) or not rule['prefixes']:
            raise ValueError('Invalid path exclusion')
        host_name(rule['host'][2:] if rule['host'].startswith('*.') else rule['host'])
        for prefix in rule['prefixes']:clean_path(prefix)

def check(c,url):
    try:
        validate_contract(c)
        if not isinstance(url,str) or any(ord(ch)<33 or ord(ch)>126 for ch in url) or '\\' in url:
            raise ValueError('Noncanonical URL')
        u=urlsplit(url)
        if u.scheme not in ('http','https') or not u.netloc or u.username is not None or u.password is not None or u.fragment:
            raise ValueError('Require absolute HTTP(S) URL without userinfo/fragment')
        host=host_name(u.hostname or '')
        if u.netloc.endswith(':'):raise ValueError('Empty port')
        port=u.port if u.port is not None else (443 if u.scheme=='https' else 80)
        path=clean_path(u.path or '/')
        if any(matches(host,p) for p in c.get('excluded_hosts',[])):
            return False,'excluded host'
        for rule in c.get('excluded_paths',[]):
            if matches(host,rule['host']) and any(prefix_match(path,p) for p in rule['prefixes']):
                return False,'excluded path'
        for rule in c['allowed']:
            if matches(host,rule['host']) and u.scheme in rule['schemes'] and port in rule['ports'] and any(prefix_match(path,p) for p in rule['path_prefixes']):
                return True,'URL preflight passed; method, query semantics, DNS, redirects, credentials, and side effects still require review'
        return False,'not allowlisted'
    except (ValueError,KeyError,TypeError,AttributeError,UnicodeError) as exc:
        return False,str(exc)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--contract',required=True,type=Path);p.add_argument('--url',required=True)
    args=p.parse_args();c=json.loads(args.contract.read_text(encoding='utf-8-sig'))
    allowed,reason=check(c,args.url)
    # Do not echo query strings which can contain credentials.
    print(json.dumps({'allowed':allowed,'reason':reason}))
    return 0 if allowed else 2

if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError) as exc:
        print(json.dumps({'allowed':False,'reason':str(exc)}));sys.exit(2)
