import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile, score_prospect


class ProspectInfoTest(unittest.TestCase):
    def test_update_refreshes_profile_and_score_input(self):
        prospect_id = "LEAD-39002"
        original_record = data_service.PROSPECTS[prospect_id]
        original_tech_stack = list(original_record["tech_stack"])
        original_profile = data_service._PROFILES.pop(prospect_id, None)

        try:
            profile = build_prospect_profile.func(prospect_id)["prospect_profile"]
            self.assertNotIn("Kafka", profile["tech_stack"])

            data_service.update_prospect_info(prospect_id, "Kafka")
            refreshed = build_prospect_profile.func(prospect_id)["prospect_profile"]

            self.assertIn("Kafka", refreshed["tech_stack"])

            captured = {}

            def invoke(messages):
                captured["prospect"] = json.loads(messages[1]["content"].split(
                    "\n\nProspect profile:\n", 1
                )[1])
                return SimpleNamespace(model_dump=lambda: {"score": 1})

            with patch("gtm_agent.gtm_agent._scoring_llm", SimpleNamespace(invoke=invoke)):
                score_prospect.func(refreshed, data_service.OFFERINGS["OFFER-10001"])

            self.assertIn("Kafka", captured["prospect"]["tech_stack"])
        finally:
            original_record["tech_stack"] = original_tech_stack
            if original_profile is None:
                data_service._PROFILES.pop(prospect_id, None)
            else:
                data_service._PROFILES[prospect_id] = original_profile


if __name__ == "__main__":
    unittest.main()
