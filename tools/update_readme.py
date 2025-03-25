from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader


def main():
    root_dir = Path(__file__).resolve().parent.parent

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(f"{root_dir}/yt_feed/templates"))
    template = env.get_template("README.md.jinja")

    # Render and merge templates
    rendered_readme = template.render()

    # Save to README.md
    with open(root_dir / "README.md", "w", newline="\n") as f:
        f.write(f"{rendered_readme}\n")


if __name__ == "__main__":
    main()
