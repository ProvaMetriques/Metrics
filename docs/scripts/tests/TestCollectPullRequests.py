import unittest
from collectors.CollectPullRequests import CollectPullRequests

class TestCollectPullRequests(unittest.TestCase):

    def setUp(self):

        self.metrics = {}
        self.members = ['member1', 'member2'] 
        self.collector = CollectPullRequests()

    def test_general_pull_requests(self):

        data = {
            "pull_requests": {
                "1": {"state": "MERGED", "author": "member1", "merged": True, "merged_by": "member1"},
                "2": {"state": "CLOSED", "author": "member1", "merged": False, "merged_by": None},
                "3": {"state": "OPEN", "author": "member2", "merged": False, "merged_by": None},
            }

        }

        result = self.collector.execute(data, self.metrics, self.members)
        
        expected_result = {
            "pull_requests": {
                "created": {
                    "member1": 2,
                    "member2": 1
                },
                "merged_per_member": {
                    "member1": 1,
                    "member2": 0
                },
                "merged": 1,
                "not_merged_by_author": 0,
                "closed": 1,
                "total": 3
            },
        }
        
        self.assertEqual(result, expected_result)

    def test_pr_merged_by_other_member(self):
        data = {
            "pull_requests": {
                "1": {"state": "MERGED", "author": "member1", "merged": True, "merged_by": "member2"},
                "2": {"state": "MERGED", "author": "member2", "merged": True, "merged_by": "member2"},
            }
        }
        result = self.collector.execute(data, self.metrics, self.members)
        self.assertEqual(result["pull_requests"]["merged"], 2)
        self.assertEqual(result["pull_requests"]["merged_per_member"]["member1"], 0)
        self.assertEqual(result["pull_requests"]["merged_per_member"]["member2"], 2)
        self.assertEqual(result["pull_requests"]["not_merged_by_author"], 1)
        self.assertEqual(result["pull_requests"]["total"], 2)


if __name__ == '__main__':
    unittest.main()
