#!/usr/bin/env python3
"""Simple CLI interface for DuoTalk"""

import asyncio
import typer
from typing import Optional
from rich.console import Console

app = typer.Typer(
    help="DuoTalk - AI conversation platform",
    no_args_is_help=True,
    rich_markup_mode="rich"
)

console = Console()

# Try to import enhanced features, fall back to basic if not available
try:
    from duotalk.enhanced import (
        quick_debate, quick_roundtable, quick_friendly, quick_interview, quick_panel,
        sync_run, get_available_personas
    )
    _enhanced_available = True
except ImportError:
    _enhanced_available = False
    # Import the working voice system
    import subprocess
    import sys
    import os

def show_banner(conversation_type: str, topic: str, agents: int):
    """Show conversation banner"""
    console.print(f"\n[bold blue]🎭 DuoTalk {conversation_type.title()}[/bold blue]")
    console.print(f"[cyan]Topic:[/cyan] {topic}")
    console.print(f"[cyan]Agents:[/cyan] {agents}")
    console.print(f"[dim]Enhanced mode: {'✓' if _enhanced_available else '✗'}[/dim]\n")

def run_voice_conversation(topic: str, mode: str = "debate", livekit_mode: str = "console"):
    """Run voice conversation using the existing dual_voice_agents.py"""
    try:
        console.print(f"[green]🎙️ Starting voice conversation about: {topic}[/green]")
        console.print(f"[cyan]Mode: {mode}[/cyan]")
        console.print(f"[dim]LiveKit mode: {livekit_mode}[/dim]")
        console.print("[dim]Setting up LiveKit session...[/dim]")
        
        # Set environment variables for the voice script
        env = os.environ.copy()
        env['DUOTALK_TOPIC'] = topic
        env['DUOTALK_MODE'] = mode
        
        # Run the dual_voice_agents.py script with specified mode
        result = subprocess.run([
            sys.executable, "dual_voice_agents.py", livekit_mode
        ], env=env, cwd=os.getcwd())
        
        return result.returncode == 0
                
    except Exception as e:
        console.print(f"[red]Error starting voice conversation: {e}[/red]")
        return False

