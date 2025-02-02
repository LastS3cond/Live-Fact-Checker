from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# System prompt (hidden from user but can be modified in code)
CLAIM_PROMPT = """Your task is to analyze a given text and identify statements that assert an objective, verifiable fact. Factual claims are statements that describe events or conditions that can be checked against external evidence.

Do Not Include the Following as Factual Claims:
    Opinions or Subjective Views: Statements that express personal feelings or beliefs.
    Promises, Predictions, or Intentions: Statements that forecast future actions or commitments (often indicated by words like “will”). For example, if a speaker says, “I will direct our government to use the full power of law enforcement...,” this is a promise or intended action—not a present, verifiable fact.
Instructions:
    - Identify Factual Claims: Look for assertions about events, conditions, or situations that exist or have existed and can be independently verified.
    - Exclude Future or Conditional Statements: Do not tag any statements that predict or promise future actions, even if they include factual elements.
    - Facts should be specific and complete statements.
    - Output as the extracted claims in a JSON array without modifying the original words. Include a topic field in the output.
By following these guidelines, you will ensure that only verifiable, factual statements are marked, and statements indicating future intentions are correctly excluded."""

# System prompt (hidden from user but can be modified in code)
FACT_CHECK_PROMPT = """You will be given a claim about a specific topic. Your job is 
to use web search to determine the truth value and relative harm of the given claim. Any sources used for the 
truth value should be cited. Your output should be a truth value seperated by a line, harm value 
separated by a line and a short paragraph explaining your decision. The accepted values for the truth
are "Certainly False", "Somewhat False", "Neutral/Ambiguous", "Somewhat True", "Certainly True". 
The accepted values for harm are "Extremely harmful to [groups harmed]", "Harmful to [groups harmed]", 
"Somewhat Harmful to [groups harmed]", "Slightly Harmful to [groups harmed]",
"Harmful to no groups".
"""

genai.configure(api_key=GOOGLE_API_KEY)


def init_claim_model():
    return genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=CLAIM_PROMPT,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object",
                "properties": {
                    "claims": {"type": "array", "items": {"type": "string"}},
                    "topic": {"type": "string"},
                },
                "required": ["claims"],
            },
            temperature=0.5,
        ),
    )


def init_fact_check_model():
    return genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=FACT_CHECK_PROMPT,
    )
