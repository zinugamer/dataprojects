
from openai import OpenAI # Import the OpenAI client library to interact with the OpenAI API.
from prompts import BRAND_CARD_PROMPT # Import a predefined prompt template for generating brand cards.

client = OpenAI() # Initialize the OpenAI client to enable API calls for generating responses.


# This function generates a simple summary for a given brand based on the provided research purpose and source text.
def generate_brand_card(brand_name: str, research_purpose: str, source_text: str) -> str: 
    
    # Create a prompt using the provided brand name, research purpose, and source text.
    prompt = BRAND_CARD_PROMPT.format(
        brand_name=brand_name, 
        research_purpose=research_purpose, 
        source_text=source_text
    )
    # Use the prompt to generate a response from the model. 
    response = client.responses.create( 
        model="gpt-5.5",
        input=prompt
    )
    
    return response.output_text

# Example usage
if __name__ == "__main__":
    brand = "Cole Haan"
    research_purpose = "To understand the brand's market position and customer perception."
    source_text = """
    Cole Haan is an American footwear and accessories brand founded in 1928.
    It was previously owned by Nike and later sold to Apax Partners.
    Himaxx became Cole Haan's exclusive distribution partner in China in 2024.
    """


    result = generate_brand_card(brand, research_purpose, source_text)
    print(result)