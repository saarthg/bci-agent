import unittest
# from unittest.mock import patch
from app import execute_query
from smartHomeAgent import tracked_calls  # Import the tracked_calls list

class TestSmartHomeAgent(unittest.TestCase):
    def test_query_execution(self):
        # Clear the tracked calls before running each test
        tracked_calls.clear()

        # Define test cases
        test_cases = [
            {
                "query": "Turn on the AC and set the thermostat to 72 degrees",
                "expected_calls": [
                    ('turn_on_ac', ()),
                    ('set_thermostat', ('72',)),
                ],
            },
            {
                "query": "Close the curtains.",
                "expected_calls": [
                    ('adjust_curtains', ('close',)),
                ],
            },
            {
                "query": "Lock the doors and turn off the AC",
                "expected_calls": [
                    ('manage_locks', ('lock',)),
                    ('turn_off_ac', ()),
                ],
            },
            {
                "query": "Turn on the lights.",
                "expected_calls": [
                    ('turn_on_lights', ()),
                ],
            },
            {
                "query": "Start the washing machine.",
                "expected_calls": [
                    ('start_appliance', ('washing machine',)),
                ],
            },
            {
                "query": "Arm the security system.",
                "expected_calls": [
                    ('manage_security', ('arm',)),
                ],
            },
            {
                "query": "Stop the dishwasher.",
                "expected_calls": [
                    ('stop_appliance', ('dishwasher',)),
                ],
            },
            {
                "query": "Unlock the doors.",
                "expected_calls": [
                    ('manage_locks', ('unlock',)),
                ],
            },
            {
                "query": "Answer the video doorbell.",
                "expected_calls": [
                    ('answer_video_doorbell', ()),
                ],
            },
            {
                "query": "Turn on the TV.",
                "expected_calls": [
                    ('control_entertainment_device', ('TV', 'on')),
                ],
            },
        ]

        test_cases += [
            {
                "query": "Search for the 'Grades' file",
                "expected_calls": [
                    ('search_files', ('Grades',)),
                ],
            },
            {
                "query": "Navigate to the settings menu.",
                "expected_calls": [
                    ('navigate_links_or_menus', ('settings',)),
                ],
            },
            {
                "query": "Enable multi-app navigation.",
                "expected_calls": [
                    ('enable_navigation_and_multiapp', ()),
                ],
            },
        ]


        total_tests = 0
        correct_tests = 0

        # Iterate over each test case
        for case in test_cases:
            with self.subTest(case=case):
                # Execute the query
                user_query = case["query"]
                execute_query(user_query)

                # Check for the expected calls
                total_tests += len(case["expected_calls"])
                correct_tests_case = 0

                for expected_func, expected_args in case["expected_calls"]:
                    # Check if the function was called with the expected arguments
                    self.assertIn((expected_func, expected_args), tracked_calls)
                    if (expected_func, expected_args) in tracked_calls:
                        correct_tests_case += 1
                
                correct_tests += correct_tests_case
            
            tracked_calls.clear()

        # Calculate accuracy
        accuracy = (correct_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    unittest.main()
