import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: mkreadme <your_script.py>")
        sys.exit(1)

    script_path = sys.argv[1]
    print(f"Generating README.md for {script_path}...")
    # aqui futuramente você implementa a lógica de gerar o README
    # por enquanto só gera um arquivo básico
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(f"# Auto-generated README\n\nFrom script: `{script_path}`\n")

    print("README.md created successfully!")
