from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import pytesseract
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class VisionLLMModel:
    def __init__(self):
        # Load the OpenAI API key from environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Initialize the OpenAI LLM
        self.llm = OpenAI(api_key=api_key, model="gpt-4o-mini")  # Replace with your model name
        # Define a prompt template for processing images
        self.prompt_template = PromptTemplate(
            input_variables=["image_text"],
            template="Extract structured data from the following image text: {image_text}",
        )

        # Create a LangChain with the defined prompt
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def predict(self, image):
        """
        Process the image using the GPT-Vision model via LangChain.
        :param image: A PIL image to be processed.
        :return: The structured data result from the model as a string.
        """
        # Convert image to text using OCR
        image_text = pytesseract.image_to_string(image)

        # Run the text through the LangChain
        result = self.chain.run(image_text)

        return result
