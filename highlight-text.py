import tkinter as tk
from tkinter import ttk

def highlight_selection():
    try:
        # Get the currently selected text
        selection_start = text_box.index(tk.SEL_FIRST)
        selection_end = text_box.index(tk.SEL_LAST)
        
        # Add a tag to the selected text with yellow background
        text_box.tag_add("highlight", selection_start, selection_end)
        text_box.tag_configure("highlight", background="yellow")
    except tk.TclError:
        # No text selected
        pass

def clear_highlights():
    # Remove all highlight tags
    text_box.tag_remove("highlight", "1.0", tk.END)

# Create the main window
root = tk.Tk()
root.title("Text Highlighter")
root.geometry("800x600")

# Create a text box with scrollbar
frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

text_box = tk.Text(frame, wrap=tk.WORD, font=("Arial", 12))
scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_box.yview)
text_box.configure(yscrollcommand=scrollbar.set)

text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create buttons for highlighting and clearing
button_frame = ttk.Frame(root)
button_frame.pack(fill=tk.X, padx=10, pady=5)

highlight_button = ttk.Button(button_frame, text="Highlight Selection", command=highlight_selection)
highlight_button.pack(side=tk.LEFT, padx=5)

clear_button = ttk.Button(button_frame, text="Clear Highlights", command=clear_highlights)
clear_button.pack(side=tk.LEFT, padx=5)

# Add some sample text
sample_text = """This is a sample text that you can use to test the highlighting feature.
Select some text with your mouse or keyboard and then click the 'Highlight Selection' button.

You can add your own study material here by copying and pasting from various sources.
The highlights will help you keep track of important sections or where you left off."""

text_box.insert("1.0", sample_text)

# Run the application
root.mainloop()