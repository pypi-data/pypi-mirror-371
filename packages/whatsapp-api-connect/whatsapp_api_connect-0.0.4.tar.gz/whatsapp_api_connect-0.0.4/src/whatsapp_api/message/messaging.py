from whatsapp_api.base_client import BaseClient
from whatsapp_api.message.validation import validate_buttons, validate_list_message


class MessagingClient(BaseClient):
    def __init__(self, access_token, phone_number_id, version="v21.0"):
        """
        Messaging client for WhatsApp.

        :param access_token: Meta API access token
        :param phone_number_id: Phone number ID from WhatsApp
        """
        super().__init__(access_token, version)
        self.endpoint = f"{phone_number_id}/messages"

    # Mark Message as Read and typing indicator
    def mark_message_as_read(self, message_id):
        """
        Mark a message as read.

        :param message_id: The ID of the message to mark as read.
        :return: API response JSON
        """
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
            "typing_indicator": {
                "type": "text"
            }
        }
        return self._request("POST", self.endpoint, payload)

    # Send Text Message
    def send_text_message(self, recipient_phone_number, message, preview_url=False, context_message_id=None):
        """
        Send a text message.

        :param recipient_phone_number: The recipient's WhatsApp phone number in international format (e.g., 1234567890, without the +).
        :param message: The message content - Maximum 4096 characters.
        :param preview_url: Preview URL render a link preview of any URL in the body text string. (optional)
        :param context_message_id: (Optional) Message ID of a previous message to reply to.
        :return: API response JSON
        """

        # Prepare the payload
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone_number,
            "type": "text",
            "text": {
                "preview_url": preview_url, 
                "body": message
            },
        }

        # Add context if provided (optional)
        if context_message_id:
            payload["context"] = {"message_id": context_message_id}

        return self._request("POST", self.endpoint, payload)

    # Send Reply to Text Message
    def reply_text_message(self, recipient_phone_number, message, context_message_id, preview_url=False):
        """
        Send a reply to a text message.

        :param recipient_phone_number: The recipient's WhatsApp phone number in international format (e.g., 1234567890, without the +).
        :param message: The reply message content - Maximum 4096 characters.
        :param context_message_id: The ID of the previous message in the conversation.
        :param preview_url: Preview URL render a link preview of any URL in the body text string. (optional)
        :return: API response JSON
        """

        # Prepare the payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone_number,
            "context": {
                "message_id": context_message_id
            },
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message
            }
        }

        return self._request("POST", self.endpoint, payload)

    # Send Reply with Reaction Message
    def send_reaction_message(self, recipient_phone_number, message_id, emoji):
        """
        Send a reaction to a specific WhatsApp message.

        :param recipient_phone_number: The recipient's WhatsApp phone number in international format (e.g., 1234567890, without the +).
        :param message_id: The ID of the message to which the reaction applies.
        :param emoji: The emoji for the reaction (e.g., 👍, ❤️, 😂).
        :return: API response JSON
        """
        # Prepare the payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone_number,
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": emoji,
            },
        }

        return self._request("POST", self.endpoint, payload)

    # Send Interactive Message with Buttons
    def send_button_message(self, recipient_phone_number, text, buttons, context_message_id=None):
        """
        Send an interactive button message.

        :param recipient_phone_number: The recipient's WhatsApp phone number in international format (e.g., 1234567890, without the +).
        :param text: The message text
        :param buttons: List of button dictionaries 
        :param context_message_id: Optional message ID of a previous message to reply to.
        :return: API response JSON
        """
        # Validate the buttons
        validate_buttons(buttons)

        # Prepare the payload
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {"buttons": buttons},
            },
        }

        # Add context if provided (optional)
        if context_message_id:
            payload["context"] = {"message_id": context_message_id}

        return self._request("POST", self.endpoint, payload)

    # Send Interactive List Message with Header and Footer
    def send_list_message(self, recipient_phone_number, body_text, sections, button_cta, header_text=None, footer_text=None, context_message_id=None):
        """
        Send an interactive list message.

        :param recipient_phone_number: The recipient's WhatsApp phone number in international format (e.g., 1234567890, without the +).
        :param body_text: The main body text of the message.
        :param sections: List of section dictionaries (with title and rows).
        :param button_cta: Button label text (CTA button).
        :param header_text: Optional header text (max 60 characters).
        :param footer_text: Optional footer text (max 60 characters).
        :param context_message_id: Optional message ID of a previous message to reply to.
        :return: API response JSON.
        """
        # Validate the inputs
        validate_list_message(body_text, sections, button_cta, header_text, footer_text)

        # Prepare the payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": body_text},
                "action": {"button": button_cta, "sections": sections},
            },
        }

        # Add optional header
        if header_text:
            payload["interactive"]["header"] = {"type": "text", "text": header_text}

        # Add optional footer
        if footer_text:
            payload["interactive"]["footer"] = {"text": footer_text}

        # Add context if provided (optional)
        if context_message_id:
            payload["context"] = {"message_id": context_message_id}

        return self._request("POST", self.endpoint, payload)

    # Send a contact message to a recipient. 
    def send_contact_message(self, recipient_phone_number, contact_data, context_message_id=None, **kwargs):
        """
        :param recipient_phone_number: The recipient's WhatsApp phone number in international format (e.g., 1234567890, without the +).
        :param contact_data: A dictionary containing the contact details (e.g., name, phone, address, etc.).
        :param context_message_id: (Optional) Message ID of a previous message to reply to.
        :param kwargs: Additional fields for the contact message (e.g., custom fields for contacts).
        :return: Response from the WhatsApp API.
        :raises ValueError: If invalid parameters are used.
        :raises Exception: If the API request fails.
        """

        # Validate required contact fields
        if "name" not in contact_data or not contact_data["name"].get("formatted_name"):
            raise ValueError("Contact data must include 'name' with a 'formatted_name' field.")
        if "phones" not in contact_data or len(contact_data["phones"]) == 0:
            raise ValueError("Contact data must include at least one 'phone'.")

        # Prepare the contact object
        contact_payload = {
            "name": contact_data["name"],  # Name is required
            "phones": contact_data.get("phones", []),  # List of phone numbers, optional but required if present
            "addresses": contact_data.get("addresses", []),  # List of addresses (optional)
            "birthday": contact_data.get("birthday"),  # Optional birthday in YYYY-MM-DD format
            "emails": contact_data.get("emails", []),  # List of emails (optional)
            "org": contact_data.get("org", {}),  # Organization details (optional)
            "urls": contact_data.get("urls", [])  # List of URLs (optional)
        }

        # Construct the payload for the API request
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_phone_number,
            "type": "contacts",
            "contacts": [contact_payload],
        }

        # Add context if provided (optional)
        if context_message_id:
            payload["context"] = {"message_id": context_message_id}

        # Send the request and return the response
        return self._request("POST", self.endpoint, payload)
