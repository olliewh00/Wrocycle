import os
import io
import json
import re
import base64
from PIL import Image
from dotenv import load_dotenv

# Load env variables from a .env file if present
load_dotenv()

SYSTEM_INSTRUCTION = """You are an expert waste sorting assistant for university students living in dormitories in Wrocław, Poland (e.g., T-17, T-15 dorms).
Your task is to analyze the image of a piece of waste and classify it strictly according to the official waste management rules of Ekosystem Wrocław.

Analyze the image and return a strict, minified JSON object with NO markdown formatting (no ```json code blocks, just raw JSON) containing exactly the following keys:
{
  "item_identified": "Short, specific name of the item (e.g., Oily Pizza Box)",
  "fraction": "PLASTICS & METALS | PAPER | GLASS | BIO-WASTE | MIXED WASTE | KAUCJA | CLOTHES & BATTERIES",
  "bin_color": "YELLOW | BLUE | GREEN | BROWN | BLACK | STORE RETURN | RED",
  "action_required": "A 3-to-5 word action phrase in all-caps (e.g., DO NOT WASH, CRUSH IT, SEPARATE LID, THROW IN BLACK BIN IF OILY)"
}

Rules for fractions & bin_color mapping:
1. PLASTICS & METALS (YELLOW):
   - Includes: Plastic bottles, aluminum/metal cans, snack wrappers, clean plastic cups/tubs, milk/juice cartons (Tetra Paks), metal lids.
2. PAPER (BLUE):
   - Includes: Clean cardboard, notebooks, paper packaging, brochures.
   - CRITICAL LOCAL RULE: Greasy, oily, or dirty paper (e.g., oily pizza boxes, food-soiled wraps) CANNOT go here. They must go to MIXED WASTE.
3. GLASS (GREEN):
   - Includes: Glass bottles, clean food jars (without metal lids/caps).
   - CRITICAL RULE: No ceramics, drinking glasses, mirrors, heat-resistant glass, or porcelain. These must go to MIXED WASTE.
4. BIO-WASTE (BROWN):
   - Includes: Vegetable/fruit scraps, coffee grounds, eggshells.
   - CRITICAL RULE: No meat, bones, dairy, or animal waste. These go to MIXED WASTE.
5. MIXED WASTE (BLACK):
   - Includes: Oily/greasy pizza boxes, dirty packaging, greasy paper, food leftovers, meat/bones, used tissues, receipts, ceramics, drinking glasses.
6. KAUCJA (STORE RETURN):
   - The Polish deposit return system (Kaucja). Applies to:
     * PET beverage bottles (up to 3 liters)
     * Aluminum beverage cans (up to 1 liter)
     * Glass bottles (up to 1.5 liters)
     * If the item is a standard returnable bottle or can, classify it as KAUCJA / STORE RETURN to encourage returning it for the deposit refund!
7. CLOTHES & BATTERIES (RED):
   - Special disposal items. Applies to:
     * Old clothes, shoes, bags, textiles
     * Alkaline or rechargeable batteries, phone/laptop batteries
     * Small electronic items (e-waste, chargers, lightbulbs)
     * CRITICAL RULE: These CANNOT go in standard trash bins. Clothes go to clothing bins/donation. Batteries and e-waste must be taken to special store return boxes or PSZOK.

CRITICAL: Return ONLY a raw JSON string. Do not include markdown code block syntax (like ```json ... ```). Validate that the JSON contains exactly the keys listed above and values match the allowed options.
"""

