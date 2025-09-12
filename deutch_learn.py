from openai import OpenAI
import tkinter as tk
from tkinter import ttk # Add this line
from tkinter import filedialog, scrolledtext, messagebox
import random
import requests
from bs4 import BeautifulSoup
import tkinter.font as tkFont
import os, sys
import subprocess

# --- Configuration ---
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default notes file:
notes_filename = r'C:\Users\George\Desktop\German_Study_Files\notes-default.txt'

# Access the key using os.getenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

if not api_key:
    messagebox.showerror("API Key Error", "Error: OPENAI_API_KEY not found. Make sure it's set in your .env file.")
    exit()


# --------------------
# Configure the OpenAI client
# --------------------
def configure_openai():
    """
    Set up the OpenAI API key and verify connectivity.
    """
    try:
        
        print("OpenAI API configured successfully.")
    except Exception as e:
        messagebox.showerror("API Configuration Error", f"Failed to configure OpenAI API: {e}")
        exit()


class VocabularyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("German Language Tutor")
        self.root.configure(bg="#222")

        # Maximize the window (keeps Windows taskbar visible)
        self.root.state('zoomed')  # <- Works well on Windows

        # --- ADD THESE TWO LINES ---
        self.root.update_idletasks() # Ensures the window is rendered before querying its geometry
        print(f"Root window geometry after zoom: {self.root.winfo_geometry()}")
        # ---------------------------

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history = [
            {"role":"system", "content":"You are a helpful assistant for German–English practice."}
        ]

        # Variables to store vocabulary and current word
        self.vocabulary = []  # List to store vocabulary lines
        self.current_word = None  # Current word/phrase being displayed
        self.current_language = "german"  # Tracks the current language (german/english)
        self.current_voc_file = None  # Store the loaded filename here
        self.current_study_file = None
        self.current_translated_file = None
        self.current_example_sentences_file = None
        self.current_ai_responses_file = None
        self.score = 0  # Initialize score
        self.count_test_num = 0 # debug. Initialize test number question
        self.total_questions = 0  # Total number of questions asked
        self.correct_answers = 0  # Number of correct answers
        self.flip_mode = False  # Tracks whether flip mode is active
        self.left_section_font = tkFont.Font(family="Helvetica", size=10, weight="normal")
        self.conversation_history = []
        self.divert = 0
        self.load_current_voc = 0

        # Create a smaller font for the highlight buttons
        self.small_button_font = tkFont.Font(family="Helvetica", size=8, weight="normal")
        
        # MANUAL CONFIGURATION OF COLOR BUTTONS
        # ... inside __init__ method ...
        self.style = ttk.Style()
        # Define a custom style for a purple button
        self.style.theme_use('default') # Ensure a base theme is used
        self.style.configure('Purple.TButton',
                            background="#ca74ea", # Your desired background color
                            foreground='black',   # Your desired text color
                            font=self.left_section_font) # Use your defined font object
        # Define a custom style for a red button
        self.style.configure('Red.TButton',
                            background='#AA0000', # Your desired background color
                            foreground='white',   # Your desired text color
                            font=self.left_section_font) # Use your defined font object
        # Define a custom style for a green button
        self.style.configure('Green.TButton',
                            background='#008844', # Your desired background color
                            foreground='black',   # Your desired text color
                            font=self.left_section_font) # Use your defined font object
        # ... you'll need to define similar styles for all your button colors

        # Inside your __init__(self, root) method:

        self.style = ttk.Style()
        self.style.theme_use('default') # Ensure a base theme is used

        # Define styles for all your button colors
        self.style.configure('DarkPurple.TButton',
                            background='#ca74ea',
                            foreground='black',
                            font=self.left_section_font)

        self.style.configure('Blue.TButton',
                            background="#73A2D0",
                            foreground='black',
                            font=self.left_section_font)

        self.style.configure('Green.TButton',
                            background='#008844',
                            foreground='black',
                            font=self.left_section_font)

        self.style.configure('Red.TButton',
                            background='#AA0000',
                            foreground='black',
                            font=self.left_section_font)

        self.style.configure('GoldBrown.TButton', # For SORT, NOTES, Flip Sentences
                            background='#AA8800',
                            foreground='black', # Check your specific fg for these
                            font=self.left_section_font)

        self.style.configure('LightPurple.TButton', # For Free-Hand Translation
                            background='#cbb0e0',
                            foreground='black', # Check your specific fg for this
                            font=self.left_section_font)

        self.style.configure('Orange.TButton', # For Clear Input, Clear Test
                            background='orange',
                            foreground='black', # Check your specific fg for these
                            font=self.left_section_font)

        self.style.configure('DarkBlue.TButton', # For Next Word
                            background='#005588',
                            foreground='black',
                            font=self.left_section_font)

        self.style.configure('GrayBlue.TButton', # For Langenscheidt
                            background="#9DC1E4",
                            foreground='black',
                            font=self.left_section_font)

        self.style.configure('DarkOlive.TButton', # For Search OWN vocab.
                            background="#95C068",
                            foreground='black',
                            font=self.left_section_font)

        self.style.configure('OliveGreen.TButton', # For Glosbe Examples
                            background='#95946A',
                            foreground='black',
                            font=self.left_section_font)
        
        self.style.configure('Greenish.TButton', # For Glosbe Examples
                            background="#AABD7E",
                            foreground='black',
                            font=self.left_section_font)
        
        # In your __init__ method, add these style definitions
        self.style.configure('SmallWhite.TButton',
                    background='#7B7D7D',
                    foreground='white',
                    font=self.small_button_font)

        self.style.configure('SmallBlueish.TButton',
                    background='#5D6D7E',
                    foreground='white',
                    font=self.small_button_font)

        # Add this to your style configurations in __init__
        self.style.configure('SmallPurple.TButton',
                    background='#ca74ea',
                    foreground='black',
                    font=self.small_button_font)  # Use the same small font as other buttons


        # Left Section - Vocabulary, Study Text, and Translation Boxes
        self.create_left_section()

        # Middle - Section for LOAD, SAVE, etc.
        self.create_middle_section()

        # Right Section - Example Sentences, Test Section, Dictionary Search
        self.create_right_section()

        # Add highlight functionality to textboxes
        self.add_highlight_functionality()

        # Create a smaller font for the highlight buttons
        self.small_button_font = tkFont.Font(family="Helvetica", size=8, weight="normal")

        # Update label colors to gold - ADD THIS LINE
        # self.update_label_colors_to_gold()
    
    # --- REFOCUS THE CURSON INSIDE THE TEST INPUT ---
    def trigger_next_word_and_refocus(self, event=None):
        """
        Triggers the next word action and ensures focus remains in the answer_entry.
        """
        self.next_word()
        self.answer_entry.focus_set()
        self.answer_entry.delete(0, tk.END) # Optional: Clear the entry
        return "break"

    def ask_chatgpt(self, prompt: str, model_name="gpt-4o", temperature=0.7) -> str:
        resp = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": prompt}
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    
    # Labels in gold
   

    def prompt_inputbox(self):
        """
        Send user input from the GUI chat input to ChatGPT, maintain conversation history, and display responses.
        If we're in comprehension test mode, evaluate the answers instead of general chat.
        """
        # Retrieve user input
        content = self.input_textbox.get(1.0, tk.END).strip()
        if not content:
            return
        
        # Check if we're in comprehension test mode (questions are in the translation box)
        translation_text = self.translation_textbox.get(1.0, tk.END).strip()
        
        if hasattr(self, 'current_comprehension_questions') and self.current_comprehension_questions:
            # We're in comprehension test mode - evaluate the answers
            evaluation_prompt = f"""
            I'm a German language learner. I was asked these comprehension questions:
            {self.current_comprehension_questions}
            
            And I provided these answers:
            {content}
            
            Please evaluate my answers:
            1. Point out any mistakes I made
            2. Suggest corrections
            3. Provide alternative correct answers where applicable
            4. Give me a score out of 10 based on accuracy and completeness
            
            Respond in English to help me understand my mistakes.
            """
            
            # Append to conversation history
            self.conversation_history.append({"role": "user", "content": evaluation_prompt})
        else:
            # Regular chat mode
            self.conversation_history.append({"role": "user", "content": content})

        try:
            # Send full history to ChatCompletion
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                temperature=0.7,
            )
            answer = response.choices[0].message.content.strip()

            # Append assistant response to history
            self.conversation_history.append({"role": "assistant", "content": answer})

            # Display in GUI
            self.ai_responses_textbox.insert(tk.END, f"You: {content} \n\n AI: {answer}\n\n")

            # Clear user input box if we're in comprehension test mode
            if hasattr(self, 'current_comprehension_questions') and self.current_comprehension_questions:
                # Clear the comprehension questions after evaluation
                delattr(self, 'current_comprehension_questions')
                self.input_textbox.delete(1.0, tk.END)
        except Exception as e:
            # Display error asynchronously
            self.root.after(0, messagebox.showerror, "Chat Error", f"An error occurred: {e}")

    def clear_input_textbox(self):
        self.input_textbox.delete(1.0, tk.END)

    # --------------------
    # AI creates vocabulary from txt file
    # --------------------
    def create_vocabulary(self): # debug
        """
        Load a German-language .txt file, send its content to OpenAI to generate
        a cleaned vocabulary list (German = English), and display in the GUI.
        """
        filename = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()

            configure_openai()

            prompt = (
            """I have uploaded a text file in the German language and I want you to process it as follows:
            1) Make a list of all of the words in the text file.
            2) Remove these words: der, die, das, Montag, Dienstag, Mittwoch, Donnerstag, Freitag, Samstag, Sonntag, \
            Januar, Februar, März, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember, ich, du, \
                er, sie, es, wir, ihr, sie, Sie, in, an, auf, unter, über, vor, hinter, neben, zwischen, mit, nach, \
                bei, seit, von, zu, für, durch, um, und, aber, gegen, ohne, am, zur, Man, Frau, Kind, mich, dich, sich \
                uns, euch, ihnen, nicht, ja, nun, ob, ist, sein, war, waren, haben, hat, gehabt, wurde, wurden, wird.
            3) Also remove these: Frühling, Sommer, Herbst, Winter
            4) Output the response without using Markup or numbers before each word.
            5) Translate the german words into the english language as instructed below but limit your responses \
                to NOT more than THREE english translations. \
                If the german word is a NOUN, start by displaying that word in SINGULAR form followed by \
                a comma and then by the article, comma again and then the PLURAL form in brackets. \
                For example, if you encounter 'Buches', display ONLY the following: Buch, das, [Bücher, die] = book, volume, ledger.
                If the german word is a verb in any form or case, display first the base form. \
                For example: if you encounter in the text the word'steht', DO NOT start by displaying 'steht' again, rather start by displaying \
                the base form 'stehen' followed by a comma and in brackets the other two forms (past and past participle), for example \
                'stehen, [stand, gestanden] = to stand, to rise.\
                Similarly, if you encounter in the text verbs in the past participle, for example 'abgeschoben',\
                then DO NOT display the past participle but the infinitive, for example, 'abschieben', followed by the past tense \
                and the past participle in brackets, ['schob ab', 'abgeschoben'], followed by the equal sign (=) and the interpretation in english.
                If you encounter a regular verb, for example 'legt', you DO NOT display 'legt' again, rather display: legen, [legte, gelegt] = to place \
                Similarly, if you encounter in the text an irregular verb, e.g. 'springst' you DO NOT display 'springst'again, rather you display \
                spriengen, [sprang, gesprungen] = to jump, to leap.
                For ALL VERBS make sure to INCLUDE the word 'to' before the english meaning, for example: \
                gehen, [ging, geganden] = to go, to walk.
                        """
            )

            # Call the ChatCompletion API
            response = client.chat.completions.create(model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for language study."},
                {"role": "user", "content": f"{prompt}\n\n{content}"}
            ],
            temperature=0.3)
            auto_vocabulary = response.choices[0].message.content

            # Display in GUI
            self.vocabulary_textbox.delete(1.0, tk.END)
            self.vocabulary_textbox.insert(tk.END, auto_vocabulary)

        except FileNotFoundError:
            self.vocabulary_textbox.delete(1.0, tk.END)
            self.vocabulary_textbox.insert(tk.END, "Error: File not found.")
        except Exception as e:
            self.vocabulary_textbox.delete(1.0, tk.END)
            self.vocabulary_textbox.insert(tk.END, f"An error occurred: {e}")


    # --------------------
    # AI: Translate study file conditionally
    # --------------------
    def translate_study_text(self):
        filename = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not filename:
            return
        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            # Build the conditional translation prompt
            prompt = (
                "If the contents of the file are in German, then translate into English. "
                "However, if the contents of the file are in English then translate into German"
                "If the contents of the file are NEITHER in German or in English, then translate into English"
            )
            # Combine prompt and content
            full_prompt = f"{prompt}\n\n{content}"

            # Send to ChatGPT
            translated_text = self.ask_chatgpt(full_prompt, model_name="gpt-4o", temperature=0.3)

            # Display the result
            self.translation_textbox.delete(1.0, tk.END)
            self.translation_textbox.insert(tk.END, translated_text)
        except FileNotFoundError:
            self.translation_textbox.delete(1.0, tk.END)
            self.translation_textbox.insert(tk.END, "Error: File not found.")
        except Exception as e:
            self.translation_textbox.delete(1.0, tk.END)
            self.translation_textbox.insert(tk.END, f"An error occurred: {e}")

    def save_ai_responses(self):
        if not self.current_ai_responses_file:
            # First save - ask for filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")])
            if not filename:  # User cancelled
                return

            self.current_ai_responses_file = filename
            with open(filename, 'w', encoding='utf-8-sig') as file:
                content = self.ai_responses_textbox.get(1.0, tk.END)
                file.write(content)
            messagebox.showinfo("Success", f"New file created at:\n{filename}")
        else:
            # Subsequent saves - ask whether to overwrite or create new
            choice = messagebox.askyesnocancel(
                "Save Options",
                f"Overwrite existing file?\n{self.current_ai_responses_file}\n\n"
                "Yes = Overwrite\nNo = Save as new file\nCancel = Abort")

            if choice is None:  # User cancelled
                return
            elif choice:  # Overwrite
                with open(self.current_ai_responses_file, 'w', encoding='utf-8-sig') as file:
                    content = self.ai_responses_textbox.get(1.0, tk.END)
                    file.write(content)
                messagebox.showinfo("Success", f"File overwritten at:\n{self.current_ai_responses_file}")
            else:  # Save as new file
                filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt")])
                if filename:
                    self.current_ai_responses_file = filename
                    with open(filename, 'w', encoding='utf-8-sig') as file:
                        content = self.ai_responses_textbox.get(1.0, tk.END)
                        file.write(content)
                        messagebox.showinfo("Success", f"New file created at:\n{filename}")

    def append_ai_responses_to_file(self):
        # Ask user to select file (can navigate directories and create new folders)
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            title="Select file to append to"
        )

        if filename:
            try:
                with open(filename, 'a+', encoding='utf-8-sig') as file:
                    content = self.ai_responses_textbox.get(1.0, tk.END)
                    file.write("\n\n")  # Add separation from previous content
                    file.write(content)
                messagebox.showinfo("Success", f"Content appended to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to append to file:\n{str(e)}")


    def copy_ai_responses(self):
        """Copies the contents of the AI responses textbox to the clipboard"""
        try:
            # Get the text from the textbox
            content = self.ai_responses_textbox.get(1.0, tk.END).strip()

            # Clear the clipboard and append the content
            self.root.clipboard_clear()
            self.root.clipboard_append(content)

            # Optional: Show a brief success message
            messagebox.showinfo("Copied", "AI responses copied to clipboard!", parent=self.root)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy text: {str(e)}", parent=self.root)

    def clear_ai_responses_textbox(self):
        self.ai_responses_textbox.delete(1.0, tk.END)


    def en_to_de_translation(self):
        # Get the contents of a vocabulary file (_VOC) to construct sentences
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        
        # explain how to engage in this translation practice
        messagebox.showinfo("Success", f"Study the senteces displayed in the 'Study Text Box. \
                            Use any other text box to write your translation per \
                            sentece. \
                            DO NOT translate into the 'Translation Box' which can display \
                            the correct translations by clicking 'Free-Hand Translation'")

        if not filename:  # User cancelled the dialog
            return
        
        try:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                word_pairs = [line.strip() for line in content.splitlines() if line.strip()]
                
        # Add a bit of random context to encourage varied responses
                variation_hints = [
                    "Try to be creative and use different contexts.",
                    "Give fresh and varied examples, avoid common textbook ones.",
                    "Use different sentence structures or scenarios than before.",
                    "Pick examples from different domains like travel, food, or work.",
                    "Avoid repeating any previous examples."
                ]
                variation_hint = random.choice(variation_hints)

                # Build the specific prompt
                prompt = (
                    "Using ONLY these English words from the dictionary:\n" +
                    "\n".join(word_pairs) +
                    "\n\nCreate exactly 10 complete English sentences. "
                    "Use at least 2 dictionary words per sentence. "
                    "ONLY output the 10 sentences, with one sentence per line. "
                    "Number the sentences but no translations, no explanations, no additional text. "
                    "Example format:\n"
                    "1) The cat sat on the mat\n"
                    "2) She enjoys reading books\n"
                    "... [8 more sentences]"
                    f"{variation_hint}"
                )
                
                sentences = self.ask_chatgpt(prompt, model_name="gpt-4o", temperature=0.8)
                
                self.study_textbox.delete(1.0, tk.END)
                self.study_textbox.insert(tk.END, sentences)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {str(e)}", parent=self.root)


    # --------------------
    # AI: Fetch example sentences for a word
    # --------------------
    def fetch_ai_examples(self):
        """
        Get up to two varied example sentences for a German word, with English translations.
        """
        import random

        entry = self.glosbe_search_entry.get().strip()
        if not entry:
            return

        # Add a bit of random context to encourage varied responses
        variation_hints = [
            "Try to be creative and use different contexts.",
            "Give fresh and varied examples, avoid common textbook ones.",
            "Use different sentence structures or scenarios than before.",
            "Pick examples from different domains like travel, food, or work.",
            "Avoid repeating any previous examples."
        ]
        variation_hint = random.choice(variation_hints)

        prompt = (
            "Please provide no more than two example sentences showing how the German word is used. "
            "Format each as: German sentence = English sentence, separated by a blank line."
            "DO NOT number the sentences."
            "Stick to the format. Always the equal sign should follow the German sentence and the English sentences follows the equal sign."
            f"{variation_hint}"
        )

        full_prompt = f"{prompt}\n\n{entry}"

        try:
            examples = self.ask_chatgpt(full_prompt, model_name="gpt-4o", temperature=0.8)
            self.example_sentences_textbox.insert(tk.END, "\n" + examples)

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Examples Error", f"An error occurred: {e}")



    def create_left_section(self):
        font = self.left_section_font
        left_frame = tk.Frame(self.root, bg="#222")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create textboxes - only add highlight buttons to Study Text Box and Translation Box
        self.vocabulary_textbox = self.create_labeled_textbox(left_frame, "Vocabulary (Current):", True, height=10, label_font=font, add_buttons=False)
        self.study_textbox = self.create_labeled_textbox(left_frame, "Study Text Box:", True, height=10, label_font=font, add_buttons=True)
        self.translation_textbox = self.create_labeled_textbox(left_frame, "Translation Box:", True, height=10, label_font=font, add_buttons=True)
        self.input_textbox = self.create_labeled_textbox(left_frame, "Prompt the AI by writing below", True, height=5, label_font=font, add_buttons=False)


        # Add the AI prompt buttons
        ttk.Button(
            left_frame,
            text="Prompt AI",
            style='Purple.TButton',
            command=self.prompt_inputbox
        ).pack(side='left', padx=(10, 3), pady=3)

        ttk.Button(
            left_frame,
            text="Clear Prompt",
            style='Red.TButton',
            command=self.clear_input_textbox
        ).pack(side='left', padx=3, pady=3)

        ttk.Button(
            left_frame,
            text="Create sentences from random words in a _VOC file",
            style='Purple.TButton',
            command=self.en_to_de_translation
        ).pack(side='left', padx=3, pady=3)

    def create_middle_section(self):
        middle_frame = tk.Frame(self.root, bg="#222")
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=18)
        
    # --- Group 1: Vocabulary Buttons ---
    # Create a frame for the Vocabulary buttons
        vocab_btn_frame = tk.Frame(middle_frame, bg="#222")
        vocab_btn_frame.pack(pady=(0, 25)) # <--- TOP & BOTTOM PADDING for this GROUP (e.g., 25 pixels at bottom)

    # Buttons for Vocabulary Box - pack into vocab_btn_frame
        ttk.Button(vocab_btn_frame, text="LOAD-VOC", style='Blue.TButton', command=self.load_vocabulary).pack(pady=2)
        ttk.Button(vocab_btn_frame, text="AI-create VOC\nfrom _TXT file", style='DarkPurple.TButton', command=self.create_vocabulary).pack(pady=2)
        ttk.Button(vocab_btn_frame, text="SAVE-VOC", style='Green.TButton', command=self.save_vocabulary).pack(pady=2)
        ttk.Button(vocab_btn_frame, text="Sort-Remove\nDuplicates", style='GoldBrown.TButton', command=self.sort_vocabulary).pack(pady=2)
        ttk.Button(vocab_btn_frame, text="CLR-VOC", style='Red.TButton', command=self.clear_vocabulary).pack(pady=2) # Adjusted from 17, as group padding will handle overall spacing


    # --- Group 2: Study Text Buttons ---
    # Create a frame for the Study Text buttons
        study_btn_frame = tk.Frame(middle_frame, bg="#222")
        study_btn_frame.pack(pady=(15, 15)) # <--- TOP & BOTTOM PADDING for this GROUP

    # Buttons for Study Text Box - pack into study_btn_frame
        ttk.Button(study_btn_frame, text="LOAD-TXT", style='Blue.TButton', command=self.load_study_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="SAVE-TXT", style='Green.TButton', command=self.save_study_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="CLR-TXT", style='Red.TButton', command=self.clear_study_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="Translate file", style='DarkPurple.TButton', command=self.translate_study_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="Free-Hand\nTranslation", style='LightPurple.TButton', command=self.capture_text).pack(pady=2)


    # --- Group 3: Translation Buttons ---
    # Create a frame for the Translation buttons
        translation_btn_frame = tk.Frame(middle_frame, bg="#222")
        translation_btn_frame.pack(pady=(25, 0)) # <--- TOP PADDING for this GROUP

    # Buttons for Translation Box - pack into translation_btn_frame
        ttk.Button(translation_btn_frame, text="LOAD-TRA", style='Blue.TButton', command=self.load_translation).pack(pady=2) # Adjusted from 20
        ttk.Button(translation_btn_frame, text="SAVE-TRA", style='Green.TButton', command=self.save_translation).pack(pady=2)
        ttk.Button(translation_btn_frame, text="CLR-TRA", style='Red.TButton', command=self.clear_translation).pack(pady=2) # Adjusted from 15
        ttk.Button(translation_btn_frame, text="NOTES", style='GoldBrown.TButton', command=self.add_notes).pack(pady=2) # Adjusted from 15
        
        # --- NEW Group 4: AI Response Buttons (Middle Section) ---
        # Create a separate frame for these 4 buttons
        ai_responses_middle_btn_frame = tk.Frame(middle_frame, bg="#222")
        # Pack this new frame with padding at the top to create separation
        ai_responses_middle_btn_frame.pack(pady=(40, 0)) # <--- Adjust this top padding for desired space

        # Buttons for AI Responses - pack into ai_responses_middle_btn_frame
        ttk.Button(ai_responses_middle_btn_frame, text="Save AI\nResponses", style='DarkPurple.TButton', command=self.save_ai_responses).pack(pady=2)
        ttk.Button(ai_responses_middle_btn_frame, text="Append AI\nResponses", style='DarkPurple.TButton', command=self.append_ai_responses_to_file).pack(pady=2)
        ttk.Button(ai_responses_middle_btn_frame, text="Copy AI \nResponses", style='DarkPurple.TButton', command=self.copy_ai_responses).pack(pady=2)
        ttk.Button(ai_responses_middle_btn_frame, text="Clear AI\nResponses", style='Red.TButton', command=self.clear_ai_responses_textbox).pack(pady=2)
    

    def create_right_section(self):
        right_frame = tk.Frame(self.root, bg="#222")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5) # Added padx=5
        # right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True) # Added expand=True back

        # Example Sentences
        self.example_sentences_textbox = self.create_labeled_textbox(right_frame, "Find example sentences using the AI or the Glosbe dictionary, also Load and Append examples", True, height=8)

        # New Input Box for Glosbe Search
        self.glosbe_search_entry = tk.Entry(right_frame, bg="black", fg="white", insertbackground="white", font=("Helvetica", 13))
        self.glosbe_search_entry.pack(fill=tk.X, padx=10, pady=5)

        # Buttons for Example Sentences
        btn_frame = tk.Frame(right_frame, bg="#222")
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="AI Examples", style='DarkPurple.TButton', command=self.fetch_ai_examples).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Glosbe Examples", style='OliveGreen.TButton', command=self.fetch_glosbe_examples).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Examples", style='Blue.TButton', command=self.load_examples).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Append", style='Green.TButton', command=self.save_examples).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Input", style='Orange.TButton', command=self.clear_examples_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", style='Red.TButton', command=self.clear_example_sentences).pack(side=tk.LEFT, padx=5)

        # Vocabulary Test Section
        test_frame = tk.Frame(right_frame, bg="#222")
        test_frame.pack(fill=tk.X, pady=10)
        tk.Label(test_frame, text="Take a test of the Vocabulary (Current) or choose other '_VOC.txt' file:", fg="gold", bg="#222").pack(anchor='w')

        btn_frame2 = tk.Frame(test_frame, bg="#222")
        btn_frame2.pack(fill=tk.X)
        ttk.Button(btn_frame2, text="Choose other '_VOC.txt' File", style='Blue.TButton', command=self.load_test_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Flip Words", style='GoldBrown.TButton', command=self.toggle_flip_mode).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Clear Test", style='Orange.TButton', command=self.clear_test).pack(side=tk.LEFT, padx=5)

        self.test_filename_label = tk.Label(test_frame, text="File is:", fg="white", bg="#222")
        self.test_filename_label.pack(anchor='w')

        self.test_textbox = scrolledtext.ScrolledText(test_frame, height=7, wrap=tk.WORD, bg="#333", fg="white", font=("Helvetica", 11))
        self.test_textbox.pack(fill=tk.X)

        # Answer Input
        tk.Label(right_frame, text="Type your answer below and then press the ENTER key. 'to' is added before the English verbs", fg="gold", bg="#222").pack(anchor='w')
        tk.Label(right_frame, text="For the 'Next Word' hold down SHIFT and press the ENTER key", fg="cyan", bg="#222").pack(anchor='w')
        self.answer_entry = tk.Entry(right_frame, bg="black", fg="white", insertbackground="white", font=("Helvetica", 11))
        self.answer_entry.pack(fill=tk.X)
        self.answer_entry.bind("<Return>", self.check_answer)
        self.answer_entry.bind("<Shift-Return>", self.trigger_next_word_and_refocus) # debuging / refocus entry input
        

        answer_frame = tk.Frame(right_frame, bg="#222")
        answer_frame.pack(fill=tk.X)
        ttk.Button(answer_frame, text="Next Word", style='Blue.TButton', command=self.next_word).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(answer_frame, text="Clear Input", style='Orange.TButton', command=self.clear_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(answer_frame, text="Revise Mistakes", style='Greenish.TButton', command=self.load_revision_file).pack(side=tk.LEFT, padx=5)
        tk.Label(answer_frame, text="Score:", fg="white", bg="#222").pack(side=tk.LEFT, padx=5)
        self.score_label = tk.Label(answer_frame, text="0%", fg="white", bg="#222")
        self.score_label.pack(side=tk.LEFT)
        tk.Label(answer_frame, text="Test Question Number", fg="white", bg="#222").pack(side=tk.LEFT, padx=5)
        self.count_test_num_label = tk.Label(answer_frame, text="0", fg="white", bg="#222") # debug
        self.count_test_num_label.pack(side=tk.LEFT) # debug

        # Dictionary Search
        tk.Label(right_frame, text="Search word using AI or Langenscheid online dictionary", fg="gold", bg="#222").pack(anchor='w', pady=5)
        self.dictionary_entry = tk.Entry(right_frame, bg="black", fg="white", insertbackground="white", font=("Helvetica", 11))
        self.dictionary_entry.pack(fill=tk.X)

        dict_btn_frame = tk.Frame(right_frame, bg="#222")
        dict_btn_frame.pack(fill=tk.X)
        ttk.Button(dict_btn_frame, text="AI word translation", style='DarkPurple.TButton', command=self.ai_translate_word).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(dict_btn_frame, text="Langenscheidt", style='GrayBlue.TButton', command=self.fetch_langenscheidt).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(dict_btn_frame, text="Search vocabulary (Current).", style='DarkOlive.TButton', command=self.search_own_vocab).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(dict_btn_frame, text="Clear Input", style='Orange.TButton', command=self.clear_entry).pack(side=tk.LEFT, padx=5)

        # AI Responses to prompts
        self.ai_responses_textbox = self.create_labeled_textbox(right_frame, "AI Responses from prompt on the left side", True, height=8, label_font="Helvetica")


    def create_labeled_inputbox(self, parent, label_text, width=80, height=20, wrap=tk.WORD, label_font=None):
        # Create container frame (matching labeled_textbox style)
        frame = tk.Frame(parent, bg="#222")
        frame.pack(fill=tk.X, expand=True, padx=10, pady=3)

        # Create the label widget (matching your style)
        label = tk.Label(frame, text=label_text, fg="gold", bg="#222")
        if label_font:
            label.config(font=label_font)
        label.pack(anchor='w')  # Left-aligned like your other labels

        # Create the ScrolledText widget with your preferred styling
        inputbox = scrolledtext.ScrolledText(
            frame,
            width=width,
            height=height,
            wrap=wrap,
            bg="#333",               # Matching your dark theme
            fg="white",              # Text color
            insertbackground="white", # Cursor color
            font=("Times New Roman", 10),  # Your preferred font
            padx=10,                 # Inner padding
            pady=10
        )
        inputbox.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 3))  # Adjusted padding

        return inputbox  # Return the widget for later access

    def create_labeled_textbox(self, parent, label_text, scrollbar=True, height=10, label_font=None, add_buttons=False):
        """Create a labeled textbox with optional scrollbar and optional highlight buttons"""
        frame = tk.Frame(parent, bg="#222")
        frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Changed fg from "white" to "gold" for the label
        label = tk.Label(frame, text=label_text, bg="#222", fg="gold", font=label_font)
        label.pack(anchor="w")
        
        if scrollbar:
            textbox = scrolledtext.ScrolledText(frame, height=height, bg="#333", fg="white", 
                                            insertbackground="white", font=label_font, wrap="word")
        else:
            textbox = tk.Text(frame, height=height, bg="#333", fg="white", 
                            insertbackground="white", font=label_font, wrap="word")
        
        textbox.pack(fill=tk.X, pady=(5, 0))
        
        # Configure highlight tag with yellow background and black text
        textbox.tag_configure("highlight", background="yellow", foreground="black")
        
        # Only add buttons if requested
        if add_buttons:
            # Create button frame for this textbox
            button_frame = tk.Frame(frame, bg="#222")
            button_frame.pack(fill=tk.X, pady=(0, 5))
            
            # Create highlight buttons
            ttk.Button(
                button_frame,
                text="Highlight",
                style='SmallWhite.TButton',
                command=lambda: self.highlight_text(textbox)
            ).pack(side='left', padx=(10, 3), pady=3)
            
            ttk.Button(
                button_frame,
                text="Clear Highlight",
                style='SmallBlueish.TButton',
                command=lambda: self.clear_text_highlight(textbox)
            ).pack(side='left', padx=3, pady=3)
            
            # Add the "Load Text and Answer Questions" button only for Study Text Box
            if label_text == "Study Text Box:":
                ttk.Button(
                    button_frame,
                    text="Reading Comprehension",
                    style='SmallPurple.TButton',
                    command=self.generate_comprehension_questions
                ).pack(side='left', padx=(20, 3), pady=3)  # Added 20px left padding to position it to the right
        
        return textbox
    
    def generate_comprehension_questions(self):
        """Generate comprehension questions based on the text in the Study Text Box"""
        # Get the text from the Study Text Box
        study_text = self.study_textbox.get(1.0, tk.END).strip()
        
        if not study_text:
            messagebox.showwarning("No Text", "Please load some text into the Study Text Box first.")
            return
        
        # Create the prompt for comprehension questions
        prompt = f"""
        Based on the following German text, create 2-5 comprehension questions in German. 
        The questions should test understanding of the text and should be appropriate for a German language learner.
        
        Text:
        {study_text}
        
        Please provide only the questions, numbered, without any additional text or explanations.
        """
        
        # Update the conversation history
        self.conversation_history.append({"role": "user", "content": prompt})
        
        try:
            # Send to OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                temperature=0.7,
            )
            
            questions = response.choices[0].message.content.strip()
            
            # Display questions in the Translation Box
            self.translation_textbox.delete(1.0, tk.END)
            self.translation_textbox.insert(tk.END, questions)
            
            # Add instructions for the user
            self.input_textbox.delete(1.0, tk.END)
            self.input_textbox.insert(tk.END, "Please answer the questions above in German. Type your answers here.")
            
            # Store the questions for later evaluation
            self.current_comprehension_questions = questions
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def add_highlight_functionality(self):
        """Add highlight functionality to the three main textboxes"""
        # Bind keyboard shortcuts
        self.root.bind('<Control-h>', self.highlight_selection)
        self.root.bind('<Control-Shift-H>', self.clear_highlight)
    
    def highlight_text(self, textbox):
        """Highlight selected text in the given textbox"""
        try:
            # Remove any existing highlight tags first
            textbox.tag_remove("highlight", "1.0", tk.END)
            
            # Check if there's a selection
            if textbox.tag_ranges(tk.SEL):
                start = textbox.index(tk.SEL_FIRST)
                end = textbox.index(tk.SEL_LAST)
                
                # Apply highlight tag
                textbox.tag_add("highlight", start, end)
        except tk.TclError:
            # No selection found
            pass
    
    def clear_text_highlight(self, textbox):
        """Clear highlight from the given textbox"""
        textbox.tag_remove("highlight", "1.0", tk.END)
    
    def highlight_selection(self, event=None):
        """Highlight selected text in the focused textbox (keyboard shortcut)"""
        # Get the currently focused widget
        focused_widget = self.root.focus_get()
        
        # Check if it's one of our textboxes
        if focused_widget in [self.vocabulary_textbox, self.study_textbox, self.translation_textbox]:
            self.highlight_text(focused_widget)
        
        return "break"  # Prevent default behavior
    
    def clear_highlight(self, event=None):
        """Clear highlight from the focused textbox (keyboard shortcut)"""
        # Get the currently focused widget
        focused_widget = self.root.focus_get()
        
        # Check if it's one of our textboxes
        if focused_widget in [self.vocabulary_textbox, self.study_textbox, self.translation_textbox]:
            self.clear_text_highlight(focused_widget)
        
        return "break"  # Prevent default behavior