@app.command()
def debate(
    topic: str = typer.Option(..., "-t", "--topic", help="Debate topic"),
    turns: int = typer.Option(10, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    personas: Optional[str] = typer.Option(None, "-p", "--personas", help="Comma-separated personas"),
    mode: str = typer.Option("console", "--mode", help="LiveKit mode: console, dev, or start")
):
    """Start a debate between two opposing viewpoints."""
    show_banner("debate", topic, 2)
    
    try:
        if _enhanced_available:
            if personas:
                selected_personas = personas.split(",")[:2]
            else:
                selected_personas = ["optimist", "skeptic"]
            
            runner = quick_debate(topic, pro_agent=selected_personas[0], con_agent=selected_personas[1] if len(selected_personas) > 1 else "skeptic", max_turns=turns, voice=voice)
            if voice:
                console.print("🎙️ Starting voice conversation...")
            sync_run(runner)
        else:
            # Use the existing voice system
            if voice:
                console.print("[blue]🎙️ Using built-in voice system...[/blue]")
                success = run_voice_conversation(topic, mode="debate", livekit_mode=mode)
                if not success:
                    console.print("[red]Voice conversation failed to start[/red]")
            else:
                console.print("[yellow]Voice disabled. No fallback text conversation available.[/yellow]")
                console.print("[dim]Tip: Use --voice to enable voice conversation[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def roundtable(
    topic: str = typer.Option(..., "-t", "--topic", help="Discussion topic"),
    agents: int = typer.Option(3, "-a", "--agents", help="Number of participants (default: 3)"),
    turns: int = typer.Option(12, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    personas: Optional[str] = typer.Option(None, "-p", "--personas", help="Comma-separated personas"),
    mode: str = typer.Option("console", "--mode", help="LiveKit mode: console, dev, or start")
):
    """Start a roundtable discussion with multiple participants."""
    show_banner("roundtable", topic, agents)
    
    try:
        if _enhanced_available:
            if personas:
                selected_personas = personas.split(",")[:agents]
            else:
                selected_personas = ["optimist", "analyst", "creative"][:agents]
            
            runner = quick_roundtable(topic, agents=selected_personas, max_turns=turns, voice=voice)
            if voice:
                console.print("🎙️ Starting voice conversation...")
            sync_run(runner)
        else:
            # Use the existing voice system - roundtable will use friendly mode
            if voice:
                console.print("[blue]🎙️ Using built-in voice system...[/blue]")
                success = run_voice_conversation(topic, mode="friendly", livekit_mode=mode)
                if not success:
                    console.print("[red]Voice conversation failed to start[/red]")
            else:
                console.print("[yellow]Voice disabled. No fallback text conversation available.[/yellow]")
                console.print("[dim]Tip: Use --voice to enable voice conversation[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def chat(
    topic: str = typer.Option(..., "-t", "--topic", help="Chat topic"),
    agents: int = typer.Option(2, "-a", "--agents", help="Number of agents (default: 2)"),
    turns: int = typer.Option(10, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    personas: Optional[str] = typer.Option(None, "-p", "--personas", help="Comma-separated personas"),
    mode: str = typer.Option("console", "--mode", help="LiveKit mode: console, dev, or start")
):
    """Start a friendly chat conversation."""
    show_banner("friendly chat", topic, agents)
    
    try:
        if _enhanced_available:
            if personas:
                selected_personas = personas.split(",")[:agents]
            else:
                selected_personas = ["optimist", "enthusiast"] if agents == 2 else ["optimist", "enthusiast", "creative"][:agents]
            
            runner = quick_friendly(topic, agents=selected_personas, max_turns=turns, voice=voice)
            if voice:
                console.print("🎙️ Starting voice conversation...")
            sync_run(runner)
        else:
            # Use the existing voice system
            if voice:
                console.print("[blue]🎙️ Using built-in voice system...[/blue]")
                success = run_voice_conversation(topic, mode="friendly", livekit_mode=mode)
                if not success:
                    console.print("[red]Voice conversation failed to start[/red]")
            else:
                console.print("[yellow]Voice disabled. No fallback text conversation available.[/yellow]")
                console.print("[dim]Tip: Use --voice to enable voice conversation[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def interview(
    topic: str = typer.Option(..., "-t", "--topic", help="Interview topic"),
    turns: int = typer.Option(10, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    interviewer: str = typer.Option("journalist", "--interviewer", help="Interviewer persona"),
    interviewee: str = typer.Option("expert", "--interviewee", help="Interviewee persona"),
    mode: str = typer.Option("console", "--mode", help="LiveKit mode: console, dev, or start")
):
    """Start an interview conversation."""
    show_banner("interview", topic, 2)
    
    try:
        if _enhanced_available:
            runner = quick_interview(topic, interviewer=interviewer, interviewee=interviewee, max_turns=turns, voice=voice)
            if voice:
                console.print("🎙️ Starting voice conversation...")
            sync_run(runner)
        else:
            # Use the existing voice system
            if voice:
                console.print("[blue]🎙️ Using built-in voice system...[/blue]")
                success = run_voice_conversation(topic, mode="friendly", livekit_mode=mode)
                if not success:
                    console.print("[red]Voice conversation failed to start[/red]")
            else:
                console.print("[yellow]Voice disabled. No fallback text conversation available.[/yellow]")
                console.print("[dim]Tip: Use --voice to enable voice conversation[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def panel(
    topic: str = typer.Option(..., "-t", "--topic", help="Panel discussion topic"),
    agents: int = typer.Option(4, "-a", "--agents", help="Number of experts (default: 4)"),
    turns: int = typer.Option(15, "-n", "--turns", help="Max conversation turns"),
    voice: bool = typer.Option(True, "--voice/--no-voice", help="Enable voice synthesis"),
    personas: Optional[str] = typer.Option(None, "-p", "--personas", help="Comma-separated personas")
):
    """Start an expert panel discussion."""
    show_banner("expert panel", topic, agents)
    
    try:
        if _enhanced_available:
            if personas:
                selected_personas = personas.split(",")[:agents]
            else:
                # Default expert personas for panels
                expert_personas = ["educator", "analyst", "scientist", "entrepreneur", "theorist"]
                selected_personas = expert_personas[:agents]
            
            runner = quick_panel(topic, agents=selected_personas, max_turns=turns, voice=voice)
            if voice:
                console.print("🎙️ Starting voice conversation...")
            sync_run(runner)
        else:
            console.print("[red]Enhanced features required for this command. Please check your installation.[/red]")
            console.print("[dim]Tip: Try running 'pip install duotalk[enhanced]' or similar[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@app.command()
def personas():
    """List all available personas."""
    if _enhanced_available:
        try:
            available = get_available_personas()
            console.print("[bold]Available Personas:[/bold]")
            for persona in available:
                console.print(f"  • [cyan]{persona}[/cyan]")
        except Exception as e:
            console.print(f"[red]Error getting personas: {e}[/red]")
    else:
        console.print("[bold]Default Personas:[/bold]")
        default_personas = [
            "optimist", "skeptic", "analyst", "creative", "enthusiast",
            "expert", "journalist", "educator", "scientist", "entrepreneur",
            "theorist", "researcher", "strategist", "philosopher"
        ]
        for persona in default_personas:
            console.print(f"  • [cyan]{persona}[/cyan]")

if __name__ == "__main__":
    app()