def parse_json_response(response_text: str) -> dict:
    """
    Cleans up any markdown wrapper blocks (like ```json ... ```) from the LLM response
    and parses it into a Python dictionary.
    """
    cleaned = response_text.strip()
    
    # Remove code blocks if present
    if cleaned.startswith("```"):
        match = re.search(r"^(?:```(?:json)?\n?)(.*?)(?:\n?```)$", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
            
    # Try parsing
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Fallback regex extraction if the model added leading/trailing conversational text
        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Failed to parse model response as JSON. Raw response: {response_text}") from e

def classify_waste(image: Image.Image) -> dict:
    """
    Main waste classification routine.
    Loads API keys and routes to Google Gemini or OpenAI GPT-4o based on availability.
    """
    backend = os.getenv("CLASSIFIER_BACKEND", "").lower()
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # Determine which backend to use
    if backend == "openai" or (openai_key and not gemini_key):
        if not openai_key:
            raise ValueError("OpenAI backend requested but OPENAI_API_KEY is not set.")
        return _classify_openai(image, openai_key)
    else:
        # Default to Gemini (or fail if no key)
        if not gemini_key:
            raise ValueError(
                "No API keys found. Please set either GEMINI_API_KEY or OPENAI_API_KEY "
                "in your environment or in a .env file in the project folder."
            )
        return _classify_gemini(image, gemini_key)

def _classify_gemini(image: Image.Image, api_key: str) -> dict:
    """
    Classifies the image using Google's new GenAI SDK with exponential backoff retries.
    """
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    import time
    
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)
    
    # Convert image to RGB if it isn't, as some image formats (like RGBA) can fail
    if image.mode != "RGB":
        image = image.convert("RGB")
        
    max_retries = 3
    delay = 1.0  # seconds
    
    for attempt in range(max_retries + 1):
        try:
            # Call Gemini Vision API
            response = client.models.generate_content(
                model=model_name,
                contents=[image, SYSTEM_INSTRUCTION],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            if not response.text:
                raise ValueError("Gemini returned an empty response.")
                
            return parse_json_response(response.text)
            
        except APIError as api_err:
            error_code = getattr(api_err, "code", None)
            error_msg = str(api_err).upper()
            
            is_retryable = (
                error_code in [429, 500, 503, 504] or
                any(kw in error_msg for kw in ["500", "503", "429", "INTERNAL", "UNAVAILABLE", "TIMEOUT", "RESOURCE_EXHAUSTED"])
            )
            
            if is_retryable and attempt < max_retries:
                time.sleep(delay)
                delay *= 2.0
                continue
            raise RuntimeError(f"Error calling Google Gemini API: {str(api_err)}") from api_err
            
        except Exception as e:
            err_msg = str(e).upper()
            is_retryable_exception = any(kw in err_msg for kw in ["500", "503", "429", "INTERNAL", "UNAVAILABLE", "TIMEOUT", "CONNECTION", "RESET", "EOF"])
            
            if is_retryable_exception and attempt < max_retries:
                time.sleep(delay)
                delay *= 2.0
                continue
            raise RuntimeError(f"Error calling Google Gemini API: {str(e)}") from e

def _classify_openai(image: Image.Image, api_key: str) -> dict:
    """
    Classifies the image using OpenAI's API with exponential backoff retries.
    """
    from openai import OpenAI
    from openai import APIError
    import time
    
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)
    
    # Convert image to RGB if it isn't
    if image.mode != "RGB":
        image = image.convert("RGB")
        
    # Convert PIL Image to base64 JPEG
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    max_retries = 3
    delay = 1.0  # seconds
    
    for attempt in range(max_retries + 1):
        try:
            # Call OpenAI Chat Completions API with vision
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": SYSTEM_INSTRUCTION},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_b64}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            if not response_text:
                raise ValueError("OpenAI returned an empty response.")
                
            return parse_json_response(response_text)
            
        except APIError as api_err:
            error_code = getattr(api_err, "status_code", None)
            error_msg = str(api_err).upper()
            
            is_retryable = (
                error_code in [429, 500, 502, 503, 504] or
                any(kw in error_msg for kw in ["429", "500", "502", "503", "504", "RATE_LIMIT", "INTERNAL", "TIMEOUT"])
            )
            
            if is_retryable and attempt < max_retries:
                time.sleep(delay)
                delay *= 2.0
                continue
            raise RuntimeError(f"Error calling OpenAI API: {str(api_err)}") from api_err
            
        except Exception as e:
            err_msg = str(e).upper()
            is_retryable_exception = any(kw in err_msg for kw in ["500", "503", "429", "INTERNAL", "UNAVAILABLE", "TIMEOUT", "CONNECTION", "RESET", "EOF"])
            
            if is_retryable_exception and attempt < max_retries:
                time.sleep(delay)
                delay *= 2.0
                continue
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}") from e
