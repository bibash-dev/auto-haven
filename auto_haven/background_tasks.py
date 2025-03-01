import json
import logging
from typing import Dict, Any
from fastapi import HTTPException, status
from openai import OpenAI
import resend
from .config import BaseConfig
from auto_haven.models.car import Car

logger = logging.getLogger(__name__)

settings = BaseConfig()

client = OpenAI(api_key=settings.OPENAI_API_KEY)

resend.api_key = settings.RESEND_API_KEY


def generate_prompt(brand: str, model: str, year: int) -> str:
    return f"""
    You are a helpful car sales assistant. Your task is to describe the {brand} {model} from {year} in a playful and engaging way.
    Additionally, provide five pros and five cons of the model. Ensure the cons are not overly negative but still honest.

    Respond in the following JSON format:
    {{
        "description": "A playful and positive description of the {brand} {model}. Make it at least 350 characters long.",
        "pros": [
            "A short and concise pro (max 12 words).",
            "Another short and concise pro (max 12 words).",
            "Keep it playful and slightly positive.",
            "Highlight the best features of the car.",
            "End with a strong positive point."
        ],
        "cons": [
            "A short and concise con (max 12 words).",
            "Another short and concise con (max 12 words).",
            "Be honest but not overly negative.",
            "Mention minor drawbacks in a lighthearted way.",
            "End with a constructive criticism."
        ]
    }}

    Guidelines:
    - The *description* should be playful, positive, and engaging. Avoid being over the top.
    - The *pros* should sound very positive and highlight the car's strengths.
    - The *cons* should be honest but not too negative. Use a slightly negative tone.
    - Keep all points concise and within the word limit.
    """


def generate_email(
    brand: str,
    model: str,
    year: int,
    image_url: str,
    car_info: Dict[str, Any],
) -> str:
    # Validate car_info
    if not all(key in car_info for key in ["description", "pros", "cons"]):
        raise ValueError(
            "car_info is missing required fields: description, pros, or cons"
        )

    # Generate pros and cons lists
    pros_list = "<br>".join([f"- {pro}" for pro in car_info["pros"]])
    cons_list = "<br>".join([f"- {con}" for con in car_info["cons"]])

    # Generate the email HTML
    return f"""
    <html>
        <body>
            <h2>Hello,</h2>
            <p>We have a new car for you: {brand} {model} from {year}.</p>
            <p><img src="{image_url}" alt="{brand} {model}" style="max-width: 100%; height: auto;"/></p>
            <p>{car_info['description']}</p>
            <h3>Pros</h3>
            <p>{pros_list}</p>
            <h3>Cons</h3>
            <p>{cons_list}</p>
        </body>
    </html>
    """


async def create_car_description_and_send_email(
    brand: str,
    model: str,
    year: int,
    image_url: str,
    recipient_email: str,
) -> Dict[str, Any]:
    try:
        # Generate the prompt
        prompt = generate_prompt(brand, model, year)
        logger.info(f"Generated prompt for {brand} {model} ({year})")

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.2,
        )
        content = response.choices[0].message.content
        logger.info(f"Received response from OpenAI for {brand} {model} ({year})")

        # Parse the JSON response
        try:
            car_info = json.loads(content)
            if not all(key in car_info for key in ["description", "pros", "cons"]):
                raise ValueError("Invalid JSON structure in OpenAI response")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse OpenAI response.",
            )

        # Update the database
        try:
            await Car.find(
                Car.brand == brand,
                Car.model == model,
                Car.year == year,
            ).set(
                {
                    "description": car_info["description"],
                    "pros": car_info["pros"],
                    "cons": car_info["cons"],
                }
            )
            logger.info(f"Updated database for {brand} {model} ({year})")
        except Exception as e:
            logger.error(f"Failed to update database: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update database.",
            )

        # Generate and send the email
        try:
            email_html = generate_email(brand, model, year, image_url, car_info)
            logger.info(f"Generated email for {brand} {model} ({year})")

            params: resend.Emails.SendParams = {
                "from": "FARM Cars <onboarding@resend.dev>",
                "to": [recipient_email],
                "subject": "New Car On Sale!",
                "html": email_html,
            }
            resend.Emails.send(params)
            logger.info(f"Email sent successfully to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {str(e)}",
            )

        return car_info

    except HTTPException:
        raise  # Re-raise HTTPException to propagate the error
    except Exception as e:
        logger.error(f"Unexpected error in create_car_description_and_send_email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the car description and sending the email.",
        )
