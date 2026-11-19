"""Smoke checks for the combined production dashboard and prediction API."""
import math
from pathlib import Path
import unittest

from fastapi.testclient import TestClient

from deploy_server import app


class DeploymentSmokeTests(unittest.TestCase):
    """Verify built assets, client routing and bundled model inference."""

    @classmethod
    def setUpClass(cls):
        if not Path("static/index.html").is_file():
            raise RuntimeError("Build the frontend and copy frontend/dist into static first")
        cls.client = TestClient(app)

    def test_dashboard_and_deep_links(self):
        for path in ("/", "/fleet", "/engine", "/performance", "/predict"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn('id="root"', response.text)

    def test_built_assets(self):
        assets = list(Path("static/assets").glob("*"))
        self.assertTrue(assets)
        for asset in assets:
            with self.subTest(asset=asset.name):
                self.assertEqual(self.client.get("/assets/" + asset.name).status_code, 200)

    def test_api_docs(self):
        self.assertEqual(self.client.get("/docs").status_code, 200)

    def test_model_health(self):
        response = self.client.get("/api/model/status")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["model_exists"])

    def test_unknown_api_is_not_spa(self):
        response = self.client.get("/api/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Not found"})

    def test_bundled_model_predictions(self):
        response = self.client.get("/api/predictions?dataset=FD001&window=30")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertGreater(result["total_engines"], 0)
        self.assertEqual(len(result["fleet"]), result["total_engines"])
        self.assertTrue(math.isfinite(result["rmse"]))
        self.assertTrue(all(math.isfinite(item["predicted_rul"]) for item in result["fleet"]))


if __name__ == "__main__":
    unittest.main()
