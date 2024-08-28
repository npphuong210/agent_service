import base64
from pydantic import BaseModel, Field
from langchain.chains import TransformChain
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain import globals
from langchain_core.runnables import chain
from langchain_core.output_parsers import JsonOutputParser
from io import BytesIO
from PIL import Image

# Set verbose logging for LangChain
globals.set_debug(True)

# Step 1: Define the function to encode the image as base64
def encode_image(image: Image.Image) -> dict:
    """Encode a PIL image as base64 and return in a dict with a proper format."""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # The correct structure expected by the API
    return {
        "url": f"data:image/jpeg;base64,{image_base64}"
    }

# Step 2: Define the Pydantic model for the expected output structure
class ImageInformation(BaseModel):
    """Information about an image."""
    image_description: str = Field(description="A short description of the image")
    people_count: int = Field(description="Number of humans in the picture")
    main_objects: list[str] = Field(description="List of the main objects in the picture")

# Step 3: Create the chain that invokes the model with the prompt and image
@chain
def image_model(inputs: dict) -> str | list[str] | dict:
    """Invoke model with image and prompt."""
    model = ChatOpenAI(temperature=0.5, model="gpt-4-turbo", max_tokens=1024)
    
    # Create a HumanMessage with both text and image content
    msg = model.invoke(
        [HumanMessage(
            content=[
                {"type": "text", "text": inputs["prompt"]},
                {"type": "image_url", "image_url": {"url": inputs['image']['url']}}
            ]
        )]
    )
    return msg.content

# Step 4: Define the output parser using the Pydantic model
parser = JsonOutputParser(pydantic_object=ImageInformation)

# Step 5: Orchestrate the entire process in one function
def get_image_informations(image: Image.Image) -> dict:
    vision_prompt = """
    Given the image, provide the following information:
    - A count of how many people are in the image
    - A list of the main objects present in the image
    - A description of the image
    """
    
    # Encode the image
    image_data = encode_image(image)
    
    # Combine encoding, processing, and parsing into a single chain
    vision_chain = image_model | parser
    
    # Execute the chain with the encoded image and prompt
    return vision_chain.invoke({
        'image': image_data,
        'prompt': vision_prompt
    })
