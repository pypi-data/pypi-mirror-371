import requests
import os
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import pyperclip

console = Console()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_gemini_response(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def main():
    global GEMINI_API_KEY
    if not GEMINI_API_KEY:
        GEMINI_API_KEY = console.input("[bold yellow]YOU_API_KEY_GEMINI:[/bold yellow] ")
        os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

    console.print(Panel("[bold green]Chào mừng bạn đến với Qelrix CLI - Trợ lý Gemini AI của bạn![/bold green]", expand=False))
    console.print("[bold blue]Gõ 'exit' để thoát.[/bold blue]")

    while True:
        user_input = console.input("[bold cyan]Bạn:[/bold cyan] ")
        if user_input.lower() == 'exit':
            break

        with console.status("[bold green]Gemini đang suy nghĩ...[/bold green]", spinner="dots"):
            response_text = get_gemini_response(user_input)

        if response_text.startswith("Error:"):
            console.print(Panel(f"[bold red]{response_text}[/bold red]", expand=False))
        else:
            # Check if the response contains code blocks
            if '```' in response_text:
                parts = response_text.split('```')
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # This is a code block
                        lang_and_code = part.split("\n", 1)
                        if len(lang_and_code) > 1:
                            lang = lang_and_code[0].strip()
                            code = lang_and_code[1].strip()
                            syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
                            console.print(Panel(syntax, title=f"[bold yellow]Code ({lang}) - Click để copy[/bold yellow]", border_style="yellow"))
                            # This is where the click-to-copy magic happens (simulated)
                            # In a real terminal, this would require a more complex solution
                            # For now, we'll just print a message indicating it's copied
                            try:
                                pyperclip.copy(code)
                                console.print("[bold green]Mã đã được sao chép vào clipboard![/bold green]")
                            except pyperclip.PyperclipException:
                                console.print("[bold red]Không thể sao chép mã vào clipboard. Vui lòng cài đặt xclip hoặc xsel.[/bold red]")
                        else:
                            console.print(Panel(f"[bold white]{part}[/bold white]", expand=False))
                    else:
                        console.print(Panel(f"[bold white]{part}[/bold white]", expand=False))
            else:
                console.print(Panel(f"[bold white]{response_text}[/bold white]", expand=False))

if __name__ == "__main__":
    main()


