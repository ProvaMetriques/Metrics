import unittest
from collectors.CollectCommits import CollectCommits
from unittest.mock import patch
from datetime import datetime, timezone
import datetime as real_datetime

class TestCollectCommitsMetrics(unittest.TestCase):

    def setUp(self):

        self.metrics = {}
        self.members = ['member1', 'member2'] 
        self.collector = CollectCommits()
        
    def test_general_commits(self):
        data = {
            "commits": {
                "1": {"author": "member1", "additions": 100, "deletions": 20, "modified": 120, "date": "2025-04-23", "merge": False},
                "2": {"author": "member2", "additions": 120, "deletions": 50, "modified": 170, "date": "2025-04-23", "merge": False}
            }
        }

        result = self.collector.execute(data, self.metrics, self.members)
        
        expected_result = {
            'commits': 
            {
                'member1': 1,
                'member2': 1,
                'anonymous': 0,
                'total': 2
            }, 
            'modified_lines': 
            {
                'member1': 
                {
                    'additions': 100,
                    'deletions': 20, 
                    'modified': 120
                },
                'member2': 
                {
                    'additions': 120, 
                    'deletions': 50, 
                    'modified': 170
                }, 
                'total': 
                {
                    'additions': 220, 
                    'deletions': 70, 
                    'modified': 290
                }
            }, 
            'commit_streak':
            {
                'member1': 0, 
                'member2': 0
            }, 
            'commit_merges': 0,
            'longest_commit_streak_per_user': 
            {
                'member1': 0, 
                'member2': 0
            }
        }
        self.assertEqual(result, expected_result)

    def test_merge_commits(self):
        data = {
            "commits" : {
            "1": {"author": "member1", "additions": 100, "deletions": 20, "modified": 120, "date": "2025-04-23", "merge": True},
            "2": {"author": "member2", "additions": 120, "deletions": 50, "modified": 170, "date": "2025-04-23", "merge": False}
            }
        }

        result = self.collector.execute(data, self.metrics, self.members)
        expected_result = {}
        expected_result['commit_merges'] = 1
        self.assertEqual(result['commit_merges'], expected_result['commit_merges'])

    @patch('collectors.CollectCommits.datetime') 
    def test_commit_streak(self, mock_datetime):
        mock_datetime.strptime = real_datetime.datetime.strptime
        mock_datetime.now.return_value = datetime(2025, 4, 22, 1, 1, 1, tzinfo=timezone.utc)

        data = {
            "commits": {
                "1": {"author": "member1", "additions": 100, "deletions": 20, "modified": 120, "date": "2025-04-20", "merge": False},
                "2": {"author": "member1", "additions": 100, "deletions": 20, "modified": 120, "date": "2025-04-21", "merge": False},
                "3": {"author": "member1", "additions": 100, "deletions": 20, "modified": 120, "date": "2025-04-22", "merge": False},
                "4": {"author": "member2", "additions": 100, "deletions": 20, "modified": 120, "date": "2025-04-20", "merge": False},
                "5": {"author": "member2", "additions": 100, "deletions": 20, "modified": 120, "date": "2025-04-22", "merge": False}
            }
        }

        result = self.collector.execute(data, self.metrics, self.members)

        commit_streaks = result['commit_streak']
        expected_result = {}
        expected_result['commit_streaks'] = {}
        expected_result['commit_streaks']['member1'] = 3
        expected_result['commit_streaks']['member2'] = 1

        self.assertEqual(result['commit_streak']['member1'], expected_result['commit_streaks']['member1'])

        self.assertEqual(result['commit_streak']['member2'], expected_result['commit_streaks']['member2'])

if __name__ == '__main__':
    unittest.main()
