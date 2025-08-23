import subprocess
import sys
import shlex

from typer import Option, Typer

def check_poetry_output(name: str, command: str, limit: int) -> bool:
    result = subprocess.run(
        shlex.split(command), 
        capture_output=True, text=True
    )
    outdated_packages = [package for package in result.stdout.strip().split("\n") if package != ""] 
    outdated_count = len(outdated_packages)

    print(f"Outdated {name} dependencies: {outdated_count}/{limit}")
    for package in outdated_packages:
        print(f"\t{package}")

    if outdated_count > limit:
        print(f"Too many outdated {name} dependencies (limit is {limit}). Check failed.")
        return False
    else:
        return True

def main():
    app = Typer()
    @app.command()
    def check_dependencies(
            top_level_limit: int = Option(10, help="Limit for top-level dependencies"),
            all_limit: int = Option(20, help="Limit for all dependencies (including transitive)"),
                           ):
        """Check for outdated dependencies."""
        top_level_result = check_poetry_output("top level", "poetry show --outdated --top-level", top_level_limit)
        all_result = check_poetry_output("all", "poetry show --outdated", all_limit)
        if top_level_result and all_result:
            print("All dependency checks passed.")
            sys.exit(0)
        else:
            sys.exit(1)
    app()

if __name__ == "__main__":
    main()