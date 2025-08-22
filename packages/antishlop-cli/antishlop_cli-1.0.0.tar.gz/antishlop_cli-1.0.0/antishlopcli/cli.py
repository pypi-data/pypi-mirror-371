#!/usr/bin/env python3
import os
import sys
import json
import argparse
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from colorama import init
from antishlopcli.agent import Agent

init(autoreset=True)
console = Console()

class SecurityScanner:
    def __init__(self, path):
        self.path = Path(path)
        self.reports = []
        self.code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php', '.c', '.cpp', '.cs']
        self.ignore_dirs = ['node_modules', '.git', 'venv', '__pycache__', 'dist', 'build', '.venv', 'env']
        
    def get_files(self):
        files = []
        
        # Check if path is a file or directory
        if self.path.is_file():
            # Single file - check if it's a code file
            if any(str(self.path).endswith(ext) for ext in self.code_extensions):
                files.append(self.path)
            else:
                console.print(f"[yellow]Warning: {self.path.name} is not a recognized code file[/yellow]")
                # Still add it if user specified it directly
                files.append(self.path)
        else:
            # Directory - walk through all files
            for root, dirs, filenames in os.walk(self.path):
                dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
                for filename in filenames:
                    if any(filename.endswith(ext) for ext in self.code_extensions):
                        files.append(Path(root) / filename)
        return files
    
    def scan(self):
        import time
        import threading
        from rich.live import Live
        
        files = self.get_files()
        total = len(files)
        
        if total == 0:
            console.print("[yellow]No code files found to scan![/yellow]")
            return []
        
        # Show appropriate message for file vs directory
        if self.path.is_file():
            scan_msg = f"Scanning file: {self.path.name}"
        else:
            scan_msg = f"Scanning {total} files in {self.path}"
            
        console.print(Panel.fit(
            f"[bold cyan]AntiShlop Security Scanner[/bold cyan]\n"
            f"[dim]{scan_msg}[/dim]",
            border_style="cyan"
        ))
        console.print()
        
        total_tokens = 0
        
        for i, file_path in enumerate(files, 1):
            # For single file, use the filename; for directory scan, use relative path
            if self.path.is_file():
                rel_path = self.path.name
            else:
                rel_path = file_path.relative_to(self.path)
            start_time = time.time()
            current_tokens = 0
            agent_done = threading.Event()
            
            # Show current file status
            if self.path.is_file():
                # For single file, don't show relative path
                console.print(f"[cyan]Scanning:[/cyan] {file_path.name}")
            else:
                console.print(f"[{i}/{total}] [cyan]Scanning:[/cyan] {rel_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Token callback to update live display
                def update_tokens(tokens):
                    nonlocal current_tokens
                    current_tokens = tokens
                
                # Status callback for iteration updates
                iteration_status = ""
                
                def update_status(status):
                    nonlocal iteration_status
                    if status.startswith("iteration_"):
                        iter_num = status.split("_")[1]
                        console.print(f"      [magenta]↻[/magenta] Deeper analysis needed - starting iteration {iter_num}")
                
                # Run agent in thread
                report = None
                tokens_used = 0
                
                def run_agent():
                    nonlocal report, tokens_used
                    report, tokens_used = Agent(content, token_callback=update_tokens, status_callback=update_status)
                    agent_done.set()
                
                agent_thread = threading.Thread(target=run_agent)
                agent_thread.start()
                
                # Live update while agent runs
                with Live(console=console, refresh_per_second=10) as live:
                    while not agent_done.is_set():
                        elapsed = time.time() - start_time
                        live.update(f"      [yellow]⟳[/yellow] Analyzing... [cyan]{current_tokens:,} tokens[/cyan] • [dim]{elapsed:.1f}s[/dim]")
                        time.sleep(0.1)
                
                agent_thread.join()
                elapsed = time.time() - start_time
                
                # Update with actual results
                console.print(f"      [green]✓[/green] Complete in {elapsed:.1f}s • {tokens_used:,} tokens")
                
                total_tokens += tokens_used
                
                self.reports.append({
                    'file': str(rel_path),
                    'status': 'scanned',
                    'report': report,
                    'scan_time': elapsed,
                    'tokens_used': tokens_used
                })
                
            except Exception as e:
                elapsed = time.time() - start_time
                console.print(f"      [red]✗[/red] Error: {str(e)[:50]}...")
                
                self.reports.append({
                    'file': str(rel_path),
                    'status': 'error',
                    'report': str(e),
                    'scan_time': elapsed,
                    'tokens_used': 0
                })
        
        console.print(f"\n[bold]Total tokens used: {total_tokens:,}[/bold]")
        return self.reports
    
    def display_results(self):
        if not self.reports:
            return
        
        console.print("\n[bold green]✓ Scan Complete![/bold green]\n")
        
        table = Table(title="Scan Summary", show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan", no_wrap=False)
        table.add_column("Status", justify="center")
        table.add_column("Issues", justify="center")
        
        issues_count = 0
        error_count = 0
        
        for report in self.reports:
            status = report['status']
            if status == 'error':
                status_display = "[red]ERROR[/red]"
                error_count += 1
            else:
                status_display = "[green]✓[/green]"
                if report['report'] and "no vulnerabilities" not in report['report'].lower() and "no security vulnerabilities" not in report['report'].lower():
                    issues_count += 1
            
            has_issues = "Yes" if report['report'] and "no security vulnerabilities" not in report['report'].lower() and "no vulnerabilities" not in report['report'].lower() else "No"
            table.add_row(report['file'], status_display, has_issues)
        
        console.print(table)
        
        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"  Total files: {len(self.reports)}")
        console.print(f"  Files with issues: {issues_count}")
        console.print(f"  Scan errors: {error_count}")
        
        # Calculate total time and tokens
        total_time = sum(r.get('scan_time', 0) for r in self.reports)
        total_tokens = sum(r.get('tokens_used', 0) for r in self.reports)
        
        console.print(f"  Total scan time: {total_time:.1f}s")
        console.print(f"  Total tokens used: {total_tokens:,}")
        
        # Display detailed findings
        console.print("\n" + "="*60)
        console.print("[bold cyan]DETAILED FINDINGS[/bold cyan]")
        console.print("="*60)
        
        for report in self.reports:
            if report['status'] == 'error':
                console.print(f"\n[red]❌ {report['file']}[/red]")
                console.print(f"[dim]Error: {report['report']}[/dim]")
            elif report['report'] and "no vulnerabilities" not in report['report'].lower() and "no security vulnerabilities" not in report['report'].lower():
                console.print(f"\n[yellow]⚠️  {report['file']}[/yellow]")
                console.print(Panel(report['report'], border_style="yellow", padding=(1, 2)))
            else:
                console.print(f"\n[green]✅ {report['file']}[/green]")
                console.print("[dim]No issues found[/dim]")
    
    def save_report(self, output_file=None):
        if not output_file:
            output_file = f"{self.path.name}_security_report.json"
        
        summary = {
            'path': str(self.path),
            'total_files': len(self.reports),
            'detailed_reports': self.reports
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        console.print(f"\n[green]Report saved to:[/green] {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='AntiShlop - Security vulnerability scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  antishlop .                    # Scan current directory
  antishlop /path/to/project     # Scan specific project directory
  antishlop /path/to/file.py     # Scan a single file
  antishlop . -o report.json     # Save report to specific file
        '''
    )
    
    parser.add_argument('path', help='Path to file or directory to scan')
    parser.add_argument('-o', '--output', help='Output file for JSON report')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode, minimal output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        console.print(f"[red]Error: Path '{args.path}' does not exist[/red]")
        sys.exit(1)
    
    scanner = SecurityScanner(args.path)
    scanner.scan()
    
    if not args.quiet:
        scanner.display_results()
    
    if args.output:
        scanner.save_report(args.output)

if __name__ == "__main__":
    main()