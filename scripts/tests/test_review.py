import concurrent.futures
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

BASE = Path(__file__).resolve().parents[1] / "studio"
sys.path.insert(0, str(BASE))
from project import register
from studio import ReviewProject, serve


class ReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.video = cls.root / "frames.mp4"
        # Animated fixture differs frame to frame; compare full-resolution decoded capture.
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                        "testsrc2=size=320x180:rate=30:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(cls.video)], check=True)
        register(cls.root, "frames.mp4", "Test A", "a")
        register(cls.root, "frames.mp4", "Test B", "b")
        cls.server = serve(cls.root, 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp.cleanup()

    def request(self, path, data=None, headers=None):
        h = {"Content-Type": "application/json", "X-Review-Token": self.server.project.token}
        h.update(headers or {})
        req = urllib.request.Request(self.url + path, data=json.dumps(data).encode() if data is not None else None, headers=h)
        try:
            with urllib.request.urlopen(req) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def payload(self, key, frame=1):
        return {"request_id": key, "revision_id": "a", "start_frame": frame, "end_frame": frame + 1,
                "category": "packaging", "note": "Test feedback: frame 1 is not frame 0."}

    def test_silent_preview_has_thumbnails_without_waveform_error(self):
        status, raw = self.request('/api/cache/a')
        self.assertEqual(status, 200, raw)
        value = json.loads(raw)
        self.assertTrue(value['thumbnails'])
        self.assertEqual(value['peaks'], [])

    def test_legacy_feedback_filename_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'frames.mp4').write_bytes(self.video.read_bytes())
            register(root,'frames.mp4','Legacy','legacy')
            legacy=root/'review'/'\u5f85\u5904\u7406.md';legacy.write_text('legacy fixture')
            reopened=ReviewProject(root)
            self.assertEqual(reopened.queue_path,legacy.resolve())
            self.assertFalse((root/'review/feedback.md').exists())

    def test_exact_frame_persistence_and_snapshot(self):
        status, raw = self.request('/api/feedback', self.payload('exact-frame-0001'))
        self.assertEqual(status, 201, raw)
        data = json.loads(raw)
        self.assertEqual(data['start_frame'], 1)
        self.assertEqual(data['timecode'], '00:00:01')
        expected = self.root / 'expected.jpg'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(self.video), '-vf', 'select=eq(n\,1)',
                        '-frames:v', '1', '-q:v', '2', str(expected)], check=True)
        self.assertEqual(expected.read_bytes(), (self.root / 'review' / data['screenshot']).read_bytes())
        restored = ReviewProject(self.root)
        self.assertEqual(restored.entries[data['id']]['start_frame'], 1)
        self.assertIn('[1, 2)', (self.root / 'review/feedback.md').read_text())

    def test_range_and_identity(self):
        p = self.payload('range-0000001', 8)
        p.update(end_frame=35, region={'x': .1, 'y': .2, 'w': .5, 'h': .4})
        status, raw = self.request('/api/feedback', p)
        self.assertEqual(status, 201, raw)
        data = json.loads(raw)
        self.assertEqual(data['end_frame'], 35)
        self.assertTrue((self.root / 'review' / data['end_screenshot']).exists())
        self.assertTrue((self.root / 'review' / data['annotated_screenshot']).exists())
        self.assertEqual(len(data['video_sha256']), 64)

    def test_idempotency_and_conflict(self):
        p = self.payload('idempotent-0001', 5)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            results = list(pool.map(lambda _: self.request('/api/feedback', p), range(3)))
        ids = {json.loads(raw)['id'] for status, raw in results}
        self.assertEqual(len(ids), 1)
        entry = json.loads(results[0][1])
        change = {'id': entry['id'], 'seq': entry['seq'], 'status': 'resolved'}
        self.assertEqual(self.request('/api/feedback/update', change)[0], 200)
        self.assertEqual(self.request('/api/feedback/update', change)[0], 409)
        current = self.server.project.entries[entry['id']]
        self.assertEqual(self.request('/api/feedback/update', {**change, 'seq': current['seq'], 'status': 'open'})[0], 200)

    def test_invalid_and_cross_site_writes(self):
        self.assertEqual(self.request('/api/feedback', self.payload('bad-token-001'), {'X-Review-Token': 'wrong'})[0], 403)
        self.assertEqual(self.request('/api/feedback', self.payload('bad-origin-01'), {'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(self.request('/api/project', headers={'Host': 'evil.example'})[0], 403)
        self.assertEqual(self.request('/api/feedback', {**self.payload('bad-range-001'), 'end_frame': 1000})[0], 400)
        self.assertEqual(self.request('/api/feedback', {**self.payload('bad-frame-001'), 'start_frame': 1.5})[0], 400)
        self.assertEqual(self.request('/media/unknown/video')[0], 400)
        self.assertEqual(self.request('/%2e%2e/studio.py')[0], 400)

    def test_range_serving(self):
        status, raw = self.request('/media/a/video', headers={'Range':'bytes=100-199'})
        self.assertEqual(status, 206)
        self.assertEqual(raw, self.video.read_bytes()[100:200])

    def test_new_version_refresh(self):
        register(self.root, 'frames.mp4', 'New revision', 'new-revision')
        status, raw = self.request('/api/project')
        self.assertEqual(status, 200, raw)
        self.assertIn('new-revision', [r['id'] for r in json.loads(raw)['revisions']])
        self.assertEqual(self.request('/media/new-revision/video', headers={'Range':'bytes=0-19'})[0], 206)

    def test_comment_edit_preserves_frame_and_snapshot(self):
        status, raw = self.request('/api/feedback', self.payload('edit-comment-0001', 17))
        self.assertEqual(status, 201)
        entry = json.loads(raw)
        before = (self.root / 'review' / entry['screenshot']).read_bytes()
        status, raw = self.request('/api/feedback/update', {'id': entry['id'], 'seq': entry['seq'], 'note': 'Fix the alignment in this frame.\nKeep everything else.'})
        self.assertEqual(status, 200, raw)
        updated = json.loads(raw)
        self.assertEqual(updated['start_frame'], 17)
        self.assertEqual(updated['screenshot'], entry['screenshot'])
        self.assertEqual((self.root / 'review' / entry['screenshot']).read_bytes(), before)
        self.assertIn('Fix the alignment in this frame.', (self.root / 'review/feedback.md').read_text())

    def test_review_reads_real_project_document(self):
        source = '# Review\n\n0:01 Check the opening.\n'
        (self.root / 'REVIEW.md').write_text(source)
        status, raw = self.request('/api/review')
        self.assertEqual(status, 200, raw)
        self.assertEqual(json.loads(raw)['text'], source)
        self.assertEqual(json.loads(raw)['path'], 'REVIEW.md')

    def test_runner_endpoints_are_removed(self):
        self.assertFalse(hasattr(self.server, 'batches'))
        for path in ('/api/host', '/api/batches'):
            self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request('/api/batches', {'instructions': 'must not run'})[0], 404)
        self.assertEqual(self.request('/api/batches/action', {'action': 'stop'})[0], 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
