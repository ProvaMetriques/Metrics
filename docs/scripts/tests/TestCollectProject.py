import unittest
from collectors.CollectProject import CollectProject

class TestCollectProject(unittest.TestCase):

    def setUp(self):
        self.metrics = {}
        self.members = ['member1', 'member2'] 
        self.collector = CollectProject()
        self.maxDiff = None

    def test_unassigned_issues_count(self):
        data = {
            "project": {
                "1": {"title": "Unassigned task","assignee": None,"status": "Todo","item_type": "Issue","iteration":"Iteration 1","issue_type": "Task"},
            },
            "iterations": [
                {"id": "1","title": "Iteration 1","startDate": "2025-02-01","duration": 7},
            ],
            "statuses": ["Todo", "In Progress", "Done"],
        }
        result = self.collector.execute(data, self.metrics, self.members)
        self.assertEqual(result["project"]["metrics_by_iteration"]["Iteration 1"]["assigned_per_member"]["non_assigned"], 1)
        self.assertEqual(result["project"]["metrics_by_iteration"]["total"]["assigned_per_member"]["non_assigned"], 1)
        self.assertTrue(result["project"]["has_iterations"])

    def test_in_progress_tasks_per_member(self):
        data = {
            "project": {
                "1": {"title": "Task in progress","assignee": "member1","status": "In Progress","item_type": "Issue","iteration":"Iteration A","issue_type": "Task"},
            },
            "iterations": [
                {"id": "A","title": "Iteration A","startDate": "2025-01-01","duration": 7},
            ],
            "statuses": ["Todo", "In Progress", "Done"],
        }
        result = self.collector.execute(data, self.metrics, self.members)
        self.assertEqual(result["project"]["metrics_by_iteration"]["Iteration A"]["in_progress_per_member"]["member1"], 1)


    def test_bugs_features_tasks_count(self):
        data = {
            "project": {
                "1": {"title": "Feature 1", "assignee": "member1", "status": "Todo", "item_type": "Issue", "iteration": None, "issue_type": "Feature"},
                "2": {"title": "Bug 1", "assignee": "member2", "status": "In Progress", "item_type": "Issue", "iteration": None, "issue_type": "Bug"},
                "3": {"title": "Task 1", "assignee": None, "status": "Done", "item_type": "Issue", "iteration": None, "issue_type": "Task"},
            },
            "iterations": [],
            "statuses": ["Todo", "In Progress", "Done"],
        }
        result = self.collector.execute(data, self.metrics, self.members)
        metrics = result["project"]["metrics_by_iteration"]["no_iteration"]
        self.assertEqual(metrics["total_features"], 1)
        self.assertEqual(metrics["total_bugs"], 1)
        self.assertEqual(metrics["total_tasks"], 1)
        self.assertEqual(metrics["total_issues_with_type"], 3)
        self.assertEqual(metrics["total"], 3)

    def test_multiple_iterations_with_tasks(self):
        data = {
            "project": {
                "1": {"title": "Task Iter 1", "assignee": "member1", "status": "Todo", "item_type": "Issue", "iteration": "Sprint 1", "issue_type": "Task"},
                "2": {"title": "Bug Iter 2", "assignee": "member2", "status": "In Progress", "item_type": "Issue", "iteration": "Sprint 2", "issue_type": "Bug"},
                "3": {"title": "Feature Iter 1", "assignee": None, "status": "Done", "item_type": "Issue", "iteration": "Sprint 1", "issue_type": "Feature"},
            },
            "iterations": [
                {"id": "1", "title": "Sprint 1", "startDate": "2025-04-01", "duration": 7},
                {"id": "2", "title": "Sprint 2", "startDate": "2025-04-08", "duration": 7},
            ],
            "statuses": ["Todo", "In Progress", "Done"],
        }
        result = self.collector.execute(data, self.metrics, self.members)

        sprint1 = result["project"]["metrics_by_iteration"]["Sprint 1"]
        self.assertEqual(sprint1["total_tasks"], 1)
        self.assertEqual(sprint1["total_features"], 1)
        self.assertEqual(sprint1["total_bugs"], 0)
        self.assertEqual(sprint1["total"], 2)

        sprint2 = result["project"]["metrics_by_iteration"]["Sprint 2"]
        self.assertEqual(sprint2["total_tasks"], 0)
        self.assertEqual(sprint2["total_features"], 0)
        self.assertEqual(sprint2["total_bugs"], 1)
        self.assertEqual(sprint2["total"], 1)

        total = result["project"]["metrics_by_iteration"]["total"]
        self.assertEqual(total["total_tasks"], 1)
        self.assertEqual(total["total_features"], 1)
        self.assertEqual(total["total_bugs"], 1)
        self.assertEqual(total["total"], 3)

    def test_no_iterations(self):
        data = {
            "project": {
                "1": {"title": "No iteration","assignee": "member2","status": "Todo","item_type": "Issue","iteration": None,"issue_type": "Task"},
            },
            "iterations": [],
            "statuses": ["Todo", "In Progress", "Done"],
        }
        result = self.collector.execute(data, self.metrics, self.members)
        self.assertFalse(result["project"]["has_iterations"])
        self.assertFalse(result["project"]["iterations"])


    def test_iteration_end_date_calculation(self):
        data = {
            "project": {},
            "iterations": [
                {"id": "1","title": "Iteration 1","startDate": "2025-03-01","duration": 5},
            ],
            "statuses": [],
        }
        result = self.collector.execute(data, self.metrics, self.members)
        self.assertTrue(result["project"]["has_iterations"])
        self.assertEqual(len(result["project"]["iterations"]), 1)
        self.assertEqual(result["project"]["iterations"]["Iteration 1"]["endDate"], "2025-03-05")

    def test_draft_issue_excluded_from_issue_with_type(self):
        data = {
            "project": {
                "1": {"title": "Draft item","assignee": "member1","status": "Todo","item_type": "DraftIssue","iteration": None,"issue_type:": None},
            },
            "iterations": [],
            "statuses": ["Todo", "In Progress", "Done"],
        }
        result = self.collector.execute(data, self.metrics, self.members)
        metrics = result["project"]["metrics_by_iteration"]["no_iteration"]
        self.assertEqual(metrics["total_issues_with_type"], 0)
        self.assertEqual(metrics["total"], 1)

    def test_issue_without_issue_type(self):
        data = {
            "project": {
                "1": {"title": "Untyped issue","assignee": "member2","status": "In Progress","item_type": "Issue","iteration": None,"issue_type": None},
            },
            "iterations": [],
            "statuses": ["Todo", "In Progress", "Done"],
        }
        result = self.collector.execute(data, self.metrics, self.members)
        metrics = result["project"]["metrics_by_iteration"]["no_iteration"]
        self.assertEqual(metrics["total_tasks"], 0)
        self.assertEqual(metrics["total_features"], 0)
        self.assertEqual(metrics["total_bugs"], 0)
        self.assertEqual(metrics["total_issues_with_type"], 0)
        self.assertEqual(metrics["total"], 1)

    def test_tasks_status(self):
        data = {
            "project": {
                "1": {"title": "Tarea 1", "assignee": "member1","status": "Todo", "item_type": "Issue","iteration": None,"issue_type": "Task"},
                "2": {"title": "Tarea 2", "assignee": "member1","status": "In Progress", "item_type": "Issue","iteration": None,"issue_type": "Task"},
                "3": {"title": "Tarea 3", "assignee": "member1","status": "In Progress", "item_type": "Issue","iteration": None,"issue_type": "Task"},
                "4": {"title": "Tarea 4", "assignee": "member2","status": "Done", "item_type": "Issue","iteration": None,"issue_type": "Task"},
                "5": {"title": "Tarea 5", "assignee": None, "status": "Todo", "item_type": "Issue","iteration": None,"issue_type": "Task"},
            },
            "iterations": [],
            "statuses": ["Todo", "In Progress", "Done"],
        }
        result = self.collector.execute(data, self.metrics, self.members)
        metrics = result["project"]["metrics_by_iteration"]["no_iteration"]
        self.assertEqual(metrics["todo"], 2)
        self.assertEqual(metrics["in_progress"], 2)
        self.assertEqual(metrics["done"], 1)
        self.assertEqual(metrics["total_tasks"],5)
    
    def test_custom_status(self):
        data = {
            "project": {
                "1": {"title": "Task 1", "status": "In Review", "item_type": "Issue", "assignee": "member1","iteration": None,"issue_type": "Task"},
                "2": {"title": "Task 2", "status": "Todo", "item_type": "Issue", "assignee": "member2","iteration": None,"issue_type": "Task"},
                "3": {"title": "Feature 1", "status": "In Review", "item_type": "Issue", "assignee": "member2","iteration": None,"issue_type": "Feature"},
            },
            "iterations": [],
            "statuses": ["Todo", "In Progress", "Done", "In Review"],
        }
        result = self.collector.execute(data, self.metrics, self.members)
        metrics = result["project"]["metrics_by_iteration"]["no_iteration"]

        self.assertIn("in_review", metrics)
        self.assertEqual(metrics["in_review"], 1)  
        self.assertEqual(metrics["total_features_in_review"], 1)
        self.assertEqual(metrics["total_features"], 1)
        self.assertEqual(metrics["total_tasks"], 2)        
        self.assertEqual(metrics["todo"], 1)       
        self.assertEqual(metrics["total"], 3)   