# -------------------- END OF HIGHLIGHTING --------------
    def load_vocabulary(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

        if filename:
            self.current_voc_file = filename  # Save the loaded filename
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                self.vocabulary_textbox.delete(1.0, tk.END)  # Clear before inserting
                self.vocabulary_textbox.insert(tk.END, content)
                self.vocabulary = [line.strip() for line in content.splitlines() if line.strip()]
                self.load_current_voc += 1
                self.load_test_file()


    # -------------- REPEAT CHANGES IN OTHER TWO TEXTBOX SAVES ----
    def save_vocabulary(self):
        if not self.current_voc_file:  # If no file was loaded, ask where to save
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if filename:
                nwext = os.path.splitext(filename)[0] # nwext = name without extension (here '_VOC')
                if '_VOC' not in filename:
                    filename = nwext + '_VOC.txt'
                self.current_voc_file = filename
            else:
                self.current_voc_file = filename  # Update current file for future saves
        else:
            filename = self.current_voc_file  # Use the stored filename

        if filename:
            with open(filename, 'w', encoding='utf-8-sig') as file:
                content = self.vocabulary_textbox.get(1.0, tk.END)
                file.write(content)
            # Show success message with file path
            messagebox.showinfo("Success", f"File saved successfully at:\n{filename}")

    def save_study_text(self):
        if not self.current_study_file:  # If no file was loaded, ask where to save
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if filename:
                nwext = os.path.splitext(filename)[0] # nwext = name without extension (here '_TXT)
                if '_TXT' not in filename:
                    filename = nwext + '_TXT.txt'
                self.current_study_file = filename  # Update current file for future saves
        else:
            filename = self.current_study_file  # Use the stored filename

        if filename:
            with open(filename, 'w', encoding='utf-8-sig') as file:
                content = self.study_textbox.get(1.0, tk.END)
                file.write(content)
            # Show success message with file path
            messagebox.showinfo("Success", f"File saved successfully at:\n{filename}")

    def save_translation(self):
        if not self.current_translated_file:  # If no file was loaded, ask where to save
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if filename:
                nwext = os.path.splitext(filename)[0] # nwext = name without extension (here '_TRA)
                if '_TRA' not in filename:
                    filename = nwext + '_TRA.txt'
                self.current_translated_file = filename  # Update current file for future saves
        else:
            filename = self.current_translated_file  # Use the stored filename

        if filename:
            with open(filename, 'w', encoding='utf-8-sig') as file:
                content = self.translation_textbox.get(1.0, tk.END)
                file.write(content)
            # Show success message with file path
            messagebox.showinfo("Success", f"File saved successfully at:\n{filename}")

    def sort_vocabulary(self):
        # Get content from the textbox
        content = self.vocabulary_textbox.get(1.0, tk.END)
        
        # Process the content to remove duplicates while preserving order
        seen = set()
        unique_lines = []
        
        for line in content.splitlines():
            # Strip whitespace and skip empty lines
            stripped_line = line.strip()
            if not stripped_line:
                continue
                
            # Only add if we haven't seen this line before
            if stripped_line not in seen:
                seen.add(stripped_line)
                unique_lines.append(stripped_line)
        
        # Sort the unique lines alphabetically (case-insensitive)
        sorted_lines = sorted(unique_lines, key=lambda x: x.split('=')[0].strip().lower())
        
        # Join with newlines and update the textbox
        sorted_content = '\n'.join(sorted_lines) + '\n'  # Add final newline
        self.vocabulary_textbox.delete(1.0, tk.END)
        self.vocabulary_textbox.insert(tk.END, sorted_content)
        
        # Show how many duplicates were removed
        duplicate_count = len(content.splitlines()) - len(unique_lines)
        if duplicate_count > 0:
            messagebox.showinfo("Sort Complete", 
                            f"Sorted vocabulary alphabetically\n"
                            f"Removed {duplicate_count} duplicate entries")

    def clear_vocabulary(self):
        self.current_voc_file = None
        self.vocabulary_textbox.delete(1.0, tk.END)

    def load_study_text(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.current_study_file = filename  # Save the loaded filename
        if filename:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                self.study_textbox.insert(tk.END, content)


    def clear_study_text(self):
        self.current_study_file = None
        self.study_textbox.delete(1.0, tk.END)

    def capture_text(self):
        """
        Read English input from the GUI, translate to German using OpenAI, and display the result.
        """
        original_text = self.study_textbox.get("1.0", tk.END).strip()
        if not original_text:
            messagebox.showwarning("Input Empty", "Please enter text in the 'Study Text' box.")
            return

        try:
            prompt = ("""You are an expert translator, fluent in English and German. If the given text is in German, translate it into English.
                If the given text is in English then translate it into German. Just give me the most common expression for everyday speech \
                    unless the English is more formal or uses scientific jargon:\n\n"""
                f"English: \"{original_text}\"\n\nGerman:"
            )
            translated = self.ask_chatgpt(prompt, model_name="gpt-4o", temperature=0.3)

            self.translation_textbox.delete(1.0, tk.END)
            self.translation_textbox.insert(tk.END, translated)

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Translation Error", f"An error occurred: {e}")



    def add_notes(self):
        NotesEditor(self.root)

    def load_translation(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.current_translated_file = filename  # Save the loaded filename
        if filename:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                self.translation_textbox.insert(tk.END, content)


    def clear_translation(self):
        self.current_translated_file = None
        self.translation_textbox.delete(1.0, tk.END)
    

    def search_own_vocab(self):
        # Get the word to search from the input field
        search_word = self.dictionary_entry.get().strip().lower()  # Assuming you have an input_field
        
        # Get the vocabulary content from the textbox
        vocab_content = self.vocabulary_textbox.get("1.0", tk.END)
        
        if not search_word or not vocab_content.strip():
            messagebox.showwarning("Warning", "Please enter a word to search and load vocabulary first")
            return
        
        # Initialize result
        result = ""
        
        # Search through each line of the vocabulary
        for line in vocab_content.split('\n'):
            if '=' in line:  # Only process lines with translations
                left_side = line.split('=')[0].strip()
                right_side = line.split('=')[1].strip()
                
                # Check if search word is German (left side)
                german_words = left_side.split(',')[0].strip().lower()
                if search_word == german_words.lower():
                    # Found German word, return English meanings
                    result = f"Found: {left_side}\nMeanings: {right_side}\n\n"
                    break
                    
                # Check if search word is English (right side)
                english_words = [w.strip().lower() for w in right_side.split(',')]
                if search_word in english_words:
                    # Found English word, return German equivalent
                    result = f"Found: {right_side}\nGerman: {left_side}\n\n"
                    break
        
        # Display results in AI responses textbox
        if result:
            self.ai_responses_textbox.insert(tk.END, result)
        else:
            self.divert += 1
            self.ai_translate_word()
            
        
        # Auto-scroll to the bottom
        self.ai_responses_textbox.see(tk.END)

    def fetch_glosbe_examples(self):
        word = self.glosbe_search_entry.get().strip()
        if not word:
            return

        url = f"https://glosbe.com/de/en/{word}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.example_sentences_textbox.insert(tk.END, f"Failed to retrieve the page. Status code: {response.status_code}\n")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        examples_list = []

        for example in soup.find_all('div', class_='mt-1 w-full flex text-gray-900 text-sm py-1 px-2 dir-aware-border-start-2 border-gray-300 translation__example'):
            german_p = example.find('p', class_='w-1/2 dir-aware-pr-1')
            german = german_p.text.strip() if german_p else "N/A"

            english_p = example.find('p', class_='w-1/2 px-1 ml-2')
            english = english_p.text.strip() if english_p else "N/A"

            example_pair = f"{german} = {english}\n\n"
            examples_list.append(example_pair)

        self.example_sentences_textbox.delete(1.0, tk.END)
        for example in examples_list:
            self.example_sentences_textbox.insert(tk.END, example)

        # --------------------
    # AI: Translate a single word
    # --------------------
    def ai_translate_word(self):
        """
        Translate a single German or English word, applying specific formatting rules.
        """
        word = self.dictionary_entry.get().strip()
        if not word:
            return
        
        prompt = (
        "You will receive a word that is either in German or English.\n\n"
        "If the word is a **German noun**, respond in this format:\n"
        "Abfahrt, die, [Abfahrten, die] = departure, leaving, start\n\n"
        "If the word is an **English noun**, respond like this:\n"
        "fame = Berühmtheit, die; Ruhm, der\n\n"
        "If the word is a **German verb**, respond in this format:\n"
        "abfahren, [fuhr ab, abgefahren] = to depart, to leave, to set off\n\n"
        "If the word is an **English verb**, respond like this:\n"
        "depart = abfahren, [fuhr ab, abgefahren]\n\n"
        "If the word is an **English adjective**, give German equivalents separated by commas:\n"
        "happy = glücklich, froh, heiter\n\n"
        "Use 'to ' before each English verb meaning.\n"
        "Use semicolons between multiple German meanings when translating English nouns.\n"
        "If unsure of the language, assume it is German."
    )
        full_prompt = f"{prompt}\n\n{word}"


        try:
            translated_word = self.ask_chatgpt(full_prompt, model_name="gpt-4o", temperature=0.3)
            if self.divert > 0:
                self.ai_responses_textbox.insert(tk.END, translated_word + "\n")
                self.divert = 0
            else:
                self.vocabulary_textbox.insert(tk.END, translated_word + "\n")
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Translation Error", f"An error occurred: {e}")


    def append_ai_responses_to_file(self):
        # Ask user to select file (can navigate directories and create new folders)
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            title="Select file to append to"
        )

        if filename:
            try:
                with open(filename, 'a+', encoding='utf-8-sig') as file:
                    content = self.ai_responses_textbox.get(1.0, tk.END)
                    file.write("\n\n")  # Add separation from previous content
                    file.write(content)
                messagebox.showinfo("Success", f"Content appended to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to append to file:\n{str(e)}")


    def fetch_langenscheidt(self):
        word = self.dictionary_entry.get().strip()
        if not word:
            return

        url = f"https://en.langenscheidt.com/german-english/{word}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.vocabulary_textbox.insert(tk.END, f"Failed to retrieve the page. Status code: {response.status_code}\n")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        myList = []

        for transl in soup.find_all('a', class_='blue'):
            myStr = transl.find('span', class_='btn-inner').text
            article = soup.find('span', class_='full').text
            if article == 'Femininum | feminine':
                article = 'die'
            elif article == 'Maskulinum | masculine':
                article = 'der'
            elif article == 'Neutrum | neuter':
                article = 'das'
            else:
                article = ''
            myStr = myStr.strip()
            myList.append(myStr)

        meaning = ', '.join(myList)
        self.vocabulary_textbox.insert(tk.END, f"{word}, {article} = {meaning}\n")

    def load_examples(self):
        filename = r"C:\Users\George\Desktop\German_Study_Files\example-sentences.txt"
        # filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.current_example_sentences_file = filename  # Save the loaded filename
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                self.example_sentences_textbox.delete(1.0, tk.END)  # Clear before inserting
                self.example_sentences_textbox.insert(tk.END, content)
                #self.vocabulary = [line.strip() for line in content.splitlines() if line.strip()]

    def save_examples(self):
            filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            title="Select file to append to"
        )
        
            if filename:
                try:
                    with open(filename, 'a+', encoding='utf-8-sig') as file:
                        content = self.example_sentences_textbox.get(1.0, tk.END)
                        file.write("\n\n")  # Add separation from previous content
                        file.write(content)
                    messagebox.showinfo("Success", f"Content appended to:\n{filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to append to file:\n{str(e)}")
            
    def clear_example_sentences(self):
        self.current_example_sentences_file = None
        self.example_sentences_textbox.delete(1.0, tk.END)

    def clear_examples_input(self):
        self.glosbe_search_entry.delete(0, tk.END)

    def load_test_file(self):
        if self.load_current_voc > 0:
            filename = self.current_voc_file
        else:
            self.count_test_num = 0 # debug
            # in the two lines below and elsewehere I replaced 'filename' with 'self.testfile'
            filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.test_filename_label.config(text=f"File is: {filename}")
            with open(filename, 'r', encoding='utf-8-sig') as file:
                self.vocabulary = [line.strip() for line in file.readlines() if line.strip()]
            self.display_random_word()
            self.load_current_voc = 0
    
    def display_random_word(self):
        if not self.vocabulary:
            self.test_textbox.delete(1.0, tk.END)
            self.test_textbox.insert(tk.END, "No vocabulary loaded. Click again!\n")
            return

        self.current_word = random.choice(self.vocabulary)
        self.test_textbox.delete(1.0, tk.END)
        self.test_textbox.insert(tk.END, "Please translate the following:\n")

        self.count_test_num += 1
        self.count_test_num_label.config(text=f"{self.count_test_num}")

        # Try to split the line regardless of space around '='
        try:
            parts = self.current_word.split('=')
            german_part = parts[0].strip()
            english_part = parts[1].strip()
        except IndexError:
            # In case the line is malformed
            self.test_textbox.insert(tk.END, "⚠️ Malformed vocabulary line.\n")
            return

        if self.flip_mode:
            self.test_textbox.insert(tk.END, f"--> {english_part}\n")
        else:
            self.test_textbox.insert(tk.END, f"--> {german_part}\n")

        # Clear the input field before displaying the new question
        self.answer_entry.delete(0, tk.END)

        # Dynamically detect if any English translation starts with "to "
        if not self.flip_mode:
            english_entries = [e.strip().lower() for e in english_part.split(',')]
            if any(entry.startswith("to ") for entry in english_entries):
                self.answer_entry.delete(0, tk.END)
                self.answer_entry.insert(0, "to ")
                self.answer_entry.update_idletasks()  # force a GUI refresh


    def toggle_flip_mode(self):
        self.flip_mode = not self.flip_mode
        self.count_test_num = 0
        self.display_random_word()

    def next_word(self):
        self.display_random_word()
    

    def clear_input(self):
        self.answer_entry.delete(0, tk.END)

    def clear_entry(self):
        self.dictionary_entry.delete(0, tk.END)

    def clear_test(self):
        self.vocabulary = []
        self.score_label.config(text="0%")
        self.score = 0
        self.total_questions = 0  # Total number of questions asked
        self.correct_answers = 0  # Number of correct answers
        self.test_filename_label.config(text="File is: ") # debug
        self.test_textbox.delete(1.0, tk.END)

    def check_answer(self, event=None):
        user_input_raw = self.answer_entry.get().strip()
        user_answer = user_input_raw.lower()

        # Remove leading 'to ' if present for comparison
        if user_answer.startswith("to "):
            user_answer = user_answer[3:].strip()

        # Determine the correct answers
        if self.flip_mode:
            correct_answers_raw = self.current_word.split(' = ')[0].split(', ')
        else:
            correct_answers_raw = self.current_word.split(' = ')[1].split(', ')

        # Make a comparison list without 'to ' prefixes
        correct_answers_normalized = [
            answer.lower().strip()[3:].strip() if answer.lower().strip().startswith("to ")
            else answer.lower().strip()
            for answer in correct_answers_raw
        ]

        self.total_questions += 1

        if user_answer in correct_answers_normalized:
            self.test_textbox.insert(tk.END, "*** Congratulations!!! ***\n")
            self.test_textbox.insert(tk.END, f"*** YES, the correct answer is: {', '.join(correct_answers_raw)} ***\n")
            self.correct_answers += 1
        else:
            self.test_textbox.insert(tk.END, f"*** You wrote:  {user_input_raw}\n I'm sorry. The correct answer is: {', '.join(correct_answers_raw)} ***\n")
            self.save_failed_word()  # <== New line to call the revision of words failed to translate

        # Calculate score
        if self.total_questions > 0:
            self.score = round((self.correct_answers / self.total_questions) * 100)
            self.score_label.config(text=f"{self.score}%")

        self.clear_input()
    
    # Extended functionality to revise mistakes
    def save_failed_word(self):
        """
        Save the current word to the appropriate revision file if the user gets it wrong.
        """
        filename = "revise-de_VOC.txt" if not self.flip_mode else "revise-en_VOC.txt"
        missed_line = self.current_word.strip()

        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            lines = []

        if missed_line not in lines:
            with open(filename, 'a', encoding='utf-8-sig') as f:
                f.write(missed_line + "\n")
    

    def load_revision_file(self):
        """
        Load revise-de_VOC.txt or revise-en_VOC.txt as the new active vocabulary for testing.
        """
        filename = "revise-de_VOC.txt" if not self.flip_mode else "revise-en_VOC.txt"

        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                self.vocabulary = [line.strip() for line in f if line.strip()]
            self.test_textbox.delete(1.0, tk.END)
            self.test_textbox.insert(tk.END, f"Loaded {len(self.vocabulary)} revision items from {filename}\n")
        except FileNotFoundError:
            self.test_textbox.delete(1.0, tk.END)
            self.test_textbox.insert(tk.END, f"No revision file found: {filename}\n")
        
        self.display_random_word()


class NotesEditor:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Notes Editor")
        self.window.geometry("500x400")
        self.current_notes_file = None # debug

        # Text area
        self.text = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, width=60, height=20)
        self.text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Button frame
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=5)

        # Buttons
        tk.Button(btn_frame, text="Open Default File", command=self.open_default_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Exit", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

        # Current file path
        self.filepath = None

    def open_default_file(self):
        filename = notes_filename
        # filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.current_notes_file = filename  # Save the loaded filename
        if filename:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                self.text.insert(tk.END, content)
        
    def save_file(self):
        """Save to current file or prompt for new file if none exists"""
        if not self.current_notes_file:  # If no file was loaded, ask where to save
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if filename:
                self.current_notes_file = filename  # Update current file for future saves
        else:
            filename = self.current_notes_file  # Use the stored filename

        if filename:
            with open(filename, 'w', encoding='utf-8-sig') as file:
                content = self.text.get(1.0, tk.END)
                file.write(content)
            # Show success message with file path
            messagebox.showinfo("Success", f"File saved successfully at:\n{filename}")


    def save_as_file(self):
        """Prompt user for save location"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(self.text.get("1.0", tk.END))
                self.filepath = filepath
                messagebox.showinfo("Saved", f"Notes saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VocabularyApp(root)
    root.mainloop()