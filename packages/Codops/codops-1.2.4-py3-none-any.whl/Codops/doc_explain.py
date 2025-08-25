import os

import openai
import typer
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI and GitHub tokens
openai_api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

console = Console()

app = typer.Typer()


@app.command()
def docexp(content: str, filename: str):
    """Command for generating a document for the given explanations of the content."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": f"explain this path: {content}"}],
        )

        doc_content = response["choices"][0]["message"]["content"]

        console.print(
            f"[bold purple underline]Explanation for your path:[/bold purple underline] {doc_content}"
        )
    except Exception as e:
        typer.echo(f"Error: {e}")
        doc_content = None  # Ensure doc_content is defined

    if doc_content is not None:  # Vérifie si le contenu est valide
        with open(filename, "w") as f:
            f.write(doc_content)
        console.print(
            f"[bold brown]Document '{filename}' has been generated with the content:[/bold brown]\n{doc_content}"
        )
    else:
        typer.echo("Failed to generate document due to empty content.")


if __name__ == "__main__":
    app()
