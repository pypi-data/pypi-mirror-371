import argparse
import sys
import os
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

# Initialize the rich console for formatted output
console = Console()

# Internal Knowledge Base for performance deltas
# This is the "wizardry" data based on research and benchmarks
PERFORMANCE_DELTAS = {
    (3, 10): 0.30,  # Based on the 3.10 -> 3.13 delta (from article)
    (3, 11): 0.15,  # Based on the 3.11 -> 3.13 delta
    (3, 12): 0.08,
    # Based on benchmarks (see https://en.lewoniewski.info/2024/python-3-12-vs-python-3-13-performance-testing/)
}


def find_projects(scan_dir):
    """Recursively finds project files like Dockerfile and environment.yaml."""
    project_files = []
    for root, _, files in os.walk(scan_dir):
        for file in files:
            if file in ['Dockerfile', 'environment.yaml']:
                project_files.append(os.path.join(root, file))
    return project_files


def get_python_version_from_file(file_path):
    """Attempts to find a Python version from a project file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Simplified detection for MVP
            if 'FROM python:' in content:
                # Dockerfile
                version_str = content.split('FROM python:')[1].split('\n')[0].strip()
                if version_str.count('.') >= 1:
                    major, minor = map(int, version_str.split('.')[:2])
                    return major, minor
            elif 'python=' in content:
                # Conda/Snakemake
                version_str = content.split('python=')[1].split('\n')[0].strip()
                if version_str.count('.') >= 1:
                    major, minor = map(int, version_str.split('.')[:2])
                    return major, minor
    except (IOError, ValueError):
        pass
    return None, None


def check_dependencies():
    """Checks for broken dependencies using pip check."""
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'check'],
            check=True,
            capture_output=True,
            text=True
        )
        return "No broken dependencies found. ✅"
    except subprocess.CalledProcessError as e:
        return f"Dependency issues found:\n{e.stdout} ⚠️"


def calculate_savings(version, monthly_bill, compute_percentage):
    """Calculates estimated annual savings based on version and bill."""
    gain = PERFORMANCE_DELTAS.get(version, 0)
    if gain > 0:
        annual_bill = monthly_bill * 12
        compute_cost = annual_bill * compute_percentage
        annual_savings = compute_cost * gain
        return annual_savings, gain
    return None, 0


def run():
    """
    Main entry point for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description="Audit Python projects for upgrade potential and estimate cloud cost savings."
    )
    parser.add_argument(
        "--monthly-bill",
        type=float,
        required=True,
        help="Your company's average monthly cloud bill in dollars (e.g., 2300000)."
    )
    parser.add_argument(
        "--compute-percentage",
        type=float,
        default=0.5,
        help="The percentage of your bill that is compute-related (e.g., 0.6 for 60%%). Defaults to 0.5."
    )
    parser.add_argument(
        "--scan-dir",
        type=str,
        default='.',
        help="The directory to scan for Python projects. Defaults to the current directory."
    )
    args = parser.parse_args()

    # --- Step 1: Automated Project Scanning ---
    console.print(Panel("[bold green]pyboost: Scanning for Projects...[/]", expand=False))
    found_files = find_projects(args.scan_dir)

    if not found_files:
        console.print("[bold red]No Dockerfile or environment.yaml files found.[/]")
        sys.exit(0)

    # --- Step 2: Detailed and Visualized Report ---
    table = Table(title="Upgrade Audit Report", style="bold")
    table.add_column("Project File", justify="left")
    table.add_column("Detected Version", justify="center")
    table.add_column("Potential Savings", justify="right")
    table.add_column("Upgrade Recommendation", justify="center")

    total_savings = 0.0

    for fpath in found_files:
        major, minor = get_python_version_from_file(fpath)
        if major is None:
            continue

        savings, gain = calculate_savings((major, minor), args.monthly_bill, args.compute_percentage)

        savings_text = f"${savings:,.2f} Annually ({gain:.0%} boost)" if savings else "No data"
        if major < 3 or minor < 12:
            recommendation = f"Upgrade to Python 3.13"
        else:
            recommendation = "Version is recent"

        if savings:
            total_savings += savings
            savings_style = "bold green"
        else:
            savings_style = "dim"

        table.add_row(fpath, f"[bold]{major}.{minor}[/]", f"[{savings_style}]{savings_text}[/]", recommendation)

    console.print(table)

    # --- Step 3: Overall Summary & Actions ---
    console.print(Panel(
        f"[bold green]✨ Total Potential Annual Savings:[/][bold white] ${total_savings:,.2f}[/]",
        title="Summary",
        expand=False
    ))

    console.print("\n[bold cyan]🛠 Actionable Recommendations:[/]")
    console.print("- Run `pyboost` in your CI/CD pipeline to prevent technical debt. ")

    console.print("\n[bold cyan]Dependency Check:[/]")
    dependency_status = check_dependencies()
    console.print(dependency_status)

    if dependency_status.startswith("Dependency issues"):
        console.print(
            "\n[bold yellow]💡 Tip:[/] Resolve these dependency issues before upgrading to ensure a smooth transition.")


if __name__ == "__main__":
    run()