import unittest

from scripts.hindi_text_check import check_text


class HindiTextCheckTests(unittest.TestCase):
    def test_accepts_correct_conjuncts(self):
        self.assertEqual(
            check_text("$", "एक चित्रकथा में बाल हनुमान मूर्च्छित हुए।"),
            [],
        )

    def test_rejects_nonstandard_spelling(self):
        issues = check_text("$", "बाल हनुमान मूर्छित हुए।")
        self.assertEqual(issues[0]["category"], "spelling")
        self.assertIn("मूर्च्छित", issues[0]["suggested"])

    def test_rejects_detached_matra(self):
        issues = check_text("$", "शब्द  ि")
        self.assertTrue(any(issue["category"] == "matra" for issue in issues))

    def test_rejects_mojibake(self):
        issues = check_text("$", "हिंदी à¤")
        self.assertTrue(any(issue["category"] == "unicode" for issue in issues))


if __name__ == "__main__":
    unittest.main()
