from src import config
from openai import OpenAI
from src.tools import TOOLS 
from .data_loader import load_profile

class AboutMe:
    def __init__(self):
        self.client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
        self.model_name = config.MODEL_NAME
        self.name = config.ME
        self.pdf_path = config.PDF_PATH
        self.about_me_text = load_profile(self)
        self.details_recorded = False
        self.error_contact = False
        self.tools = TOOLS

