import unittest
from collectors.CollectIssues import CollectIssues

class TestCollectIssues(unittest.TestCase):

    def setUp(self):

        self.metrics = {}
        self.members = ['member1', 'member2'] 
        self.collector = CollectIssues()

    def test_general_issues(self):

        data = {
            'issues': {
                "1": {'state': 'CLOSED', 'assignee': 'member1', 'has_pull_request': True, 'pr_author_is_assignee': True},
                "2": {'state': 'OPEN', 'assignee': 'member2', 'has_pull_request': False, 'pr_author_is_assignee': False},
                "3": {'state': 'CLOSED', 'assignee': None, 'has_pull_request': False, 'pr_author_is_assignee': False},
                "4": {'state': 'CLOSED', 'assignee': 'member1', 'has_pull_request': True, 'pr_author_is_assignee': False},
            }
        }

        result = self.collector.execute(data, self.metrics, self.members)
        
        expected_result = {
            'issues': {
                'assigned': {'member1': 2, 'member2': 1, 'non_assigned': 1},
                'closed': {'member1': 2, 'member2': 0},
                'have_pull_request': 2,
                'assignee_is_pr_author': 1,
                'total_closed': 3,
                'total': 4
            }
        }
        
        self.assertEqual(result, expected_result)

    def test_non_assigned(self):

        data = {
            'issues': {
                "1": {'state': 'OPEN', 'assignee': None, 'has_pull_request': False, 'pr_author_is_assignee': False},
                "2": {'state': 'CLOSED', 'assignee': None, 'has_pull_request': False, 'pr_author_is_assignee': False},

            }
        }

        result = self.collector.execute(data, self.metrics, self.members)
        
        expected_result = {
            'issues': {
                'assigned': {'member1': 0, 'member2': 0, 'non_assigned': 2},
                'closed': {'member1': 0, 'member2': 0},
                'have_pull_request': 0,
                'assignee_is_pr_author': 0,
                'total_closed': 1,
                'total': 2
            }
        }
        
        self.assertEqual(result, expected_result)

    def test_has_pull_request(self):

        data = {
            'issues': {
                "1": {'state': 'OPEN', 'assignee': 'member1', 'has_pull_request': True, 'pr_author_is_assignee': True},
                "2": {'state': 'CLOSED', 'assignee': 'member1', 'has_pull_request': True, 'pr_author_is_assignee': True},
                "3": {'state': 'CLOSED', 'assignee': 'member1', 'has_pull_request': False, 'pr_author_is_assignee': False},
                "4": {'state': 'CLOSED', 'assignee': 'member1', 'has_pull_request': True, 'pr_author_is_assignee': False},
            }
        }

        result = self.collector.execute(data, self.metrics, self.members)
        
        expected_result = {
            'issues': {
                'assigned': {'member1': 4, 'member2': 0, 'non_assigned': 0},
                'closed': {'member1': 3, 'member2': 0},
                'have_pull_request': 2,
                'assignee_is_pr_author': 1,
                'total_closed': 3,
                'total': 4
            }
        }
        
        self.assertEqual(result, expected_result)

    def test_pr_author_is_assignee(self):
        data = {
            'issues': {
                "1": {'state': 'OPEN', 'assignee': 'member1', 'has_pull_request': True, 'pr_author_is_assignee': True},
                "2": {'state': 'CLOSED', 'assignee': 'member1', 'has_pull_request': True, 'pr_author_is_assignee': True},
                "3": {'state': 'CLOSED', 'assignee': 'member1', 'has_pull_request': False, 'pr_author_is_assignee': False},
                "4": {'state': 'CLOSED', 'assignee': 'member1', 'has_pull_request': True, 'pr_author_is_assignee': False},
            }
        }

        result = self.collector.execute(data, self.metrics, self.members)
        
        expected_result = {
            'issues': {
                'assigned': {'member1': 4, 'member2': 0, 'non_assigned': 0},
                'closed': {'member1': 3, 'member2': 0},
                'have_pull_request': 2,
                'assignee_is_pr_author': 1,
                'total_closed': 3,
                'total': 4
            }
        }
        
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
