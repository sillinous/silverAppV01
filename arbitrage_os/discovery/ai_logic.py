import logging
import os
import json
from openai import OpenAI

logger = logging.getLogger(__name__)

def analyze_description(description: str) -> dict:
    """
    Analyzes a sale description using an LLM to rank it for silver content and extract an address.

    This function requires an OpenAI API key to be set in the environment
    as `OPENAI_API_KEY`.

    Args:
        description: The text description of the sale.

    Returns:
        A dictionary containing the score and the extracted address.
    """
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set.")
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    client = OpenAI()

    system_prompt = """
    You are an expert in sourcing precious metals. Your task is to analyze text from online marketplace listings (like Craigslist or Facebook Marketplace) to find potential silver items.
    Analyze the provided text and return a JSON object with the following keys:
    1. "score": An integer from 1 to 10, where 10 is the highest likelihood of the listing containing high-purity, valuable silver items. Base your score on keywords like 'tarnish', 'heavy', 'antique', 'collection', 'sterling', 'estate', 'flatware', 'hallmark'. Downgrade the score for keywords like 'plate', 'plated', 'silverware' (when used ambiguously), or 'EPNS'.
    2. "reasoning": A brief, one-sentence explanation for why you assigned the score.
    3. "address": The full street address of the sale, if mentioned. If no address is found, return "Not found".
    4. "weight_grams": The estimated weight of the silver item in grams, if mentioned. Return null if not found.
    5. "purity": The estimated purity of the silver (e.g., 0.925 for sterling, 0.999 for fine silver), if mentioned. Return null if not found.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        analysis_result = json.loads(response.choices[0].message.content)
        return analysis_result

    except Exception as e:
        logger.error(f"An error occurred during LLM analysis: {str(e)}")
        return {"error": f"An error occurred during LLM analysis: {str(e)}"}

