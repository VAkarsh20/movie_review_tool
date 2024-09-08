import yaml
import time
import google.generativeai as genai
from utils.constants import GEMINI_REQUEST_LIMIT, GEMINI_PROMPT


def proofread_comments(comments, model):
    parts = comments.split(";")
    try:
        result = model.generate_content("{}: {}".format(GEMINI_PROMPT, str(parts)))
        return result.text.replace("**", "").rstrip()
    except ValueError as e:
        print('Cannot produce a result for comments: "{}"'.format(comments))
        return comments


def wait(counter, request_batch, sleep_time=65):
    if counter / request_batch > GEMINI_REQUEST_LIMIT:
        print("Above Google Gemini request limit, waiting 1 minute before next batch")
        time.sleep(sleep_time)
        return True
    else:
        return False


def create_model():
    # Load yaml file
    yml = yaml.safe_load(open("login_details.yml"))

    # Configure API key (replace with your actual key)
    genai.configure(api_key=yml["gemini"]["api_key"])

    # Generate text using the prompt
    return genai.GenerativeModel("gemini-1.5-flash")
