import os
import sys
import unittest
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from whatsapp_api.message.messaging import MessagingClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TestMessagingClient(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        # Load variables from .env
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.recipient_phone_number = os.getenv("TEST_RECIPIENT_PHONE_NUMBER")

        if not self.access_token or not self.phone_number_id or not self.recipient_phone_number:
            raise EnvironmentError("Missing environment variables in .env file.")

        # Initialize the MessagingClient
        self.client = MessagingClient(self.access_token, self.phone_number_id)

    # Send Text Message
    @patch("whatsapp_api.base_client.BaseClient._request")
    def test_send_text_message(self, mock_request):
        """Test sending a text message."""
        mock_request.return_value = {"success": True}

        response = self.client.send_text_message(self.recipient_phone_number, "Hello, World!")
        self.assertEqual(response, {"success": True})

        mock_request.assert_called_once_with(
            "POST",
            f"{self.phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "to": self.recipient_phone_number,
                "type": "text",
                "text": {
                    'preview_url': False,
                    "body": "Hello, World!"
                },
            },
        )

    # Send Reply with Reaction Message
    @patch("whatsapp_api.base_client.BaseClient._request")
    def test_send_reaction_message(self, mock_request):
        """Test sending a reaction message."""
        mock_request.return_value = {"success": True}

        message_id = "wam1234567890..."
        emoji = "👍"

        response = self.client.send_reaction_message(self.recipient_phone_number, message_id, emoji)
        self.assertEqual(response, {"success": True})

        mock_request.assert_called_once_with(
            "POST",
            self.client.endpoint,
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.recipient_phone_number,
                "type": "reaction",
                "reaction": {
                    "message_id": message_id,
                    "emoji": emoji,
                },
            },
        )

    # Send Interactive Message with Buttons
    @patch("whatsapp_api.base_client.BaseClient._request")
    def test_send_button_message(self, mock_request):
        """Test sending a button message."""
        mock_request.return_value = {"success": True}

        buttons = [
            {"type": "reply", "reply": {"id": "btn1", "title": "Button 1"}},
            {"type": "reply", "reply": {"id": "btn2", "title": "Button 2"}},
        ]

        response = self.client.send_button_message(self.recipient_phone_number, "Choose an option:", buttons)
        self.assertEqual(response, {"success": True})

        mock_request.assert_called_once_with(
            "POST",
            f"{self.phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "to": self.recipient_phone_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": "Choose an option:"},
                    "action": {"buttons": buttons},
                },
            },
        )

    # Send Interactive Message with List
    @patch("requests.request")
    def test_send_list_message(self, mock_request):
        """Test sending a list message."""
        mock_request.return_value = MagicMock(
            status_code=200,
            json=lambda: {"messaging_product": "whatsapp", "messages": [{"id": "wamid.mock_message_id"}]},
        )

        sections = [
            {
                "title": "I want it ASAP!",
                "rows": [
                    {"id": "priority_express", "title": "Priority Mail Express", "description": "Next Day to 2 Days"},
                    {"id": "priority_mail", "title": "Priority Mail", "description": "1–3 Days"},
                ],
            },
        ]

        response = self.client.send_list_message(
            self.recipient_phone_number,
            body_text="Which shipping option do you prefer?",
            sections=sections,
            button_cta="Shipping Options",
            header_text="Choose Shipping Option",
            footer_text="Lucky Shrub: Your gateway to succulents™"
        )
        # self.assertEqual(response, {"success": True})
        self.assertEqual(response["messages"][0]["id"], "wamid.mock_message_id")

        mock_request.assert_called_once_with(
            "POST",
            f"{self.client.base_url}{self.client.endpoint}",
            json={
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self.recipient_phone_number,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {"text": "Which shipping option do you prefer?"},
                    "header": {"type": "text", "text": "Choose Shipping Option"},
                    "footer": {"text": "Lucky Shrub: Your gateway to succulents™"},
                    "action": {
                        "button": "Shipping Options",
                        "sections": sections,
                    },
                },
            },
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
        )

if __name__ == "__main__":
    unittest.main()
