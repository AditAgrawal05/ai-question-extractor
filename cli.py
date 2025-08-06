import typer
import json
from core.pipeline import create_rag_pipeline, extract_questions
from pathlib import Path

app = typer.Typer()

# --- DYNAMICALLY BUILD THE FILE PATH ---
# This makes the script work reliably.
# It finds the directory where cli.py is located, then goes to 'data/filename'
try:
    SCRIPT_DIR = Path(__file__).parent
except NameError:
    SCRIPT_DIR = Path.cwd()

PDF_PATH = SCRIPT_DIR / "data" / "RD_Sharma_Class_12.pdf"
OUTPUT_DIR = SCRIPT_DIR / "output"
# ----------------------------------------

@app.command()
def extract(
    chapter: int = typer.Option(..., "--chapter", "-c", help="Chapter number, e.g., 30"),
    topic: str = typer.Option(..., "--topic", "-t", help="Topic name, e.g., 'Conditional Probability'")
):
    """
    Extracts math questions from a given chapter and topic of the RD Sharma PDF
    and saves them as a Markdown file with rendered LaTeX.
    """
    # Ensure the book exists
    if not Path(PDF_PATH).exists():
        typer.secho(f"Error: Book not found at {PDF_PATH}", fg=typer.colors.RED)
        typer.echo(f"Please check that the file exists and is named exactly 'RD_Sharma_Class_12.pdf' inside the 'data' folder.")
        raise typer.Exit(code=1)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 1. Create the pipeline
    typer.echo("Creating RAG pipeline...")
    rag_pipeline = create_rag_pipeline(str(PDF_PATH))

    # 2. Extract the questions
    typer.echo(f"Extracting questions for Chapter {chapter}: {topic}...")
    extracted_data = extract_questions(rag_pipeline, chapter, topic)

    # 3. Save the output
    if extracted_data and isinstance(extracted_data, list):
        output_filename = topic.lower().replace(" ", "_") + ".md"
        output_path = OUTPUT_DIR / output_filename

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Questions for Chapter {chapter}: {topic}\n\n")
            for i, question in enumerate(extracted_data, 1):
                f.write(f"**Question {i}:**\n")
                f.write(f"```latex\n{question}\n```\n")
                # Also render it for easy viewing in Markdown
                f.write(f"$${question}$$ \n\n") # Using $$ for better rendering
        
        typer.secho(f"Successfully extracted {len(extracted_data)} questions.", fg=typer.colors.GREEN)
        typer.secho(f"Output saved to: {output_path}", fg=typer.colors.CYAN)
    else:
        typer.secho("Failed to extract questions or received an empty/invalid list from the AI.", fg=typer.colors.YELLOW)


if __name__ == "__main__":
    app()