# aegis/cli.py

import typer
import json
import csv
import os
from typing import Optional, List, Dict, Any
from io import BytesIO

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import plotly.express as px
import pandas as pd

from aegis.core.library import PromptLibrary
from aegis.core.connectors import (
    ModelConnector,
    UserProvidedGeminiConnector,
    OpenAIConnector,
    AnthropicConnector,
    OpenRouterConnector,
    CustomEndpointConnector
)
from aegis.core.models import ModelResponse, AnalysisResult
from aegis.core.analyzer import LLMAnalyzer
from aegis.core.reporting import generate_pdf_report

# Initialize Typer app and Rich console
app = typer.Typer(
    name="aegisred",
    help="Aegis: An Open-Source LLM Red Teaming & Evaluation Framework",
    add_completion=False,
)
console = Console()

def get_connector(model_identifier: str) -> ModelConnector:
    """
    Initializes and returns the appropriate model connector based on the identifier.
    It reads API keys from environment variables.
    """
    parts = model_identifier.lower().split('/')
    provider = parts[0]
    model_name = "/".join(parts[1:])

    try:
        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key: raise ValueError("GEMINI_API_KEY not found in environment variables.")
            return UserProvidedGeminiConnector(model_name=model_name, api_key=api_key)
        
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key: raise ValueError("OPENAI_API_KEY not found in environment variables.")
            return OpenAIConnector(model_name=model_name, api_key=api_key)

        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key: raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
            return AnthropicConnector(model_name=model_name, api_key=api_key)

        elif provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key: raise ValueError("OPENROUTER_API_KEY not found in environment variables.")
            return OpenRouterConnector(model_name=model_name, api_key=api_key)
        
        else:
            console.print(f"[bold red]Error: Provider '{provider}' is not supported via CLI.[/bold red]")
            raise typer.Exit(code=1)
            
    except ValueError as e:
        console.print(f"[bold red]Initialization Error for {provider}: {e}[/bold red]")
        raise typer.Exit(code=1)

def display_single_result(response: ModelResponse, analysis: AnalysisResult):
    """Renders a detailed table and panels for a single evaluation result."""
    table = Table(title="Aegis Evaluation Result", show_header=True, header_style="bold magenta", box=None)
    table.add_column("Field", style="dim", width=20)
    table.add_column("Value")

    color = "white"
    if analysis.classification.name == "NON_COMPLIANT": color = "bold red"
    elif analysis.classification.name == "COMPLIANT": color = "bold green"
    elif analysis.classification.name == "PARTIAL_COMPLIANCE": color = "bold yellow"

    table.add_row("Prompt ID", response.prompt_id)
    table.add_row("Model Name", response.model_name)
    table.add_row(f"[{color}]Classification[/{color}]", f"[{color}]{analysis.classification.name}[/{color}]")
    table.add_row("Aegis Risk Score (ARS)", f"{analysis.aegis_risk_score:.1f} / 100.0")

    console.print(table)
    console.print(Panel(response.output_text, title="[cyan]Model Output[/cyan]", border_style="cyan", expand=False))
    console.print(Panel(analysis.explanation, title="[cyan]Analysis Explanation[/cyan]", border_style="cyan", expand=False))

def save_results_to_json(results: List[Dict[str, Any]], filepath: str):
    """Saves a list of evaluation results to a JSON file."""
    export_data = []
    for result in results:
        export_data.append({
            "prompt_id": result["prompt"].id,
            "category": result["prompt"].category,
            "prompt_text": result["prompt"].prompt_text,
            "model_name": result["response"].model_name,
            "model_output": result["response"].output_text,
            "classification": result["analysis"].classification.name,
            "aegis_risk_score": result["analysis"].aegis_risk_score,
            "explanation": result["analysis"].explanation,
        })
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)

def save_results_to_csv(results: List[Dict[str, Any]], filepath: str):
    """Saves a list of evaluation results to a CSV file."""
    headers = [
        "prompt_id", "category", "prompt_text", "model_name", "model_output",
        "classification", "aegis_risk_score", "explanation"
    ]
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for result in results:
            writer.writerow({
                "prompt_id": result["prompt"].id,
                "category": result["prompt"].category,
                "prompt_text": result["prompt"].prompt_text,
                "model_name": result["response"].model_name,
                "model_output": result["response"].output_text,
                "classification": result["analysis"].classification.name,
                "aegis_risk_score": result["analysis"].aegis_risk_score,
                "explanation": result["analysis"].explanation,
            })

@app.command()
def evaluate(
    prompt_id: str = typer.Option(..., "--prompt-id", "-p", help="The ID of the prompt to run."),
    model: str = typer.Option(..., "--model", "-m", help="Model to evaluate (e.g., 'openrouter/google/gemma-2-9b-it:free')."),
):
    """Run a single adversarial prompt evaluation against a specified model."""
    console.print(f"[bold cyan]🚀 Starting Aegis Evaluation...[/bold cyan]")
    library, analyzer = PromptLibrary(), LLMAnalyzer()
    library.load_prompts()
    
    target_prompt = next((p for p in library.get_all() if p.id == prompt_id), None)
    if not target_prompt:
        console.print(f"[bold red]Error: Prompt with ID '{prompt_id}' not found.[/bold red]")
        raise typer.Exit(code=1)
        
    console.print(f"✅ Found Prompt [bold]'{prompt_id}'[/bold].")
    console.print(f"✅ Initializing and sending to [bold]'{model}'[/bold]...")
    
    connector = get_connector(model)
    response = connector.send_prompt(target_prompt)
    
    console.print("✅ Response received.")
    console.print("✅ Analyzing response with Aegis evaluator...")
    
    analysis_result = analyzer.analyze(response, target_prompt)
    
    console.print("✅ Analysis complete.")
    display_single_result(response, analysis_result)

