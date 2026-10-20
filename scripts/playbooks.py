#!/usr/bin/env python3
"""Retrieve local Redhood test cards. Creates plans, not testing results. No network."""
import argparse
import json
from pathlib import Path
import re
import sys

DATA = Path(__file__).resolve().parents[1]/'data'/'test-cards.json'
FIELDS = {'id','title','prerequisites','invariant','test','oracle','false_positive','stop','reference','source_url'}

def load_cards(path=DATA):
    cards = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(cards,list) or not cards:
        raise ValueError('Expected a nonempty card list')
    ids = set()
    for card in cards:
        if not isinstance(card,dict) or not FIELDS.issubset(card):
            raise ValueError('Incomplete card')
        if not all(isinstance(card[k],str) and card[k].strip() for k in FIELDS):
            raise ValueError('Empty card field')
        if not re.fullmatch(r'RH-\d{2}',card['id']) or card['id'] in ids:
            raise ValueError('Invalid or duplicate card ID')
        ids.add(card['id'])
    return cards

def search(cards, query):
    words = re.findall(r'[\w-]+',query.casefold())
    if not words:return []
    scored = []
    for card in cards:
        title = card['title'].casefold()
        body = ' '.join(card[k] for k in FIELDS).casefold()
        scores = [3*int(word in title)+int(word in body) for word in words]
        if all(scores):scored.append((sum(scores),card))
    return [c for _,c in sorted(scored,key=lambda x:(-x[0],x[1]['id']))]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('list')
    s=sub.add_parser('search');s.add_argument('query')
    s=sub.add_parser('show');s.add_argument('id')
    cards=load_cards();args=p.parse_args()
    if args.command=='list':result=[{'id':c['id'],'title':c['title']} for c in cards]
    elif args.command=='search':result=search(cards,args.query)
    else:
        result=next((c for c in cards if c['id']==args.id.upper()),None)
        if result is None:raise ValueError('Unknown card ID')
    print(json.dumps(result,ensure_ascii=True,indent=2))

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(f'Error: {exc}',file=sys.stderr);sys.exit(2)
