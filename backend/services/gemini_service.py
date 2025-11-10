import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# Constants
GEMINI_MODEL = "gemini-2.0-flash"


class GeminiService:
    """Handles intelligent JSON payload generation for farmer surveys."""

    def __init__(self):
        self.llm = self._initialize_llm()

    def _initialize_llm(self) -> Optional[ChatGoogleGenerativeAI]:
        if not os.getenv("GEMINI_API_KEY"):
            print("ERROR: Gemini API key not found. Please set it in your .env file.")
            return None
        try:
            return ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.0)
        except Exception as e:
            print(f"Failed to initialize Gemini model: {e}")
            return None

    def generate_json_payload(
        self, schema: str, transcript: str
    ) -> Optional[Dict[str, Any]]:
        """Generates a structured JSON payload from a transcript based on a provided schema."""
        if not self.llm:
            return None
        try:
            print("Gemini is analyzing the interview to generate the JSON payload...")
            # Define a dynamic Pydantic model for the parser
            class DynamicSchema(BaseModel):
                payload: Dict[str, Any] = Field(
                    description="The final JSON payload based on the user's schema"
                )

            parser = JsonOutputParser(pydantic_object=DynamicSchema)

            prompt_template = """
                You are an expert agricultural data analyst specializing in Indian farmer surveys. 
                Your task is to carefully analyze the interview transcript and extract accurate information to populate the JSON schema.

                **CRITICAL INSTRUCTIONS:**
                1. **FILL MAXIMUM FIELDS**: Extract and populate as many fields as possible from the transcript
                2. **ACCURACY FIRST**: Only extract information that is explicitly mentioned in the transcript
                3. **CONTEXT AWARENESS**: Understand Hindi/English mixed conversations common in rural India
                4. **FIELD MAPPING**: Map transcript content to correct schema fields precisely
                5. **CREATE MULTIPLE ENTRIES**: For arrays, create multiple objects when multiple items are mentioned

                **SPECIFIC GUIDELINES:**
                - Names: Extract full names as mentioned
                - Numbers: Convert spoken numbers to digits (e.g., "पांच एकड़" → "5")
                - Locations: Use proper spelling for villages/districts
                - Crops: Use standard crop names (wheat, rice, sugarcane, etc.)
                - Technology: Map to specific tools/apps mentioned
                - Government schemes: Use official scheme names if mentioned

                **JSON Schema:**
                ```json
                {schema}
                ```

                **Interview Transcript:**
                ```text
                {transcript}
                ```

                **IMPORTANT**: Return ONLY the populated JSON object. No explanations or additional text.
                
                {format_instructions}
            """
            prompt = ChatPromptTemplate.from_template(
                template=prompt_template,
                partial_variables={
                    "format_instructions": parser.get_format_instructions()
                },
            )

            chain = prompt | self.llm | parser
            response = chain.invoke({"schema": schema, "transcript": transcript})

            print("Gemini has successfully generated the JSON payload!")
            # The parser wraps the result in a 'payload' key, so we extract it.
            return response.get("payload", {})
        except Exception as e:
            print(f"Failed to generate JSON payload with Gemini: {e}")
            return None