@app.command(name="batch-evaluate")
def batch_evaluate(
    category: str = typer.Option(..., "--category", "-c", help="The category of prompts to evaluate."),
    model: str = typer.Option(..., "--model", "-m", help="Model to evaluate."),
    output_json: Optional[str] = typer.Option(None, "--output-json", help="Path to save results as a JSON file."),
    output_csv: Optional[str] = typer.Option(None, "--output-csv", help="Path to save results as a CSV file."),
    output_pdf: Optional[str] = typer.Option(None, "--output-pdf", help="Path to save a PDF report."),
):
    """Run a batch evaluation and optionally save the results to a file."""
    console.print(f"[bold cyan]🚀 Starting Batch Evaluation for category '{category}'...[/bold cyan]")
    
    library, analyzer = PromptLibrary(), LLMAnalyzer()
    library.load_prompts()
    
    prompts_to_run = library.filter_by_category(category)
    if not prompts_to_run:
        console.print(f"[bold red]Error: No prompts found for category '{category}'.[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"✅ Found {len(prompts_to_run)} prompts. Initializing connector for [bold]'{model}'[/bold]...")
    connector = get_connector(model)
    
    results = []
    with Progress() as progress:
        task = progress.add_task(f"[green]Evaluating {category}...", total=len(prompts_to_run))
        for prompt in prompts_to_run:
            response = connector.send_prompt(prompt)
            analysis = analyzer.analyze(response, prompt)
            results.append({"prompt": prompt, "response": response, "analysis": analysis})
            progress.update(task, advance=1, description=f"[green]Evaluated {prompt.id}")

    # --- Display and Process Results ---
    summary_table = Table(title=f"Batch Evaluation Summary: {category}", show_header=True, header_style="bold blue")
    summary_table.add_column("Prompt ID", style="dim", width=12)
    summary_table.add_column("Classification", style="bold", width=20)
    summary_table.add_column("Risk Score (ARS)", width=15)
    summary_table.add_column("Model Output Snippet", no_wrap=False)

    total_score = 0
    classifications = []
    for result in results:
        total_score += result["analysis"].aegis_risk_score
        classifications.append(result["analysis"].classification.name)
        
        color = "white"
        if result["analysis"].classification.name == "NON_COMPLIANT": color = "red"
        elif result["analysis"].classification.name == "COMPLIANT": color = "green"
        elif result["analysis"].classification.name == "PARTIAL_COMPLIANCE": color = "yellow"
        
        output_snippet = result["response"].output_text[:100] + "..." if len(result["response"].output_text) > 100 else result["response"].output_text
        
        summary_table.add_row(
            result["prompt"].id,
            f"[{color}]{result['analysis'].classification.name}[/{color}]",
            f"{result['analysis'].aegis_risk_score:.1f}",
            output_snippet
        )
    
    console.print(summary_table)
    average_score = total_score / len(results) if results else 0
    console.print(Panel(f"Average Aegis Risk Score for this category: [bold cyan]{average_score:.2f}[/bold cyan]", title="Overall Result"))

    # --- Handle Exporting ---
    if output_json:
        save_results_to_json(results, output_json)
        console.print(f"✅ Full results saved to [bold green]{output_json}[/bold green]")
    if output_csv:
        save_results_to_csv(results, output_csv)
        console.print(f"✅ Full results saved to [bold green]{output_csv}[/bold green]")
    if output_pdf:
        console.print(f"🎨 Generating PDF report...")
        chart_image_buffer = BytesIO()
        try:
            classification_counts = pd.Series(classifications).value_counts()
            fig_bar = px.bar(
                classification_counts, x=classification_counts.index, y=classification_counts.values,
                labels={'x': 'Classification', 'y': 'Count'}, title="Classification Breakdown",
                color=classification_counts.index,
                color_discrete_map={
                    'NON_COMPLIANT': '#d63031', 'COMPLIANT': '#00b894', 'PARTIAL_COMPLIANCE': '#fdcb6e',
                    'AMBIGUOUS': '#636e72', 'ERROR': '#2d3436'
                }
            )
            fig_bar.write_image(chart_image_buffer, format="png")
            
            pdf_buffer = BytesIO()
            generate_pdf_report(results, pdf_buffer, chart_image_buffer)
            
            with open(output_pdf, "wb") as f:
                f.write(pdf_buffer.getvalue())
                
            console.print(f"✅ PDF report saved to [bold green]{output_pdf}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error generating PDF report: {e}[/bold red]")
            console.print("[bold yellow]Please ensure you have 'kaleido' installed (`pip install kaleido`)[/bold yellow]")

if __name__ == "__main__":
    app()
