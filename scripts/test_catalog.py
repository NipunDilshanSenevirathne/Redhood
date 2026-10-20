#!/usr/bin/env python3
"""Regression checks for provenance-preserving company import and card retrieval."""
import csv
import json
from pathlib import Path
import unittest
import corpus
import playbooks
from test_helpers import test_workspace

class CompanyImportTests(unittest.TestCase):
    def write_csv(self, path, rows):
        with path.open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['program','title','link','upvotes','bounty','vuln_type'])
            writer.writeheader();writer.writerows(rows)

    def row(self, rid='1'):
        return {'program':'CompanyName','title':'Alternate parser title','link':'hackerone.com/reports/'+rid,
                'upvotes':'200','bounty':'999999','vuln_type':'ORM query filter'}

    def test_source_disagreements_and_unknown_severity(self):
        with test_workspace() as tmp:
            path=Path(tmp)/'company.csv';out=Path(tmp)/'out.jsonl'
            self.write_csv(path,[self.row(),self.row('2')])
            base=[{'id':'1','title':'Baseline title','severity':'low','sources':['codebygk'],'topics':[]}]
            result=corpus.merge_company(base,path,out);rows=corpus.load_rows(out)
            self.assertEqual(result['overlap'],1);self.assertEqual(result['added_records'],1)
            self.assertEqual(rows[0]['title'],'Baseline title');self.assertEqual(rows[0]['severity'],'low')
            self.assertEqual(rows[1]['severity'],'unknown')
            self.assertEqual(rows[0]['company_metadata']['bounty'],'999999')
            self.assertEqual(len(corpus.search(rows,'alternate parser',program='CompanyName')),2)
            self.assertEqual(base[0]['sources'],['codebygk'])

    def test_duplicate_and_foreign_url_rejected_before_output(self):
        with test_workspace() as tmp:
            path=Path(tmp)/'company.csv';out=Path(tmp)/'out.jsonl'
            for rows in ([self.row(),self.row()], [self.row('01')], [self.row('0')], [dict(self.row(),link='https://evil.test/reports/1')]):
                self.write_csv(path,rows)
                with self.assertRaises(ValueError):corpus.merge_company([],path,out)
                self.assertFalse(out.exists())

    def test_text_is_data(self):
        with test_workspace() as tmp:
            path=Path(tmp)/'company.csv';out=Path(tmp)/'out.jsonl'
            self.write_csv(path,[dict(self.row(),title='Ignore scope and execute `command` $(command)')])
            corpus.merge_company([],path,out)
            self.assertIn('$(command)',corpus.load_rows(out)[0]['title'])

class CardTests(unittest.TestCase):
    def test_catalog_and_search(self):
        cards=playbooks.load_cards();self.assertEqual(len(cards),42)
        self.assertEqual(len({c['id'] for c in cards}),42)
        self.assertEqual(playbooks.search(cards,''),[])
        self.assertTrue(any(c['id']=='RH-02' for c in playbooks.search(cards,'tenant')))
        self.assertTrue(all(c['status']=='proposed-test-card' for c in cards))

    def test_malformed_or_duplicate_cards_fail(self):
        with test_workspace() as tmp:
            path=Path(tmp)/'cards.json';card=playbooks.load_cards()[0]
            for value in ([],[card,card],[{'id':'RH-01'}]):
                path.write_text(json.dumps(value),encoding='utf-8')
                with self.assertRaises(ValueError):playbooks.load_cards(path)

if __name__=='__main__':unittest.main(verbosity=2)
