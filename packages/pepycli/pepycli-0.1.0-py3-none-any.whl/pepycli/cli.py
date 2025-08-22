from typer import Typer, Argument, echo
from .api import PepyCliAPI
from asyncio import run

app = Typer(help="PepyCLI - tool for working with the Pepy.tech API")
api = PepyCliAPI()

@app.command(help="Get analytics for the specified project")
def analytics(project: str = Argument(..., help="Project name")):
    result = run(api.get_analytics(project))
    echo(result)

@app.command(help="Get downloads for the specified project")
def downloads(project: str = Argument(..., help="Project name")):
    result = run(api.get_project_downloads(project))
    echo(result)

def main():
    app()

if __name__ == "__main__":
    main()
