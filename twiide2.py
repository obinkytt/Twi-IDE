import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox, filedialog
import sys
import io
import re

root = tk.Tk()
root.title("Twi Programming IDE By Dr. Williams Obinkyereh")
root.geometry("900x800")

# Expanded Twi to Python keyword mapping with additional keywords
keyword_map = {
    "kyerɛ": "print",
    "fa": "custom_input",
    "yɛ": "def",
    "sɛ": "if",
    "naaso": "else",
    "bere a": "while",
    "ma": "return",
    "nokware": "True",
    "tɔkwa": "False",
    "gye": "import",           # Example additional keywords
    "san": "continue",
    "breaki": "break",
    "bo": "for",
    "fi": "from"
}

# List of keywords for autocomplete & syntax highlighting
twi_keywords = list(keyword_map.keys())

# === Dark mode colors ===
light_bg = "white"
light_fg = "black"
dark_bg = "#2e2e2e"
dark_fg = "#f2f2f2"
current_theme = "light"

def custom_input(prompt=""):
    return simpledialog.askstring("Twi Input", prompt, parent=root)

def twi_to_python(twi_code):
    for twi_kw, py_kw in keyword_map.items():
        pattern = r'\b' + re.escape(twi_kw) + r'\b'
        twi_code = re.sub(pattern, py_kw, twi_code)
    return twi_code

# === Run Code ===
def run_code():
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    twi_code = text_input.get("1.0", tk.END)
    try:
        python_code = twi_to_python(twi_code)
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        exec(python_code, {"custom_input": custom_input})
        sys.stdout = old_stdout
        result = redirected_output.getvalue()
        output_box.insert(tk.END, result)
    except Exception as e:
        output_box.insert(tk.END, f"Error: {str(e)}")
        sys.stdout = old_stdout
    output_box.config(state="disabled")

def clear_code():
    text_input.delete("1.0", tk.END)
    update_line_numbers()

def clear_output():
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.config(state="disabled")

