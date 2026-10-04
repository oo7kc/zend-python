"""Quickstart walkthrough of the Zend SDK."""

from __future__ import annotations

import os

from zend import Zend


def main() -> None:
    with Zend(os.environ.get("ZEND_API_KEY")) as zend:
        # SMS — every option (keep only what you need)
        message = zend.messages.send(
            to="+233201234567",
            body="Hello from Zend!",
            preferred_channels=["sms"],
            sender_id="MyBrand",
            fallback_enabled=True,
            priority="high",
            delivery_priority="speed",
            webhook_url="https://your-app.com/webhooks/zend",
            # scheduled_for="2026-08-01T09:00:00Z",
        ).unwrap()
        print(f"Message {message.id} ({message.status})")

        # WhatsApp with a template, falling back to SMS
        zend.messages.send(
            to="+233201234567",
            template_id="welcome",
            template_params={"first_name": "John"},
            preferred_channels=["whatsapp", "sms"],
            fallback_enabled=True,
            sender_id="MyBrand",
        ).unwrap()

        # Bulk send
        zend.messages.send_bulk(
            messages=[
                {"to": "+233201234567", "body": "Hi Ama!"},
                {
                    "to": "+233207654321",
                    "body": "Your code is 123456",
                    "template_params": {"code": "123456"},
                },
            ],
            preferred_channels=["sms"],
            sender_id="MyBrand",
            fallback_enabled=True,
            webhook_url="https://your-app.com/webhooks/zend",
        ).unwrap()

        # Email
        email = zend.emails.send(
            from_="you@example.com",
            to="user@gmail.com",
            subject="Hello world",
            html="<p>It works!</p>",
            text="It works!",
        ).unwrap()
        print(f"Email {email.id} sent")

        # Voice — text-to-speech with all options
        zend.voice.send(
            recipients=["+233201234567"],
            text="Your order has shipped.",
            voice="female",
            retry=True,
            callback_url="https://your-app.com/webhooks/voice",
            fallback={
                "sms": True,
                "sms_text": "Your order has shipped.",
                "sender_id": "MyBrand",
            },
        ).unwrap()

        # Voice — a pre-recorded audio file
        zend.voice.send(
            recipients=["+233201234567"],
            voice_url="https://cdn.example.com/message.mp3",
            fallback={"sms": True, "sms_text": "You have a new message."},
        ).unwrap()

        # Templates (read-only)
        templates = zend.templates.list(
            category="transactional",
            status="active",
            limit=20,
            offset=0,
        ).unwrap()
        print(f"You have {templates.total} templates")


if __name__ == "__main__":
    main()
