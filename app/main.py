from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class = HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Find test dataset
@app.post("/find-dataset", response_class=HTMLResponse)
async def generate_dataset(request: Request, query: str = Form(...), count: int = Form(...)):
    return templates.TemplateResponse("result.html", {"request": request, "query": query, "count": count})