import google.generativeai as genai
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# System prompt (hidden from user but can be modified in code)
CLAIM_PROMPT = """Your task is to parse a speech, and you are 
going to identify any claims made within the speech that assert 
some fact which can be fact-checked using external resources. The 
claims may or may not be true, however you are not going to determine 
the validity of the truth. You must wrap any claims with a <claim></claim> 
tag. For all speakers, try to infer their names and if no name can be 
inferred, call them by Speaker #X. Separate each speaker\u0027s transcript 
with [Speaker name]: [Speaker text]."""

# System prompt (hidden from user but can be modified in code)
FACT_CHECK_PROMPT = """You will be given a claim. Your job is 
to use web search to determine the truth value and relative harm of the given claim. Any sources used for the 
truth value should be cited. Your output should be a truth value seperated by a line, harm value 
separated by a line and a short paragraph explaining your decision. The accepted values for the truth
are "Certainly False", "Somewhat False", "Neutral/Ambiguous", "Somewhat True", "Certainly True". 
The accepted values for harm are "Extremely harmful to [groups harmed]", "Harmful to [groups harmed]", 
"Somewhat Harmful to [groups harmed]", "Slightly Harmful to [groups harmed]",
"Harmful to no groups".
"""

genai.configure(api_key=GOOGLE_API_KEY)


# Initialize Gemini model
def init_claim_model(system_prompt):
    return genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)


def init_fact_check_model(system_prompt):
    return genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=system_prompt,
    )
