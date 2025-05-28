import sys
import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext, messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parser.parser import tokenize_output, parse_tokens, generate_c_code


def compile_lexer():
    lexer_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lexer', 'python_lexer.l'))
    if not os.path.exists(lexer_file):
        messagebox.showerror("Error", f"Lexer file not found at: {lexer_file}")
        sys.exit(1)
    
    lexer_output = os.path.join(os.path.dirname(lexer_file), "lex.yy.c")
    exe_file = "lexer.exe"
    
    try:
        if not os.path.exists(exe_file) or os.path.getmtime(lexer_file) > os.path.getmtime(exe_file):
            print("Compiling lexer...")
            subprocess.run(["flex", "-o", lexer_output, lexer_file], check=True)
            subprocess.run(["gcc", lexer_output, "-o", exe_file], check=True)
            print("Lexer compiled successfully.")
    except FileNotFoundError as e:
        messagebox.showerror("Error", f"Compilation failed: {e}\nEnsure Flex and GCC are installed.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to compile lexer: {e}")
        sys.exit(1)


def validate_input(input_code):
    lines = input_code.splitlines()
    for i, line in enumerate(lines, 1):
        if '\t' in line:
            messagebox.showerror("Input Error", f"Tab detected at line {i}. Use 4 spaces for indentation.")
            return False
        if any(ord(c) >= 128 for c in line):
            messagebox.showerror("Input Error", f"Non-ASCII character detected at line {i}.")
            return False
    return True


def process_code():
    input_code = code_input.get("1.0", tk.END).strip()
    if not input_code:
        messagebox.showwarning("Empty Input", "Please enter Python code.")
        return

    # Clean input
    input_code = ''.join(c for c in input_code if ord(c) < 128)
    input_code = input_code.replace('\r\n', '\n').replace('\r', '\n')
    input_code = '\n'.join(line.rstrip() for line in input_code.splitlines())
    if not input_code.endswith('\n'):
        input_code += '\n'

    # Save raw input before tab replacement
    with open("raw_input.txt", "w", encoding="utf-8") as f:
        f.write(input_code)
    print("Raw input saved to raw_input.txt")

    # Replace tabs
    input_code = input_code.replace('\t', '    ')

    # Validate input
    if not validate_input(input_code):
        return

    # Save cleaned input
    with open("input.txt", "w", encoding="utf-8") as f:
        f.write(input_code)
    print("Cleaned input saved to input.txt")

    try:
        result = subprocess.run(["lexer.exe"], input=input_code, text=True, capture_output=True)
        if result.returncode != 0:
            messagebox.showerror("Error", f"Lexer failed: {result.stderr}")
            return
        lexer_output = result.stdout
        with open("lexer_output.txt", "w") as f:
            f.write(lexer_output)
        print("Lexer output saved to lexer_output.txt")
        with open("raw_lexer_output.txt", "w") as f:
            f.write(f"Raw lexer stdout:\n{lexer_output}\n")
            if result.stderr:
                f.write(f"Raw lexer stderr:\n{result.stderr}\n")
        print("Raw lexer output saved to raw_lexer_output.txt")
        tokens = tokenize_output(lexer_output)
        with open("tokens.txt", "w") as f:
            f.write("\n".join(tokens))
        print("Tokens saved to tokens.txt")
        parsed_statements = parse_tokens(tokens)
        c_code = generate_c_code(parsed_statements)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, c_code)
    except FileNotFoundError:
        messagebox.showerror("Error", "lexer.exe not found.")
    except SyntaxError as e:
        messagebox.showerror("Syntax Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")


def save_c_code():
    c_code = output_box.get("1.0", tk.END).strip()
    if c_code:
        try:
            os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'output'), exist_ok=True)
            output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'result.c'))
            with open(output_path, "w") as f:
                f.write(c_code)
            messagebox.showinfo("Success", f"C code saved to {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save C code: {e}")
    else:
        messagebox.showwarning("Empty Output", "No C code to save.")


compile_lexer()

root = tk.Tk()
root.title("Python to C Converter")

tk.Label(root, text="Enter Python Code:").pack()
code_input = scrolledtext.ScrolledText(root, height=10, width=80)
code_input.pack(pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="Convert to C", command=process_code).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Save C Code", command=save_c_code).pack(side=tk.LEFT, padx=5)

tk.Label(root, text="C Output Code:").pack()
output_box = scrolledtext.ScrolledText(root, height=10, width=80)
output_box.pack(pady=5)

root.mainloop()