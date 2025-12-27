from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class = HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Find test dataset endpoint
@app.post("/find-dataset", response_class=HTMLResponse)
async def generate_dataset(request: Request, prompt: str = Form(...), count_of_img: int = Form(...)):

    # Request to GPT 4o-mini
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    completion = client.chat.completions.create(
        extra_body={},
        model="openai/gpt-4o-mini",
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Analyse the request. 
                        It will describe what the set of images should look like. 
                        Your task is to find 10 websites where these images can be found. 
                        Check the links very carefully to make sure they all work and open. 
                        Also, filter the requests. For sensitive content, simply respond with 
                        ‘status: sensored content’ without any extra text. 
                        If the request is acceptable and you understand what set of images the user wants, 
                        simply list 10 websites as we discussed earlier in this format: 
                        "status: good
                        sites: and here, list all the links one by one, separated by commas"
                        Here is a request for analysis: {prompt}"""
                    }
                ]
            }
        ]
    )

    result = completion.choices[0].message.content

    # Result parsing
    data = {}

    for line in result.strip().splitlines():
        key, value = line.strip().split(":", 1)
        key = key.strip()
        value = value.strip()

        if key == "sites":
            data[key] = [v.strip() for v in value.split(",")]
        else:
            data[key] = value


    if data.get("status") == "good":
        sites = data.get("sites", [])

    # Return .html and data
    return templates.TemplateResponse("result.html", {
        "request": request, 
        "query": prompt, 
        "count": count_of_img, 
        "sites": sites
    })