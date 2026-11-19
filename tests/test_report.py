import unittest
from src.report import aggregate


class ReportTests(unittest.TestCase):
    def test_month_filter(self):
        rows = [
            {"site_id": "A", "date": "2026-10-01", "energy_kwh": 4},
            {"site_id": "A", "date": "2026-11-01", "energy_kwh": 6},
        ]
        self.assertEqual(aggregate(rows, "2026-10")[0]["energy_kwh"], 4)


if __name__ == "__main__":
    unittest.main()
