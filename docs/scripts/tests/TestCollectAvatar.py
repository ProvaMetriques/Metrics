import unittest
from collectors.CollectAvatar import CollectAvatar

class TestCollectAvatar(unittest.TestCase):

    def setUp(self):

        self.metrics = {}
        self.members = ['member1', 'member2'] 
        self.collector = CollectAvatar()

    def test_general_avatar(self):

        data = {
            "members_images": {
                "member1": "https://avatars.githubusercontent.com/u/324424322?v=4",
                "member2": "https://avatars.githubusercontent.com/u/234243243?v=4"
            },
        }

        result = self.collector.execute(data, self.metrics, self.members)
        
        expected_result = {
                "avatars": {
                    "member1": "https://avatars.githubusercontent.com/u/324424322?v=4",
                    "member2": "https://avatars.githubusercontent.com/u/234243243?v=4"
                },
        }
        
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