def save_code():
    file_path = filedialog.asksaveasfilename(defaultextension=".twi", filetypes=[("Twi Files", "*.twi")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_input.get("1.0", tk.END))

def load_code():
    file_path = filedialog.askopenfilename(filetypes=[("Twi Files", "*.twi")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            text_input.delete("1.0", tk.END)
            text_input.insert(tk.END, content)
        update_line_numbers()

def translate_code():
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    code = text_input.get("1.0", tk.END)
    translated = twi_to_python(code)
    output_box.insert("1.0", translated)
    output_box.config(state="disabled")

def export_python():
    twi_code = text_input.get("1.0", tk.END)
    translated_code = twi_to_python(twi_code)
    file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(translated_code)
        messagebox.showinfo("Export Successful", "Python code exported successfully!")

# === Line Numbers ===
def update_line_numbers(event=None):
    lines = text_input.get("1.0", "end-1c").split("\n")
    line_numbers.config(state="normal")
    line_numbers.delete("1.0", tk.END)
    line_numbers.insert(tk.END, "\n".join(str(i+1) for i in range(len(lines))))
    line_numbers.config(state="disabled")

def on_text_scroll(*args):
    line_numbers.yview(*args)
    text_input.yview(*args)

# === Syntax Highlighting (basic, on key release) ===
def highlight_keywords(event=None):
    # Remove previous tags
    text_input.tag_remove("keyword", "1.0", tk.END)

    content = text_input.get("1.0", tk.END)
    for kw in twi_keywords:
        start = "1.0"
        while True:
            pos = text_input.search(r'\b' + kw + r'\b', start, stopindex=tk.END, regexp=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(kw)}c"
            text_input.tag_add("keyword", pos, end_pos)
            start = end_pos

# === Autocomplete ===
autocomplete_window = None

def show_autocomplete(event):
    global autocomplete_window
    if event.keysym == "BackSpace":
        close_autocomplete()
        return

    # Get current word
    index = text_input.index(tk.INSERT)
    line, col = map(int, index.split('.'))
    line_text = text_input.get(f"{line}.0", f"{line}.end")
    prefix = ""
    i = col - 1
    while i >= 0 and (line_text[i].isalnum() or line_text[i] in ['ɛ', 'ɔ', 'ŋ', 'Ɛ', 'Ɔ']):
        prefix = line_text[i] + prefix
        i -= 1

    if prefix == "":
        close_autocomplete()
        return

    matches = [kw for kw in twi_keywords if kw.startswith(prefix)]
    if not matches:
        close_autocomplete()
        return

    if autocomplete_window:
        autocomplete_window.destroy()

    autocomplete_window = tk.Toplevel(root)
    autocomplete_window.wm_overrideredirect(True)

    x, y, _, _ = text_input.bbox(tk.INSERT)
    x += text_input.winfo_rootx()
    y += text_input.winfo_rooty() + 20

    autocomplete_window.wm_geometry(f"+{x}+{y}")

    listbox = tk.Listbox(autocomplete_window, height=min(len(matches), 5))
    listbox.pack()
    for m in matches:
        listbox.insert(tk.END, m)

    def select_autocomplete(event):
        selected = listbox.get(tk.ACTIVE)
        # Replace current prefix with selected
        text_input.delete(f"{line}.{col - len(prefix)}", f"{line}.{col}")
        text_input.insert(f"{line}.{col - len(prefix)}", selected)
        close_autocomplete()

    listbox.bind("<<ListboxSelect>>", select_autocomplete)
    listbox.bind("<Return>", select_autocomplete)
    listbox.focus_set()

def close_autocomplete():
    global autocomplete_window
    if autocomplete_window:
        autocomplete_window.destroy()
        autocomplete_window = None

def on_key_release(event):
    highlight_keywords()
    update_line_numbers()
    show_autocomplete(event)

# === Dark Mode Toggle ===
def toggle_dark_mode():
    global current_theme
    if current_theme == "light":
        current_theme = "dark"
        set_theme(dark_bg, dark_fg)
    else:
        current_theme = "light"
        set_theme(light_bg, light_fg)

def set_theme(bg_color, fg_color):
    root.config(bg=bg_color)
    text_input.config(bg=bg_color, fg=fg_color, insertbackground=fg_color)
    output_box.config(bg=bg_color, fg=fg_color)
    line_numbers.config(bg=bg_color, fg=fg_color)
    button_frame.config(bg=bg_color)
    for btn in button_frame.winfo_children():
        btn.config(bg=bg_color, fg=fg_color)
    for lbl in root.pack_slaves():
        if isinstance(lbl, tk.Label):
            lbl.config(bg=bg_color, fg=fg_color)

# === EXAMPLES ===
def insert_example(title):
    examples = {
        "Function": """yɛ frɛpa():
    kyerɛ("Afehyia pa!")

frɛpa()""",

        "Loop": """yɛ ka_10():
    n = 1
    bere a n <= 10:
        kyerɛ(n)
        n = n + 1

ka_10()""",

        "Condition": """din = fa("Wo din de sɛn? ")
sɛ din == "Kwame":
    kyerɛ("Agoo Kwame!")
naaso:
    kyerɛ("Yɛfrɛ wo " + din)""",
    
        "What is your name?": """ 
yɛ frɛpa():
    din = fa("Wo din de sɛn? ")
    kyerɛ("Yɛfrɛ wo " + din)
frɛpa()""",}

    clear_code()
    text_input.insert(tk.END, examples.get(title, ""))

# === TUTORIAL ===
def show_tutorial():
    guide = (
        "Twi Programming IDE - Guide\n\n"
        "KEYWORDS:\n"
        " - yɛ       → def (define a function)\n"
        " - fa       → input()\n"
        " - kyerɛ    → print()\n"
        " - sɛ       → if\n"
        " - naaso    → else\n"
        " - bere a   → while\n"
        " - ma       → return\n"
        " - nokware  → True\n"
        " - tɔkwa    → False\n\n"
        "SAMPLE CODE:\n"
        "yɛ frɛpa():\n"
        "    din = fa(\"Wo din de sɛn? \")\n"
        "    kyerɛ(\"Yɛfrɛ wo \" + din)\n\n"
        "frɛpa()\n\n"
        "Use the cursor to select twi \n" 
        "alphabets which are not on your keyboard \n"
    )
    messagebox.showinfo("Twi Programming Tutorial", guide)
    
# === TWI CHARACTER TOOLBAR ===
char_frame = tk.Frame(root)
char_frame.pack(fill=tk.X, padx=5, pady=3)

def insert_char(char):
    text_input.insert(tk.INSERT, char)

chars = ['ɛ', 'ɔ', 'ŋ', 'Ɛ', 'Ɔ']
for c in chars:
    btn = tk.Button(char_frame, text=f"[ {c} ]", command=lambda ch=c: insert_char(ch), width=4)
    btn.pack(side=tk.LEFT, padx=2)    

# === GUI ===
menu_bar = tk.Menu(root)
example_menu = tk.Menu(menu_bar, tearoff=0)
example_menu.add_command(label="Functions in Twi", command=lambda: insert_example("Function"))
example_menu.add_command(label="Loops in Twi", command=lambda: insert_example("Loop"))
example_menu.add_command(label="Conditionals in Twi", command=lambda: insert_example("Condition"))
example_menu.add_command(label="What is your name in Twi", command=lambda: insert_example("What is your name?"))

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Twi Programming Guide", command=show_tutorial)

menu_bar.add_cascade(label="Examples", menu=example_menu)
menu_bar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu_bar)

tk.Label(root, text="Write your Twi code below:\n Use the cursor to select twi alphabets which are not on your keyboard", font=("Arial", 12)).pack(pady=5)

# Container frame for line numbers and text input
text_frame = tk.Frame(root)
text_frame.pack(pady=5, fill="both", expand=True)

line_numbers = tk.Text(text_frame, width=4, padx=3, takefocus=0, border=0,
background=light_bg, foreground=light_fg, state="disabled", font=("Courier", 11))
line_numbers.pack(side="left", fill="y")

text_input = tk.Text(text_frame, width=90, height=15, font=("Courier", 11), undo=True, wrap="none")
text_input.pack(side="left", fill="both", expand=True)

# Scrollbar for both text areas
scrollbar = tk.Scrollbar(text_frame, command=lambda *args: [text_input.yview(*args), line_numbers.yview(*args)])
scrollbar.pack(side="right", fill="y")

text_input.config(yscrollcommand=scrollbar.set)

# Bind events for line numbers and autocomplete
text_input.bind("<KeyRelease>", on_key_release)
text_input.bind("<MouseWheel>", update_line_numbers)
text_input.bind("<Button-1>", update_line_numbers)
text_input.bind("<FocusIn>", update_line_numbers)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="▶ Run", command=run_code, bg="green", fg="white", font=("Arial", 11)).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="🧹 Clear Code", command=clear_code, font=("Arial", 11)).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="🔄 Clear Output", command=clear_output, font=("Arial", 11)).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="💾 Save", command=save_code, font=("Arial", 11)).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="📂 Load", command=load_code, font=("Arial", 11)).grid(row=0, column=4, padx=5)
tk.Button(button_frame, text="🔤 Translate", command=translate_code, font=("Arial", 11)).grid(row=0, column=5, padx=5)
tk.Button(button_frame, text="📤 Export Python", command=export_python, font=("Arial", 11), bg="orange").grid(row=0, column=6, padx=5)
tk.Button(button_frame, text="🌙 Dark Mode", command=toggle_dark_mode, font=("Arial", 11)).grid(row=0, column=7, padx=5)

tk.Label(root, text="Output:", font=("Arial", 12)).pack(pady=5)
output_box = scrolledtext.ScrolledText(root, width=100, height=10, font=("Courier", 11), state="disabled", bg="white")
output_box.pack(pady=5)

# Syntax highlighting tag config
text_input.tag_configure("keyword", foreground="blue")

# Initialize line numbers
update_line_numbers()

root.mainloop()

