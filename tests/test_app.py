import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from app import create_app, summarize, status

class AppTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = self.directory.name + '/test.sqlite3'
        self.app = create_app(self.path)
        self.client = self.app.test_client()
    def tearDown(self):
        self.directory.cleanup()
    def post(self, level, i=0):
        return self.client.post('/api/readings', json=dict(sensorId='CREEK-01', waterLevelCm=level, timestamp=f'2026-10-17T00:{i//60:02}:{i%60:02}+00:00'))
    def test_validation(self):
        for level in (None, '100', True, -1, 501, float('nan'), float('inf')):
            self.assertEqual(self.post(level).status_code, 400)
        for data in ({}, [], {'waterLevelCm':10}, {'sensorId':' ', 'waterLevelCm':10}, {'sensorId':'x','waterLevelCm':5,'timestamp':'bad'}):
            self.assertEqual(self.client.post('/api/readings',json=data).status_code,400)
        self.assertEqual(self.client.post('/api/readings',data='{',content_type='application/json').status_code,400)
        self.assertEqual(self.post(0).status_code,201)
        self.assertEqual(self.post(500).status_code,201)
    def test_persistence_order_and_limit(self):
        for i in range(55): self.post(i,i)
        rows=create_app(self.path).test_client().get('/api/readings').json
        self.assertEqual(len(rows),50)
        self.assertEqual(rows[0]['waterLevelCm'],54)
        self.assertEqual(rows[-1]['waterLevelCm'],5)
        summary=self.client.get('/api/summary').json
        self.assertEqual(summary['count'],55)
        self.assertEqual(summary['average'],27)
        self.assertEqual(summary['trend'],'rising')
    def test_boundaries_and_summary(self):
        self.assertEqual([status(x) for x in (99.9,100,149.9,150)],['Normal','Alert','Alert','Danger'])
        rows=[dict(waterLevelCm=v,timestamp=str(i)) for i,v in enumerate([0,50,99,100,149,150,200,250,300,500])]
        s=summarize(rows)
        self.assertEqual((s['normal'],s['alert'],s['danger']),(3,2,5))
        self.assertEqual(s['average'],179.8)
        self.assertEqual((s['minimum'],s['maximum']),(0,500))
        self.assertEqual(summarize([])['trend'],'insufficient data')
        self.assertEqual(summarize([dict(waterLevelCm=80,timestamp=str(i)) for i in range(10)])['trend'],'steady')
    def test_advisory(self):
        self.post(170)
        with patch.dict(os.environ,{'GEMINI_API_KEY':''}):
            r=self.client.post('/api/advisory').json
            self.assertEqual(r['source'],'Rule-based fallback')
            self.assertIn('Danger',r['english'])
            self.assertTrue(r['filipino'])
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test-only'}),patch('app.urlopen',side_effect=TimeoutError):
            self.assertEqual(self.client.post('/api/advisory').json['source'],'Rule-based fallback')
        payload={'candidates':[{'content':{'parts':[{'text':json.dumps({'english':'Test English.','filipino':'Test Filipino.'})}]}}]}
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test-only'}),patch('app.urlopen',return_value=io.BytesIO(json.dumps(payload).encode())):
            self.assertEqual(self.client.post('/api/advisory').json['english'],'Test English.')
    def test_dashboard_assets(self):
        for url in ('/','/static/app.js','/static/style.css','/health'):
            response=self.client.get(url)
            self.assertEqual(response.status_code,200)
            response.close()

if __name__ == '__main__': unittest.main()
