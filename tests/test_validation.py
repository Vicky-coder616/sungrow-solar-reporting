import os
import unittest
from unittest.mock import Mock, patch
import requests
from src.report import aggregate
from src.fetch_live import fetch_raw


class ValidationTests(unittest.TestCase):
    def row(self, **values):
        return {"site_id": "DEMO-1", "date": "2026-10-01", "energy_kwh": 2, **values}

    def test_aggregation_and_outside_month(self):
        rows = [
            self.row(),
            self.row(date="2026-10-02", energy_kwh=3),
            self.row(date="2026-11-01"),
        ]
        self.assertEqual(aggregate(rows, "2026-10")[0]["energy_kwh"], 5)

    def test_nonfinite_negative_boolean_and_missing_values(self):
        for value in ("NaN", "inf", -1, True, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                aggregate([self.row(energy_kwh=value)], "2026-10")

    def test_dates_site_and_month_validation(self):
        for row in (
            self.row(date="2026-02-30"),
            self.row(site_id="=formula"),
            self.row(site_id=""),
            {},
        ):
            with self.subTest(row=row), self.assertRaises(ValueError):
                aggregate([row], "2026-10")
        for month in ("2026-99", "2026-1", "invalid"):
            with self.subTest(month=month), self.assertRaises(ValueError):
                aggregate([], month)

    def test_duplicates_rejected_even_outside_month(self):
        with self.assertRaises(ValueError):
            aggregate([self.row(), self.row()], "2026-11")

    @patch.dict(
        os.environ,
        {
            "SUNGROW_API_URL": "https://example.invalid/readings",
            "SUNGROW_API_TOKEN": "synthetic-token",
        },
        clear=True,
    )
    def test_http_adapter_mock_and_redacted_error(self):
        http = Mock()
        http.get.return_value.status_code = 200
        http.get.return_value.json.return_value = {"demo": True}
        self.assertEqual(fetch_raw(http), {"demo": True})
        self.assertEqual(http.get.call_args.kwargs["timeout"], 30)
        http.get.side_effect = requests.Timeout("synthetic-token")
        with self.assertRaises(RuntimeError) as caught:
            fetch_raw(http)
        self.assertNotIn("synthetic-token", str(caught.exception))

    @patch.dict(
        os.environ,
        {
            "SUNGROW_API_URL": "http://example.invalid",
            "SUNGROW_API_TOKEN": "synthetic-token",
        },
        clear=True,
    )
    def test_http_refused_before_request(self):
        http = Mock()
        with self.assertRaises(ValueError):
            fetch_raw(http)
        http.get.assert_not_called()
