import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from analysis_service import Analysis


class ReviewFlowTests(unittest.TestCase):
    def test_review_persists_and_resets_for_new_analysis(self):
        result = Analysis("Failure", "Cause", "Emotion", "Response", 4,
                          {"failure_point": [], "root_cause": [], "customer_emotion": []}, ["Follow up"])
        with patch("analysis_service.analyze_conversation", return_value=result):
            app = AppTest.from_file("../app.py").run()
            app.text_area[0].set_value("A transcript").run()
            app.button[3].click().run()
            app.selectbox[0].select("Needs correction").run()
            app.text_area[1].set_value("The cause needs review").run()
            self.assertEqual(app.selectbox[0].value, "Needs correction")
            self.assertEqual(app.text_area[1].value, "The cause needs review")
            app.button[3].click().run()
            self.assertEqual(app.selectbox[0].value, "Not reviewed")
            self.assertEqual(app.text_area[1].value, "")
            self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
