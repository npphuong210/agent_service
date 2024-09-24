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


# globals.set_debug(True)

def encode_image(image: Image.Image) -> dict:
    """Encode a PIL image as base64 and return in a dict with a proper format."""
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return {
        "url": f"data:image/jpeg;base64,{image_base64}"
    }

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

# parser = JsonOutputParser(pydantic_object=ImageInformation)

def get_image_informations(image: Image.Image) -> dict:
    vision_prompt = """Given the image, extract all visible text from the scanned image. 
    Ensure that the extraction includes all text present in the image, regardless of the language.     
    - Provide the full text found in the image without any translation. 
    - Output the text clearly and completely as it appears in the image.
    """
    
    # Encode the image
    image_data = encode_image(image)
    
    # Combine encoding, processing, and parsing into a single chain
    vision_chain = image_model
    
    # Execute the chain with the encoded image and prompt
    return vision_chain.invoke({
        'image': image_data,
        'prompt': vision_prompt
    })