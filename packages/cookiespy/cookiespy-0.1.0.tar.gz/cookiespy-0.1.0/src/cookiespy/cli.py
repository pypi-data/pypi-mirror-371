import argparse
import requests
from rich.console import Console
from urllib.parse import urlparse
from cookiespy.exporter import export_to_json, export_to_csv


console = Console()

def validate_url(url: str) -> str:
    """Validate URL format, raise ValueError if invalid"""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return url

def fetch_cookies(url: str) -> dict:
    """Fetch cookies from target URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.cookies.get_dict()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch cookies from {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="CookieSpy - Inspect and export cookies")
    parser.add_argument("url", help="Target URL to fetch cookies from")
    parser.add_argument("--export", choices=["json", "csv"], help="Export format")
    parser.add_argument("--output", help="Output file name (default: cookies.json / cookies.csv)", default=None)
    args = parser.parse_args()

    try:
        target_url = validate_url(args.url)
        console.print(f"[bold green]Fetching cookies from:[/bold green] {target_url}")
        cookies = fetch_cookies(target_url)

        if not cookies:
            console.print("[red]No cookies found.[/red]")
        else:
            console.print(f"[cyan]Cookies found:[/cyan] {cookies}")

        if args.export:
            filename = args.output or f"cookies.{args.export}"
            if args.export == "json":
                export_to_json(cookies, filename)
            elif args.export == "csv":
                export_to_csv(cookies, filename)
            console.print(f"[yellow]Exported cookies to {filename}[/yellow]")

    except Exception as e:
        console.print(f"[red][!] {e}[/red]")
        raise

if __name__ == "__main__":
    main()
