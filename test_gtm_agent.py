import json
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import gtm_agent


class ProspectToolPrivacyTest(unittest.TestCase):
    def test_prospect_tools_exclude_billing_fields(self):
        record = {
            "name": "Test Prospect",
            "email": "test@example.com",
            "billing_qualification": {
                "tax_id": "123-45-6789",
                "date_of_birth": "1990-01-01",
                "card_on_file": "4111111111111111",
                "credit_check_ref": "EXPN-12345",
            },
            "annual_revenue": 1000000,
        }
        with (
            patch.object(gtm_agent.data_service, "get_prospect_record", return_value=record),
            patch.object(gtm_agent.data_service, "get_profile_from_db", return_value={"prospect_profile": None}),
            patch.object(gtm_agent.data_service, "fetch_engagement_history", return_value=[]),
            patch.object(gtm_agent.data_service, "fetch_account_details", return_value={}),
            patch.object(gtm_agent.data_service, "fetch_tech_stack", return_value=[]),
            patch.object(gtm_agent.data_service, "save_profile_to_db"),
        ):
            results = [
                gtm_agent.get_prospect.invoke({"prospect_id": "LEAD-TEST"}),
                gtm_agent.build_prospect_profile.invoke({"prospect_id": "LEAD-TEST"}),
            ]

        serialized_results = json.dumps(results)
        for field in ("billing_qualification", "tax_id", "card_on_file"):
            self.assertNotIn(field, serialized_results)


if __name__ == "__main__":
    unittest.main()
