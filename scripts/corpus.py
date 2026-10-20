#!/usr/bin/env python3
"""Offline corpus builder/search. Does not fetch URLs or execute repository code."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / 'data' / 'reports.jsonl'
TOPICS = {
    'authorization': r'\b(?:idor|bola|authorization|access control|tenant|privilege)\b',
    'authentication': r'\b(?:authentication|login|session|password|recovery|mfa|otp)\b',
    'oauth': r'\b(?:oauth|oidc|pkce|redirect_uri)\b',
    'saml': r'\b(?:saml|assertion|xml signature)\b',
    'graphql': r'\bgraphql\b',
    'import-export': r'\b(?:imports?|exports?|bulkimports|migration)\b',
    'archive': r'\b(?:archive|symlink|untar|zip|tar|extraction)\b',
    'file-upload': r'\b(?:upload|multipart|filename|file upload)\b',
    'path-traversal': r'\b(?:traversal|arbitrary file|file inclusion)\b',
    'ssrf': r'\b(?:ssrf|server.side request forgery|metadata service)\b',
    'rendering': r'\b(?:pdf|renderer|rendering|template|ssti)\b',
    'sql-injection': r'\b(?:sql injection|sqli|sqlmap)\b',
    'query-filter': r'\b(?:nosql|orm|filter expression|odata)\b',
    'command-execution': r'\b(?:rce|command injection|code execution|popen|exec)\b',
    'deserialization': r'\b(?:deserialization|unserialize|object injection)\b',
    'xss': r'\b(?:xss|cross.site scripting)\b',
    'csrf': r'\b(?:csrf|cross.site request forgery)\b',
    'cors': r'\b(?:cors|access-control-allow-origin)\b',
    'prototype': r'\b(?:prototype pollution|__proto__)\b',
    'cache': r'\b(?:cache poisoning|cache deception|cached|caching)\b',
    'desync': r'\b(?:smuggling|desync|content-length|transfer-encoding)\b',
    'race': r'\b(?:race condition|toctou|concurrent|concurrency)\b',
    'business-logic': r'\b(?:business logic|payment|refund|gift card|coupon|balance)\b',
    'cloud': r'\b(?:aws|azure|gcp|kubernetes|s3 bucket|iam)\b',
    'secrets': r'\b(?:secret|credential|access token|api key|private key)\b',
    'supply-chain': r'\b(?:dependency confusion|npm|registry|supply.chain|workflow)\b',
    'mobile': r'\b(?:android|ios|apk|intent|deep link)\b',
    'memory-safety': r'\b(?:use.after.free|buffer overflow|memory corruption|out.of.bounds)\b',
    'ai': r'\b(?:prompt injection|llm|language model|chatbot)\b',
    'resource-consumption': r'\b(?:denial of service|redos|exhaustion|resource consumption)\b',
}

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def load_rows(path=DEFAULT_DATA):
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def topics(text):
    return [key for key, pattern in TOPICS.items() if re.search(pattern, text, re.I)]

def parse_markdown(path, text=None):
    if text is None:
        text = Path(path).read_text(encoding='utf-8-sig')
    header = text.split('## Vulnerability Information', 1)[0]
    match = re.search(r'^- \*\*Report ID\*\*:\s*(\d+)\s*$', header, re.M)
    if not match:
        raise ValueError(f'Missing report ID: {Path(path).name}')
    rid = match.group(1)
    def field(name):
        m = re.search(r'^- \*\*' + re.escape(name) + r'\*\*:\s*(.*?)\s*$', header, re.M)
        return m.group(1) if m else ''
    title = next((line[2:].strip() for line in header.splitlines() if line.startswith('# ')), '')
    body = text.split('## Vulnerability Information', 1)[1].split('\n## Attachments',1)[0] if '## Vulnerability Information' in text else ''
    # Presence is a heuristic, not a claim of completeness or semantic review.
    meaningful = body.strip() not in ('', 'N/A', 'No vulnerability information provided.', 'No vulnerability information available.')
    return {'id': rid, 'url': f'https://hackerone.com/reports/{rid}',
            'title': title, 'severity': field('Severity').lower() if field('Severity').lower() not in ('','n/a','null') else 'unknown',
            'program': field('Handle'), 'disclosed_at': field('Disclosed'),
            'topics': topics(text), 'markdown_file': Path(path).name,
            'markdown_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'markdown_chars': len(text), 'body_chars':len(body.strip()), 'body_present_heuristic': meaningful,
            'review_status': 'machine-indexed'}, text

def git_reports(repo, commit):
    """Read tracked report blobs without running or materializing their content."""
    listing = subprocess.run(['git','-C',str(repo),'ls-tree','-r','-z',commit,'--','reports'],check=True,capture_output=True).stdout
    entries=[]
    for entry in listing.split(b'\0'):
        if not entry:continue
        meta,path=entry.split(b'\t',1)
        mode,kind,oid=meta.split()
        if kind==b'blob' and mode==b'100644' and path.endswith(b'.md'):
            entries.append((oid.decode(),path.decode('utf-8')))
    for start in range(0,len(entries),100):
        batch=entries[start:start+100]
        raw=subprocess.run(['git','-C',str(repo),'cat-file','--batch'],input=('\n'.join(oid for oid,_ in batch)+'\n').encode(),check=True,capture_output=True).stdout
        pos=0
        for oid,path in batch:
            end=raw.index(b'\n',pos);header=raw[pos:end].split();size=int(header[2]);pos=end+1
            if header[0].decode()!=oid or header[1]!=b'blob':raise ValueError('Unexpected Git object')
            text=raw[pos:pos+size].decode('utf-8-sig');pos+=size+1
            yield Path(path).name,text

def build(metadata_path, markdown_dir, output, marco_commit, markdown_repo=None):
    raw = read_json(metadata_path)
    entries = raw['reports'] if isinstance(raw, dict) else raw
    merged = {}
    for row in entries:
        m = re.fullmatch(r'https://hackerone\.com/reports/(\d+)/?', row.get('url', ''))
        if not m:
            raise ValueError('Unexpected report URL in metadata')
        rid = m.group(1)
        if rid in merged:
            raise ValueError(f'Duplicate metadata ID: {rid}')
        item = {k: row.get(k) for k in ('title','url','program','severity','vulnerability_type','asset_type','disclosed_at','submitted_at')}
        item.update(id=rid, severity=row.get('severity') or 'unknown',
                    topics=topics((row.get('title') or '')+' '+(row.get('vulnerability_type') or '')),
                    sources=['codebygk'], review_status='metadata-only')
        merged[rid] = item
    seen = set()
    if markdown_dir or markdown_repo:
        documents = git_reports(markdown_repo,marco_commit) if markdown_repo else ((p,None) for p in sorted(Path(markdown_dir).glob('*.md')))
        for path,text in documents:
            item, _ = parse_markdown(path,text)
            rid = item['id']
            if rid in seen:
                raise ValueError(f'Duplicate Markdown ID: {rid}')
            seen.add(rid)
            prior = merged.get(rid)
            if prior:
                # Retain both source assertions where their metadata disagree.
                prior['marco_metadata'] = {k:item[k] for k in ('title','severity','program','disclosed_at')}
                prior['topics'] = sorted(set(prior['topics']) | set(item['topics']))
                prior.update({k:v for k,v in item.items() if k.startswith('markdown_') or k in ('body_chars','body_present_heuristic','review_status')})
                prior['sources'].append('marco')
            else:
                item['sources'] = ['marco']
                merged[rid] = item
            merged[rid]['markdown_url'] = 'https://github.com/bugbountywithmarco/bugbounty-disclosed-reports/blob/'+marco_commit+'/reports/'+quote(Path(path).name)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', encoding='utf-8', newline='\n') as f:
        for row in sorted(merged.values(), key=lambda x:int(x['id'])):
            f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
    return {'metadata_records':len(entries),'markdown_records':len(seen),
            'overlap':sum(len(r['sources'])==2 for r in merged.values()),'unique_reports':len(merged)}

def merge_company(rows, csv_path, output):
    """Merge supplied Pashupatastra metadata without adopting its instructions/code."""
    merged = {str(row['id']): dict(row) for row in rows}
    if len(merged) != len(rows):
        raise ValueError('Duplicate base report IDs')
    seen, overlap = set(), 0
    with Path(csv_path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        required = {'program', 'title', 'link', 'upvotes', 'bounty', 'vuln_type'}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError('Missing company metadata columns')
        for row in reader:
            match = re.fullmatch(r'(?:https://)?hackerone\.com/reports/([1-9][0-9]*)/?', row['link'].strip())
            if not match:
                raise ValueError('Unexpected company report URL')
            rid = match.group(1)
            if rid in seen:
                raise ValueError(f'Duplicate company report ID: {rid}')
            seen.add(rid)
            assertion = {key: row[key] for key in sorted(required)}
            item = merged.get(rid)
            if item is not None:
                overlap += 1
                item['sources'] = sorted(set(item.get('sources', [])) | {'company-zip'})
                item['topics'] = sorted(set(item.get('topics', [])) | set(topics(row['title']+' '+row['vuln_type'])))
            else:
                item = {'id': rid, 'url': f'https://hackerone.com/reports/{rid}',
                        'title': row['title'], 'program': row['program'], 'severity': 'unknown',
                        'vulnerability_type': row['vuln_type'], 'sources': ['company-zip'],
                        'topics': topics(row['title']+' '+row['vuln_type']),
                        'review_status': 'metadata-only'}
                merged[rid] = item
            # Bounty/votes are source assertions, never inferred severity or validity.
            item['company_metadata'] = assertion
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8', newline='\n') as f:
        for row in sorted(merged.values(), key=lambda x: int(x['id'])):
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True)+'\n')
    return {'base_records': len(rows), 'company_records': len(seen), 'overlap': overlap,
            'added_records': len(seen)-overlap, 'unique_reports': len(merged),
            'company_csv_sha256': hashlib.sha256(Path(csv_path).read_bytes()).hexdigest()}

ALIASES = {'idor':'authorization','bola':'authorization','ssrf':'ssrf','sqli':'sql-injection','rce':'command-execution','import':'import-export','export':'import-export','payment':'business-logic','auth':'authentication'}

def search(rows, query, severity=None, program=None, limit=5, reports_dir=None):
    words = re.findall(r'[\w-]+',query.casefold())
    if not words:
        return []
    results=[]
    for row in rows:
        if severity and (row.get('severity') or 'unknown') not in severity:
            continue
        if program and program.casefold() not in ((row.get('program') or '')+' '+(row.get('marco_metadata',{}).get('program') or '')+' '+(row.get('company_metadata',{}).get('program') or '')).casefold():
            continue
        title=(row.get('title') or '').casefold()
        alternatives = ' '.join(str(row.get(source, {}).get(key) or '') for source in ('company_metadata','marco_metadata') for key in ('title','program','vuln_type'))
        meta=(title+' '+(row.get('vulnerability_type') or '')+' '+(row.get('program') or '')+' '+alternatives).casefold()
        tags=row.get('topics',[])
        body=''
        if reports_dir and row.get('markdown_file'):
            base=Path(reports_dir).resolve()
            p=(base/row['markdown_file']).resolve()
            if p.parent != base:
                raise ValueError('Unsafe stored Markdown path')
            if p.is_file(): body=p.read_text(encoding='utf-8-sig').casefold()
        scores=[]
        for word in words:
            tag=ALIASES.get(word,word)
            scores.append(5*(word in title)+2*(word in meta)+1*(tag in tags)+1*(bool(body) and word in body))
        if all(scores):
            results.append((sum(scores),row))
    results.sort(key=lambda x:(-x[0],int(x[1]['id'])))
    return [dict(row,match_score=score) for score,row in results[:limit]]

def stats(rows):
    return {'unique_reports':len(rows),'severity':dict(Counter(r.get('severity') or 'unknown' for r in rows)),
            'sources':dict(Counter(s for r in rows for s in r.get('sources',[]))),
            'topics':dict(Counter(t for r in rows for t in r.get('topics',[]))),
            'markdown_available':sum(bool(r.get('markdown_file')) for r in rows)}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=DEFAULT_DATA)
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('stats')
    s=sub.add_parser('search');s.add_argument('query');s.add_argument('--severity',action='append');s.add_argument('--program');s.add_argument('--limit',type=int,default=5);s.add_argument('--reports-dir',type=Path)
    g=sub.add_parser('get');g.add_argument('id')
    b=sub.add_parser('build');b.add_argument('--metadata',required=True,type=Path);b.add_argument('--markdown-dir',type=Path);b.add_argument('--markdown-repo',type=Path);b.add_argument('--output',required=True,type=Path);b.add_argument('--marco-commit',default='main')
    c=sub.add_parser('merge-company');c.add_argument('--csv',required=True,type=Path);c.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    if args.cmd=='build': result=build(args.metadata,args.markdown_dir,args.output,args.marco_commit,args.markdown_repo)
    elif args.cmd=='merge-company':
        if args.output.resolve()==args.data.resolve():raise ValueError('Use a distinct output path to preserve the base index')
        result=merge_company(load_rows(args.data),args.csv,args.output)
    else:
        rows=load_rows(args.data)
        if args.cmd=='stats':result=stats(rows)
        elif args.cmd=='get':
            result=next((r for r in rows if r['id']==args.id),None)
            if result is None:raise ValueError('Report ID not found')
            notes=ROOT/'data'/'reviewed-cases.json'
            if notes.exists():result=dict(result,reviewed_case=read_json(notes).get(args.id))
        else:
            if not 1 <= args.limit <=100:raise ValueError('--limit must be 1..100')
            if args.reports_dir and not args.reports_dir.is_dir():raise ValueError('--reports-dir must exist')
            result=search(rows,args.query,args.severity,args.program,args.limit,args.reports_dir)
    print(json.dumps(result,ensure_ascii=True,indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,subprocess.SubprocessError) as exc:
        print(f'Error: {exc}',file=sys.stderr);sys.exit(2)
