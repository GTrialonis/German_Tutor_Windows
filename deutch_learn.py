from openai import OpenAI
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext, messagebox
import random
import requests
from bs4 import BeautifulSoup
import tkinter.font as tkFont
import os
import threading
from gtts import gTTS
import pygame
import tempfile
import time
import re

# Initialize pygame mixer
pygame.mixer.init()

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

def configure_openai():
    """Set up the OpenAI API key and verify connectivity."""
    try:
        print("OpenAI API configured successfully.")
    except Exception as e:
        messagebox.showerror("API Configuration Error", f"Failed to configure OpenAI API: {e}")
        exit()

class Tooltip:
    """Simple tooltip class for tkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Display the tooltip."""
        if self.tooltip:
            return
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        
        # Position tooltip near cursor
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create label with text
        label = tk.Label(
            self.tooltip,
            text=self.text,
            background="#FFFFE0",
            foreground="#000000",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9),
            padx=5,
            pady=3
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide the tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class VocabularyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("German Language Tutor")
        self.root.configure(bg="#222")
        self.root.state('zoomed')  # Maximize window

        self.root.update_idletasks()
        print(f"Root window geometry after zoom: {self.root.winfo_geometry()}")

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history = [
            {"role":"system", "content":"You are a helpful assistant for German–English practice."}
        ]

        # Core application variables
        self.vocabulary = []
        self.current_word = None
        self.current_language = "german"
        self.current_voc_file = None
        self.current_study_file = None
        self.current_translation_file = None
        self.translation_content_cleared = False  # Track if translation content was cleared
        self.current_example_sentences_file = None
        self.current_ai_responses_file = None
        self.score = 0
        self.count_test_num = 0
        self.total_questions = 0
        self.correct_answers = 0
        self.flip_mode = False
        self.left_section_font = tkFont.Font(family="Helvetica", size=10, weight="normal")
        self.conversation_history = []
        self.divert = 0
        self.load_current_voc = 0

        # TTS configuration
        self.tts_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.current_voice = "nova"

        # Listening comprehension variables
        self.listening_comprehension_text = ""
        self.current_questions = []
        self.current_question_index = 0
        self.listening_score = 0
        self.total_listening_questions = 0
        self.listening_dir = "list_compr_files"
        os.makedirs(self.listening_dir, exist_ok=True)

        # Text-to-speech variables
        self.is_reading = False
        self.current_audio_file = None
        self.reading_paused = False
        self.reading_thread = None
        self.speech_playing = False

        # Font and style configuration
        self.small_button_font = tkFont.Font(family="Helvetica", size=8, weight="normal")
        self.setup_styles()
        
        # Evaluation tracking
        self.evaluated_questions = set()
        # Reading comprehension state
        self.reading_comprehension_active = False
        self.reading_questions = []
        self.current_reading_question_index = 0
        self.reading_questions_generated = False

        # Create UI sections
        self.create_left_section()
        self.create_middle_section()
        self.create_right_section()
        self.add_highlight_functionality()

        # Ensure Prompt AI button is enabled on startup
        self.root.after(100, self.ensure_prompt_ai_enabled)

    def setup_styles(self):
        """Configure all button styles"""
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Define color styles for buttons
        color_styles = {
            'SmallPurple.TButton': {'background': '#ca74ea', 'foreground': 'black'},
            'SmallBlue.TButton': {'background': '#73A2D0', 'foreground': 'black'},
            'SmallBrownish.TButton': {'background': "#d4d0ac", 'foreground': 'black'},
            'SmallGreen.TButton': {'background': '#008844', 'foreground': 'black'},
            'SmallRed.TButton': {'background': '#AA0000', 'foreground': 'black'},
            'SmallGoldBrown.TButton': {'background': '#AA8800', 'foreground': 'black'},
            'SmallLightPurple.TButton': {'background': '#cbb0e0', 'foreground': 'black'},
            'SmallOrange.TButton': {'background': 'orange', 'foreground': 'black'},
            'SmallDarkBlue.TButton': {'background': '#005588', 'foreground': 'black'},
            'SmallGrayBlue.TButton': {'background': '#9DC1E4', 'foreground': 'black'},
            'SmallDarkOlive.TButton': {'background': '#95C068', 'foreground': 'black'},
            'SmallOliveGreen.TButton': {'background': '#95946A', 'foreground': 'black'},
            'SmallGreenish.TButton': {'background': '#AABD7E', 'foreground': 'black'},
            'SmallWhiteBlue.TButton': {'background': '#AACCC6', 'foreground': 'black'},
            'SmallDarkOrange.TButton': {'background': '#AA5200', 'foreground': 'black'},
            'SmallWhite.TButton': {'background': '#7B7D7D', 'foreground': 'white'},
            'SmallGoldYellow.TButton': {'background': '#EBCE65', 'foreground': 'black'},
            'SmallDarkRed.TButton': {'background': '#8B0000', 'foreground': 'white'},
            'SmallBlueish.TButton': {'background': '#5D6D7E', 'foreground': 'white'},
            'SmallGoldenSummer.TButton': {'background': '#d4a373', 'foreground': 'black'}        
            }
        
        for style_name, colors in color_styles.items():
            self.style.configure(style_name, 
                               background=colors['background'],
                               foreground=colors['foreground'],
                               font=self.small_button_font)

    # === CORE FUNCTIONALITY METHODS ===

    def ask_chatgpt(self, prompt: str, model_name="gpt-4o", temperature=0.7) -> str:
        """Send prompt to ChatGPT and return response"""
        resp = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()

    def trigger_next_word_and_refocus(self, event=None):
        """Triggers next word action and refocuses answer entry"""
        self.next_word()
        self.answer_entry.focus_set()
        self.answer_entry.delete(0, tk.END)
        return "break"

    # === LISTENING COMPREHENSION FIXED METHODS ===

    def create_listening_comprehension(self):
        """Create the listening comprehension popup window - FIXED VERSION"""
        listen_comp_window = tk.Toplevel(self.root)
        listen_comp_window.title("Listening Comprehension")
        listen_comp_window.configure(bg="#222")
        listen_comp_window.geometry("400x300")
        listen_comp_window.transient(self.root)
        listen_comp_window.grab_set()
        
        # Center the window
        listen_comp_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (listen_comp_window.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (listen_comp_window.winfo_height() // 2)
        listen_comp_window.geometry(f"+{x}+{y}")
        
        # Main frame
        frame = tk.Frame(listen_comp_window, bg="#222")
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Voice selection
        voice_label = tk.Label(frame, text="Select Voice:", bg="#222", fg="white")
        voice_label.pack(anchor=tk.W, pady=(0, 5))
        
        voice_var = tk.StringVar(value="alloy")
        voice_frame = tk.Frame(frame, bg="#222")
        voice_frame.pack(fill=tk.X, pady=(0, 15))
        
        voices = [("Alloy", "alloy"), ("Echo", "echo"), ("Fable", "fable"), 
                ("Onyx", "onyx"), ("Nova", "nova"), ("Shimmer", "shimmer")]
        
        for name, value in voices:
            rb = tk.Radiobutton(voice_frame, text=name, variable=voice_var, value=value,
                            bg="#222", fg="white", selectcolor="#444")
            rb.pack(side=tk.LEFT, padx=(0, 10))
        
        # Button frame
        btn_frame = tk.Frame(frame, bg="#222")
        btn_frame.pack(fill=tk.X, pady=20)
        
        def on_file_select():
            """Handle file selection for listening comprehension"""
            filename = filedialog.askopenfilename(
                title="Select German Text File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as file:
                        self.listening_comprehension_text = file.read()
                    
                    self.current_voice = voice_var.get()
                    listen_comp_window.destroy()
                    
                    # Start the listening comprehension flow
                    self.start_listening_comprehension_flow()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Could not read file: {e}")
            else:
                # User cancelled file selection - re-enable Prompt AI button
                self.ensure_prompt_ai_enabled()
                listen_comp_window.destroy()
        
        def on_cancel():
            """Handle cancel operation"""
            self.ensure_prompt_ai_enabled()
            listen_comp_window.destroy()

        def on_clipboard_select():
            """Use text currently in the clipboard for listening comprehension."""
            text = ""
            try:
                text = listen_comp_window.clipboard_get()
            except Exception:
                try:
                    text = self.root.clipboard_get()
                except Exception:
                    text = ""

            if not text or not text.strip():
                messagebox.showwarning("No Text", "Clipboard has no text to use for listening comprehension.", parent=listen_comp_window)
                return

            self.listening_comprehension_text = text
            self.current_voice = voice_var.get()
            listen_comp_window.destroy()
            self.start_listening_comprehension_flow()
        
        # Create buttons
        ttk.Button(btn_frame, text="Select Text File", 
                  style='SmallBlue.TButton',
                  command=on_file_select).pack(pady=5, fill=tk.X)
        
        ttk.Button(btn_frame, text="Search Internet for German Text", 
              style='SmallGreen.TButton',
              command=lambda: self.search_german_text(listen_comp_window, voice_var.get())).pack(pady=5, fill=tk.X)

        ttk.Button(btn_frame, text="Use Clipboard Text",
              style='SmallPurple.TButton',
              command=on_clipboard_select).pack(pady=5, fill=tk.X)

        ttk.Button(btn_frame, text="Cancel", 
              style='SmallRed.TButton',
              command=on_cancel).pack(pady=5, fill=tk.X)
        
        # Handle window close
        listen_comp_window.protocol("WM_DELETE_WINDOW", on_cancel)

    def start_listening_comprehension_flow(self):
        """Start the complete listening comprehension flow"""
        if not self.listening_comprehension_text:
            messagebox.showwarning("No Text", "No German text available.")
            return
        
        # Disable Prompt AI button during session
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state="disabled")
        
        # Enable Evaluate Answer button
        if hasattr(self, 'eval_answer_btn'):
            self.eval_answer_btn.config(state="normal")
        
        # Reset evaluation tracking
        self.evaluated_questions = set()
        
        # Show reading controls first
        self.show_reading_controls(
            self.listening_comprehension_text,
            "Listening Comprehension Text",
            self.current_voice
        )

    def show_reading_controls(self, text_content, source_name, voice):
        """Show reading controls window"""
        self.stop_reading()
        
        controls_window = tk.Toplevel(self.root)
        controls_window.title(f"Reading: {source_name}")
        controls_window.configure(bg="#222")
        controls_window.geometry("400x200")
        controls_window.transient(self.root)
        controls_window.attributes('-topmost', True)
        
        # Center window
        controls_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (controls_window.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (controls_window.winfo_height() // 2)
        controls_window.geometry(f"+{x}+{y}")
        
        # Content frame
        content_frame = tk.Frame(controls_window, bg="#222")
        content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # UI elements
        source_label = tk.Label(content_frame, text=f"Source: {source_name}", 
                              bg="#222", fg="white", font=("Helvetica", 10, "bold"))
        source_label.pack(pady=(0, 10))
        
        status_label = tk.Label(content_frame, text="Ready to read", 
                              bg="#222", fg="lightgreen", font=("Helvetica", 9))
        status_label.pack(pady=(0, 10))
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(content_frame, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        button_frame = tk.Frame(content_frame, bg="#222")
        button_frame.pack(fill=tk.X)
        
        def on_reading_complete():
            """Handle reading completion"""
            controls_window.destroy()
            self.generate_listening_questions()
        
        play_button = ttk.Button(button_frame, text="Start Reading", 
                               style='SmallGreen.TButton',
                               command=lambda: self.start_reading_with_callback(
                                   text_content, play_button, pause_button, status_label, 
                                   progress_var, voice, on_reading_complete))
        play_button.pack(side=tk.LEFT, padx=(0, 10))
        
        pause_button = ttk.Button(button_frame, text="Pause", 
                                style='SmallGoldBrown.TButton',
                                command=lambda: self.toggle_pause(pause_button, status_label),
                                state=tk.DISABLED)
        pause_button.pack(side=tk.LEFT, padx=(0, 10))
        
        stop_button = ttk.Button(button_frame, text="Stop", 
                               style='SmallRed.TButton',
                               command=lambda: self.stop_reading_ui(controls_window, play_button, pause_button, status_label, progress_var))
        stop_button.pack(side=tk.LEFT)
        
        controls_window.protocol("WM_DELETE_WINDOW", 
                              lambda: self.stop_reading_ui(controls_window, play_button, pause_button, status_label, progress_var))
        
        self.current_controls_window = controls_window

    def start_reading_with_callback(self, text_content, play_button, pause_button, status_label, progress_var, voice, completion_callback):
        """Start reading with completion callback"""
        self.toggle_reading(text_content, play_button, pause_button, status_label, progress_var, voice)
        
        def check_reading_complete():
            if not self.is_reading:
                completion_callback()
            else:
                self.root.after(1000, check_reading_complete)
        
        check_reading_complete()

    def create_translation_listen_popup(self):
        """Popup to choose to listen to a translation file or the Translation Box content."""
        popup = tk.Toplevel(self.root)
        popup.title("Listen to Translation")
        popup.configure(bg="#222")
        popup.geometry("380x180")
        popup.transient(self.root)
        popup.grab_set()

        # Center
        popup.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

        tk.Label(popup, text="Listen to Translation", bg="#222", fg="white", font=("Helvetica", 11, "bold")).pack(pady=(10, 5))

        # Buttons frame
        btn_frame = tk.Frame(popup, bg="#222")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        def choose_file():
            filename = filedialog.askopenfilename(title="Select translation file", filetypes=[("Translation files", "*_TRA.txt"), ("Text files", "*.txt"), ("All files", "*.*")], parent=popup)
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8-sig') as f:
                        text = f.read()
                    popup.destroy()
                    # Use current voice if available
                    voice = getattr(self, 'current_voice', 'alloy')
                    self.speak_text(text, voice)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read file: {e}", parent=popup)

        def read_from_box():
            text = self.translation_textbox.get(1.0, tk.END).strip()
            if not text:
                messagebox.showwarning("No Text", "Translation Box is empty.", parent=popup)
                return
            popup.destroy()
            voice = getattr(self, 'current_voice', 'alloy')
            self.speak_text(text, voice)

        def on_cancel():
            popup.destroy()

        ttk.Button(btn_frame, text="Select _TRA.txt File", style='SmallBlue.TButton', command=choose_file).pack(pady=6, fill=tk.X)
        ttk.Button(btn_frame, text="Read from Translation Box", style='SmallGreen.TButton', command=read_from_box).pack(pady=6, fill=tk.X)
        ttk.Button(btn_frame, text="Cancel", style='SmallRed.TButton', command=on_cancel).pack(pady=6, fill=tk.X)

        popup.protocol("WM_DELETE_WINDOW", on_cancel)

    def generate_listening_questions(self):
        """Generate comprehension questions based on the German text"""
        try:
            prompt = f"""
            Basierend auf dem folgenden deutschen Text, erstelle 3-5 Verständnisfragen auf Deutsch.
            Die Fragen sollten das Hörverständnis testen und für Deutschlernende geeignet sein.
            
            WICHTIG: Gib die Fragen in diesem Format zurück:
            
            FRAGE 1: [Hier kommt die erste Frage]
            FRAGE 2: [Hier kommt die zweite Frage]
            FRAGE 3: [Hier kommt die dritte Frage]
            
            Text:
            {self.listening_comprehension_text}
            
            Stelle sicher, dass jede Frage mit "FRAGE X:" beginnt.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            
            questions_text = response.choices[0].message.content.strip()
            self.parse_questions(questions_text)
            self.start_question_session()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate questions: {e}")

    def parse_questions(self, questions_text):
        """Parse questions from AI response"""
        questions = []
        lines = questions_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('FRAGE') and ':' in line:
                question = line.split(':', 1)[1].strip()
                if question:
                    questions.append(question)
        
        # Fallback if no questions found
        if not questions:
            questions = [
                "Was ist die Hauptidee des Textes?",
                "Welche wichtigen Informationen wurden erwähnt?",
                "Was können Sie über das Thema sagen?"
            ]
        
        self.current_questions = questions
        self.total_listening_questions = len(questions)
        self.current_question_index = 0
        self.listening_score = 0

    def start_question_session(self):
        """Start the question answering session"""
        if not self.current_questions:
            messagebox.showwarning("No Questions", "No questions were generated.")
            return
        # If Translation Box already has content, ask user whether to save it
        existing_translation = self.translation_textbox.get(1.0, tk.END).strip()
        if existing_translation:
            prompt = "Translation Box contains text. Save current content before replacing?"
            choice = messagebox.askyesnocancel("Translation Box Not Empty", prompt, parent=self.root)
            if choice is None:
                # User cancelled - abort
                return
            elif choice:
                # User chose to save first
                try:
                    self.save_translation()
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save translation: {e}", parent=self.root)

        # Display first question in translation box
        self.translation_textbox.delete(1.0, tk.END)
        self.translation_textbox.insert(tk.END, "Answer these questions in German:\n\n")
        
        for i, question in enumerate(self.current_questions, 1):
            self.translation_textbox.insert(tk.END, f"{i}. {question}\n")
        
        # Instructions in input box
        self.input_textbox.delete(1.0, tk.END)
        self.input_textbox.insert(tk.END, "Type your answers to the questions here, one after another. Click 'Eval.Answer' after each answer.")
        # Note: Do NOT save the inserted comprehension questions to the translation file.
        # Only the user's pre-existing translation will be saved earlier if they chose to.

    def handle_listening_answer(self):
        """Handle answer evaluation for listening comprehension"""
        if not self.current_questions:
            self.prompt_inputbox()
            return
        
        user_answer = self.input_textbox.get(1.0, tk.END).strip()
        
        if not user_answer:
            messagebox.showwarning("No Answer", "Please type your answer before submitting.")
            return
        
        if self.current_question_index in self.evaluated_questions:
            messagebox.showinfo("Already Evaluated", "This question has already been evaluated. Please proceed to next question.")
            return
        
        self.evaluate_listening_answer(user_answer)
        self.evaluated_questions.add(self.current_question_index)
        
        # Move to next question or end session
        self.current_question_index += 1
        if self.current_question_index >= len(self.current_questions):
            self.end_listening_comprehension_session()
        else:
            messagebox.showinfo("Next Question", f"Please answer question {self.current_question_index + 1}")

    def evaluate_listening_answer(self, user_answer):
        """Evaluate listening comprehension answer"""
        try:
            current_question = self.current_questions[self.current_question_index]
            
            prompt = f"""
            Evaluate this German language answer:

            QUESTION: {current_question}
            ANSWER: {user_answer}

            Provide evaluation in this format:
            SCORE: X/5
            FEEDBACK: [Your feedback in German]
            CORRECTION: [Corrected version if needed, otherwise empty]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            
            evaluation = response.choices[0].message.content.strip()
            self.display_evaluation(evaluation, user_answer, current_question)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not evaluate answer: {e}")

    def display_evaluation(self, evaluation, user_answer, question):
        """Display evaluation results"""
        self.ai_responses_textbox.insert(tk.END, f"\n{'='*50}\n")
        self.ai_responses_textbox.insert(tk.END, f"QUESTION: {question}\n")
        self.ai_responses_textbox.insert(tk.END, f"YOUR ANSWER: {user_answer}\n")
        self.ai_responses_textbox.insert(tk.END, f"EVALUATION:\n{evaluation}\n")
        self.ai_responses_textbox.see(tk.END)

    def end_listening_comprehension_session(self):
        """End the listening comprehension session"""
        # Re-enable buttons
        if hasattr(self, 'eval_answer_btn'):
            self.eval_answer_btn.config(state="disabled")
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state="normal")
        
        # Clear session data
        self.current_questions = []
        self.evaluated_questions = set()
        self.current_question_index = 0
        
        messagebox.showinfo("Session Complete", "All questions have been evaluated!")

    # === READING COMPREHENSION METHODS ===

    def parse_reading_questions(self, questions_text):
        """Parse generated reading comprehension questions into a list."""
        questions = []
        lines = questions_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if (line.lower().startswith('frage') or line.lower().startswith('question')) and ':' in line:
                q = line.split(':', 1)[1].strip()
                if q:
                    # Remove leading numbers like "1. ", "2. ", etc.
                    q = re.sub(r'^\d+\.\s*', '', q)
                    questions.append(q)
            else:
                # Accept bare lines as questions, but remove leading numbers
                q = re.sub(r'^\d+\.\s*', '', line)
                if q:
                    questions.append(q)

        if not questions:
            questions = [
                "Was ist die Hauptidee des Textes?",
                "Nenne zwei wichtige Details aus dem Text.",
                "Welche Schlussfolgerung kann man aus dem Text ziehen?"
            ]

        self.reading_questions = questions
        self.current_reading_question_index = 0
        self.reading_questions_generated = True

    def start_reading_comprehension_session(self):
        """Begin a reading-comprehension question-evaluation session."""
        if not self.reading_questions:
            messagebox.showwarning("No Questions", "No reading comprehension questions available.")
            return

        # If Translation Box already has content, ask user whether to save it
        existing_translation = self.translation_textbox.get(1.0, tk.END).strip()
        if existing_translation:
            prompt = "Translation Box contains text. Save current content before replacing?"
            choice = messagebox.askyesnocancel("Translation Box Not Empty", prompt, parent=self.root)
            if choice is None:
                return
            elif choice:
                try:
                    self.save_translation()
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save translation: {e}", parent=self.root)

        # Display questions in Translation Box
        self.translation_textbox.delete(1.0, tk.END)
        self.translation_textbox.insert(tk.END, "Answer these questions in German:\n\n")
        for i, q in enumerate(self.reading_questions, 1):
            self.translation_textbox.insert(tk.END, f"{i}. {q}\n")

        # Instructions for the user
        self.input_textbox.delete(1.0, tk.END)
        self.input_textbox.insert(tk.END, "Type your answer to the current question here. Click 'Eval.Answer' after each answer.")

        # Disable Prompt AI and enable Eval.Answer
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state="disabled")
        if hasattr(self, 'eval_answer_btn'):
            self.eval_answer_btn.config(state="normal")

        # Create an End Reading button near prompt controls so user can finish session
        try:
            parent = self.prompt_ai_button.master
            if not hasattr(self, 'end_reading_btn') or not getattr(self, 'end_reading_btn'):
                self.end_reading_btn = ttk.Button(parent, text="End Reading", style='SmallRed.TButton', command=self.end_reading_comprehension_session)
                self.end_reading_btn.pack(side='left', padx=3, pady=3)
        except Exception:
            pass

        self.reading_comprehension_active = True
        self.evaluated_questions = set()

    def handle_evaluation(self):
        """Unified handler for Eval.Answer that dispatches to reading or listening flows."""
        if getattr(self, 'reading_comprehension_active', False):
            self.handle_reading_answer()
        elif getattr(self, 'current_questions', None):
            self.handle_listening_answer()
        else:
            # Default behaviour: send prompt to AI
            self.prompt_inputbox()

    def handle_reading_answer(self):
        """Evaluate the user's answer for the current reading question."""
        if not self.reading_questions:
            self.prompt_inputbox()
            return

        idx = self.current_reading_question_index
        user_answer = self.input_textbox.get(1.0, tk.END).strip()
        if not user_answer:
            messagebox.showwarning("No Answer", "Please type your answer before submitting.")
            return

        if idx in self.evaluated_questions:
            messagebox.showinfo("Already Evaluated", "This question has already been evaluated. Please proceed to next question.")
            return

        # Build evaluation prompt using Study Text as context
        current_question = self.reading_questions[idx]
        study_text = self.study_textbox.get(1.0, tk.END).strip()

        try:
            prompt = f"""
            Evaluate this German language answer in the context of the provided Study Text.

            STUDY TEXT:
            {study_text}

            QUESTION: {current_question}
            ANSWER: {user_answer}

            Provide evaluation in this format:
            SCORE: X/5
            FEEDBACK: [Your feedback in German]
            CORRECTION: [Corrected version if needed]
            """

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            evaluation = response.choices[0].message.content.strip()
            self.display_evaluation(evaluation, user_answer, current_question)

            # Mark evaluated and advance
            self.evaluated_questions.add(idx)
            self.current_reading_question_index += 1

            if self.current_reading_question_index >= len(self.reading_questions):
                self.end_reading_comprehension_session()
            else:
                self.show_next_question_popup()

        except Exception as e:
            messagebox.showerror("Error", f"Could not evaluate answer: {e}")

    def show_next_question_popup(self):
        """Modal popup informing user to proceed to next question and focusing input."""
        popup = tk.Toplevel(self.root)
        popup.transient(self.root)
        popup.grab_set()
        popup.title("Next Question")
        popup.configure(bg="#222")
        popup.geometry("300x120")

        popup.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

        tk.Label(popup, text=f"Proceed to question {self.current_reading_question_index + 1}", bg="#222", fg="white").pack(pady=(20, 10))
        def on_next():
            popup.destroy()
            # Clear input box and focus for next answer
            try:
                self.input_textbox.delete(1.0, tk.END)
                self.input_textbox.focus_set()
            except Exception:
                pass

        ttk.Button(popup, text="Next", style='SmallGreen.TButton', command=on_next).pack(pady=5)

    def end_reading_comprehension_session(self):
        """End the reading comprehension session and restore UI state."""
        # Disable Eval button, enable Prompt AI
        try:
            if hasattr(self, 'eval_answer_btn'):
                self.eval_answer_btn.config(state="disabled")
            if hasattr(self, 'prompt_ai_button'):
                self.prompt_ai_button.config(state="normal")
        except Exception:
            pass

        # Destroy End button if present
        try:
            if hasattr(self, 'end_reading_btn') and getattr(self, 'end_reading_btn'):
                self.end_reading_btn.destroy()
                self.end_reading_btn = None
        except Exception:
            pass

        # Clear session state
        self.reading_comprehension_active = False
        self.reading_questions = []
        self.current_reading_question_index = 0
        self.reading_questions_generated = False
        self.evaluated_questions = set()

        messagebox.showinfo("Session Complete", "Reading comprehension session ended.")

    # === TEXT-TO-SPEECH METHODS ===

    def toggle_reading(self, text_content, play_button, pause_button, status_label, progress_var, voice):
        """Start or resume reading"""
        if not self.is_reading:
            self.is_reading = True
            self.reading_paused = False
            play_button.config(state=tk.DISABLED)
            pause_button.config(state=tk.NORMAL)
            status_label.config(text="Reading...", fg="lightgreen")
            progress_var.set(0)
            
            self.reading_thread = threading.Thread(
                target=self.read_text,
                args=(text_content, status_label, progress_var, play_button, pause_button, voice),
                daemon=True
            )
            self.reading_thread.start()
        elif self.reading_paused:
            self.reading_paused = False
            pygame.mixer.music.unpause()
            pause_button.config(text="Pause")
            status_label.config(text="Reading...", fg="lightgreen")

    def read_text(self, text_content, status_label, progress_var, play_button, pause_button, voice):
        """Read text using TTS"""
        try:
            # Helper: split into manageable chunks to avoid API length limits
            def chunk_text_local(text, max_chars=4000):
                import re
                if not text:
                    return []
                if len(text) <= max_chars:
                    return [text]
                # Split on sentence boundaries if possible
                sentences = re.split(r'(?<=[\.\!\?])\s+', text)
                chunks = []
                current = ""
                for s in sentences:
                    if len(current) + len(s) + 1 <= max_chars:
                        current = (current + " " + s).strip()
                    else:
                        if current:
                            chunks.append(current)
                        # If single sentence too long, hard-split it
                        if len(s) > max_chars:
                            for i in range(0, len(s), max_chars):
                                chunks.append(s[i:i+max_chars])
                            current = ""
                        else:
                            current = s
                if current:
                    chunks.append(current)
                return chunks

            def generate_audio_files_for_text(text, voice, max_chars=4000):
                audio_files = []
                chunks = chunk_text_local(text, max_chars=max_chars)
                if not chunks:
                    return audio_files
                for idx, chunk in enumerate(chunks):
                    with tempfile.NamedTemporaryFile(suffix=f'_{idx}.mp3', delete=False) as temp_audio:
                        audio_path = temp_audio.name
                    try:
                        # Use streaming response API when available to avoid deprecation warning
                        speech_api = getattr(self.client, 'audio').speech
                        try:
                            if hasattr(speech_api, 'with_streaming_response'):
                                with speech_api.with_streaming_response.create(
                                    model="tts-1", voice=voice, input=chunk
                                ) as stream:
                                    # Prefer helper if present
                                    if hasattr(stream, 'stream_to_file'):
                                        stream.stream_to_file(audio_path)
                                    else:
                                        # Iterate events and write any audio bytes found
                                        with open(audio_path, 'wb') as wf:
                                            for evt in stream:
                                                # try common attribute names
                                                data = getattr(evt, 'data', None) or getattr(evt, 'chunk', None)
                                                if isinstance(data, (bytes, bytearray)):
                                                    wf.write(data)
                            else:
                                response = speech_api.create(model="tts-1", voice=voice, input=chunk)
                                if hasattr(response, 'stream_to_file'):
                                    response.stream_to_file(audio_path)
                                else:
                                    # Last resort: try to extract bytes
                                    if isinstance(response, (bytes, bytearray)):
                                        with open(audio_path, 'wb') as wf:
                                            wf.write(response)
                                    else:
                                        raise Exception('No streaming method available on TTS response')
                        except Exception:
                            # If streaming failed for any reason, fallback to gTTS
                            try:
                                tts = gTTS(text=chunk, lang='de', slow=False)
                                tts.save(audio_path)
                            except Exception:
                                raise
                        audio_files.append(audio_path)
                    except Exception as e:
                        # Cleanup any generated files so far
                        for f in audio_files:
                            try:
                                os.unlink(f)
                            except Exception:
                                pass
                        raise
                return audio_files

            # Generate audio files (chunks)
            audio_files = generate_audio_files_for_text(text_content, voice)

            # Play audio files sequentially and respect pause/resume
            total_chars = max(1, len(text_content))
            played_chars = 0
            for audio_file in audio_files:
                if not self.is_reading:
                    break
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                # Wait while this chunk plays (respect pause)
                while (pygame.mixer.music.get_busy() or self.reading_paused) and self.is_reading:
                    if self.reading_paused:
                        time.sleep(0.1)
                        continue
                    # Update progress estimate based on characters
                    # We approximate chunk contribution by file size / char ratio
                    played_chars += max(1, len(text_content) // max(1, len(audio_files)))
                    percent = min(100.0, (played_chars / total_chars) * 100.0)
                    self.safe_ui_update(progress_var, "set", percent)
                    time.sleep(0.1)

            # Cleanup generated chunk files
            for f in audio_files:
                try:
                    os.unlink(f)
                except Exception:
                    pass

            # Update UI when finished
            if self.is_reading:
                self.safe_ui_update(status_label, "config", text="Finished", fg="lightgreen")

        except Exception as e:
            print(f"Error in read_text: {e}")
            self.safe_ui_update(status_label, "config", text=f"Error: {str(e)}", fg="red")
        finally:
            self.is_reading = False
            self.reading_paused = False
            self.safe_ui_update(play_button, "config", state=tk.NORMAL)
            self.safe_ui_update(pause_button, "config", state=tk.DISABLED, text="Pause")

    def safe_ui_update(self, widget, method, *args, **kwargs):
        """Safely update UI elements from threads"""
        try:
            if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                if method == "config":
                    widget.config(**kwargs)
                elif method == "set":
                    widget.set(*args)
        except Exception as e:
            print(f"UI update failed: {e}")

    def safe_cleanup_audio_file(self, audio_file):
        """Safely cleanup audio files"""
        if not audio_file or not os.path.exists(audio_file):
            return
        try:
            os.unlink(audio_file)
        except Exception as e:
            print(f"Cleanup failed for {audio_file}: {e}")

    def toggle_pause(self, pause_button, status_label):
        """Pause or resume reading"""
        if self.is_reading and not self.reading_paused:
            self.reading_paused = True
            pygame.mixer.music.pause()
            pause_button.config(text="Resume")
            status_label.config(text="Paused", fg="yellow")
        elif self.is_reading and self.reading_paused:
            self.reading_paused = False
            pygame.mixer.music.unpause()
            pause_button.config(text="Pause")
            status_label.config(text="Reading...", fg="lightgreen")

    def stop_reading_ui(self, controls_window, play_button, pause_button, status_label, progress_var):
        """Stop reading and clean up UI"""
        self.stop_reading()
        progress_var.set(0)
        status_label.config(text="Stopped", fg="red")
        play_button.config(state=tk.NORMAL)
        pause_button.config(state=tk.DISABLED, text="Pause")
        controls_window.destroy()

    def stop_reading(self):
        """Stop reading completely"""
        self.is_reading = False
        self.reading_paused = False
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    # === SIMPLE LISTEN-ONLY FUNCTIONALITY ===

    def create_listen_functionality(self):
        """Create popup for text-to-speech only (no comprehension questions)"""
        listen_window = tk.Toplevel(self.root)
        listen_window.title("Listen to Text")
        listen_window.configure(bg="#222")
        listen_window.geometry("400x300")
        
        # Voice selection
        tk.Label(listen_window, text="Select Voice:", bg="#222", fg="white").pack(pady=10)
        
        voice_var = tk.StringVar(value="alloy")
        voice_frame = tk.Frame(listen_window, bg="#222")
        voice_frame.pack(pady=10)
        
        for voice in ["alloy", "echo", "fable", "onyx", "nova"]:
            tk.Radiobutton(voice_frame, text=voice.capitalize(), variable=voice_var, 
                         value=voice, bg="#222", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Button functions
        def listen_from_file():
            filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as file:
                        text = file.read()
                    self.speak_text(text, voice_var.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read file: {str(e)}")
        
        def listen_from_study_box():
            text = self.study_textbox.get(1.0, tk.END).strip()
            if text:
                self.speak_text(text, voice_var.get())
            else:
                messagebox.showwarning("No Text", "Study Text Box is empty.")

        def listen_from_clipboard():
            """Read text from clipboard and speak it."""
            text = ""
            try:
                # Try popup window clipboard first
                text = listen_window.clipboard_get()
            except Exception:
                try:
                    # Fallback to root clipboard
                    text = self.root.clipboard_get()
                except Exception:
                    text = ""

            if text and text.strip():
                self.speak_text(text, voice_var.get())
            else:
                messagebox.showwarning("No Text", "Clipboard has no text to read.")
        
        # Buttons
        btn_frame = tk.Frame(listen_window, bg="#222")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Load TXT File", 
              style='SmallBlue.TButton',
              command=listen_from_file).pack(pady=5, fill=tk.X)
        ttk.Button(btn_frame, text="Read from Study Text Box", 
              style='SmallGreen.TButton',
              command=listen_from_study_box).pack(pady=5, fill=tk.X)
        ttk.Button(btn_frame, text="Read from Clipboard",
              style='SmallPurple.TButton',
              command=listen_from_clipboard).pack(pady=5, fill=tk.X)
        ttk.Button(btn_frame, text="Cancel", 
              style='SmallRed.TButton',
              command=listen_window.destroy).pack(pady=5, fill=tk.X)

    def speak_text(self, text, voice="alloy"):
        """Speak text using TTS"""
        try:
            # If text is short, use direct generation. For long text, split into chunks.
            def chunk_text_local(text, max_chars=4000):
                import re
                if not text:
                    return []
                if len(text) <= max_chars:
                    return [text]
                sentences = re.split(r'(?<=[\.\!\?])\s+', text)
                chunks = []
                current = ""
                for s in sentences:
                    if len(current) + len(s) + 1 <= max_chars:
                        current = (current + " " + s).strip()
                    else:
                        if current:
                            chunks.append(current)
                        if len(s) > max_chars:
                            for i in range(0, len(s), max_chars):
                                chunks.append(s[i:i+max_chars])
                            current = ""
                        else:
                            current = s
                if current:
                    chunks.append(current)
                return chunks

            def generate_audio_files_for_text(text, voice, max_chars=4000):
                audio_files = []
                chunks = chunk_text_local(text, max_chars=max_chars)
                if not chunks:
                    return audio_files
                for idx, chunk in enumerate(chunks):
                    with tempfile.NamedTemporaryFile(suffix=f'_{idx}.mp3', delete=False) as temp_audio:
                        audio_path = temp_audio.name
                    try:
                        # Use streaming response API when available to avoid deprecation warning
                        speech_api = getattr(self.client, 'audio').speech
                        try:
                            if hasattr(speech_api, 'with_streaming_response'):
                                with speech_api.with_streaming_response.create(
                                    model="tts-1", voice=voice, input=chunk
                                ) as stream:
                                    if hasattr(stream, 'stream_to_file'):
                                        stream.stream_to_file(audio_path)
                                    else:
                                        with open(audio_path, 'wb') as wf:
                                            for evt in stream:
                                                data = getattr(evt, 'data', None) or getattr(evt, 'chunk', None)
                                                if isinstance(data, (bytes, bytearray)):
                                                    wf.write(data)
                            else:
                                response = speech_api.create(model="tts-1", voice=voice, input=chunk)
                                if hasattr(response, 'stream_to_file'):
                                    response.stream_to_file(audio_path)
                                else:
                                    if isinstance(response, (bytes, bytearray)):
                                        with open(audio_path, 'wb') as wf:
                                            wf.write(response)
                                    else:
                                        raise Exception('No streaming method available on TTS response')
                        except Exception:
                            try:
                                tts = gTTS(text=chunk, lang='de', slow=False)
                                tts.save(audio_path)
                            except Exception:
                                raise
                        audio_files.append(audio_path)
                    except Exception:
                        for f in audio_files:
                            try:
                                os.unlink(f)
                            except Exception:
                                pass
                        raise
                return audio_files

            # Generate and play in a background thread so UI isn't blocked
            def generate_and_play():
                try:
                    files = generate_audio_files_for_text(text, voice)
                    for f in files:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()
                        pygame.mixer.music.load(f)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                    # cleanup
                    for f in files:
                        try:
                            os.unlink(f)
                        except Exception:
                            pass
                except Exception as e:
                    try:
                        messagebox.showerror("TTS Error", f"Failed to generate speech: {str(e)}")
                    except Exception:
                        print(f"TTS Error: {e}")

            threading.Thread(target=generate_and_play, daemon=True).start()

        except Exception as e:
            messagebox.showerror("TTS Error", f"Failed to generate speech: {str(e)}")

    def wait_and_cleanup(self, audio_file):
        """Wait for playback to finish and cleanup"""
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        self.safe_cleanup_audio_file(audio_file)

    # === SEARCH FUNCTIONALITY ===

    def search_german_text(self, parent_window, voice):
        """Search for German text online"""
        try:
            sources = [
                "https://www.dw.com/de/themen/s-9077",
                "https://www.tagesschau.de/",
            ]
            
            source = random.choice(sources)
            response = requests.get(source, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            paragraphs = soup.find_all('p')
            german_text = ""
            
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 50:
                    german_text += text + " "
                    if len(german_text.split()) > 150:
                        break
            
            if not german_text:
                german_text = self.generate_german_text_with_ai()
            
            self.listening_comprehension_text = german_text[:2000]
            self.current_voice = voice
            parent_window.destroy()
            self.start_listening_comprehension_flow()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch German text: {e}")

    def generate_german_text_with_ai(self):
        """Generate German text using AI fallback"""
        themes = [
            "Umwelt und Naturschutz in Deutschland",
            "Alltagsleben in einer deutschen Stadt",
        ]
        
        theme = random.choice(themes)
        prompt = f"Schreibe einen deutschen Text von 100 Wörtern zum Thema: {theme}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except:
            return "Dies ist ein Beispieltext für das Hörverständnis. Er enthält verschiedene Aspekte der deutschen Sprache und Kultur."

    # === UTILITY METHODS ===

    def ensure_prompt_ai_enabled(self):
        """Ensure Prompt AI button is enabled"""
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state=tk.NORMAL)

    # === UI CREATION METHODS ===

    def create_left_section(self):
        """Create the left section of the UI"""
        left_frame = tk.Frame(self.root, bg="#222")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create textboxes
        self.vocabulary_textbox = self.create_labeled_textbox(left_frame, "Vocabulary (Current):", True, height=9, label_font=self.left_section_font, add_buttons=False)
        self.study_textbox = self.create_labeled_textbox(left_frame, "Study Text Box:", True, height=10, label_font=self.left_section_font, add_buttons=True)
        tk.Label(left_frame, text="Double-click on a German noun in the Study Textbox to see it declined.", fg="cyan", bg="#222").pack(anchor='w')
        self.study_textbox.bind('<Double-Button-1>', self.on_study_text_double_click)
        self.translation_textbox = self.create_labeled_textbox(left_frame, "Translation Box:", True, height=9, label_font=self.left_section_font, add_buttons=True)
        self.input_textbox = self.create_labeled_textbox(left_frame, "Prompt the AI by writing below", True, height=5, label_font=self.left_section_font, add_buttons=False)

        # Add the AI prompt buttons
        self.prompt_ai_button = ttk.Button(
            left_frame,
            text="Prompt AI",
            style='SmallPurple.TButton',
            command=self.prompt_inputbox
        )
        self.prompt_ai_button.pack(side='left', padx=(10, 3), pady=3)

        self.eval_answer_btn = ttk.Button(
            left_frame,
            text="Eval.Answer",
            style='SmallGoldYellow.TButton',
            command=self.handle_evaluation,  # unified handler for reading/listening
            state="disabled"
        )
        self.eval_answer_btn.pack(side='left', padx=(10, 3), pady=3)

        ttk.Button(
            left_frame,
            text="Clear Prompt",
            style='SmallRed.TButton',
            command=self.clear_input_textbox
        ).pack(side='left', padx=3, pady=3)

        ttk.Button(
            left_frame,
            text="Create sentences from current _VOC file or select other _VOC.txt",
            style='SmallPurple.TButton',
            command=lambda: self.en_to_de_translation()
        ).pack(side='left', padx=3, pady=3)

    def create_middle_section(self):
        """Create the middle section with control buttons"""
        middle_frame = tk.Frame(self.root, bg="#222")
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=12)
        
        # Group 1: Vocabulary Buttons
        vocab_btn_frame = tk.Frame(middle_frame, bg="#222")
        vocab_btn_frame.pack(pady=(0, 10))

        ttk.Button(vocab_btn_frame, text="LOAD-VOC", style='SmallBlue.TButton', command=self.load_vocabulary).pack(pady=2)
        ai_create_voc_btn = ttk.Button(vocab_btn_frame, text="AI-create VOC", style='SmallDarkPurple.TButton', command=lambda: self.create_vocabulary())
        ai_create_voc_btn.pack(pady=2)
        Tooltip(ai_create_voc_btn, "Click to let AI create a vocabulary from a -VOC file, then use buttons 'Beautify' and 'Fix Verbs' if necesssary.")
        ttk.Button(vocab_btn_frame, text="SAVE-VOC", style='SmallGreen.TButton', command=self.save_vocabulary).pack(pady=2)
        beautify_btn = ttk.Button(vocab_btn_frame, text="Beautify", style='SmallGoldBrown.TButton', command=self.beautify_vocabulary)
        beautify_btn.pack(pady=2)
        Tooltip(beautify_btn, "Click to remove preceding numbers, if any, and duplicate entries.")
        fix_verbs_btn = ttk.Button(vocab_btn_frame, text="Fix Verbs", style='SmallOliveGreen.TButton', command=self.fix_verbs)
        fix_verbs_btn.pack(pady=2)
        Tooltip(fix_verbs_btn, "Find all verbs and format them as: infinitive, Präteritum, Partizip II. Append them at the end of the vocabulary.")
        ttk.Button(vocab_btn_frame, text="CLR-VOC", style='SmallRed.TButton', command=self.clear_vocabulary).pack(pady=2)
        search_vocab_btn = ttk.Button(vocab_btn_frame, text="🔍 Search Vocab.", style='SmallBlue.TButton',
                command=self.show_vocabulary_search)
        search_vocab_btn.pack(side=tk.RIGHT, padx=(0, 5))
        Tooltip(search_vocab_btn, "Load a vocabulary file (_VOC.txt) to search its contents.")
        
        # Group 2: Study Text Buttons
        study_btn_frame = tk.Frame(middle_frame, bg="#222")
        study_btn_frame.pack(pady=(2, 2)) # debug (15 replaced by 5)

        ttk.Button(study_btn_frame, text="LOAD-TXT", style='SmallBlue.TButton', command=self.load_study_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="SAVE-TXT", style='SmallGreen.TButton', command=self.save_study_text).pack(pady=2)
        copy_txt_btn = ttk.Button(study_btn_frame, text="COPY-TXT", style='SmallBrownish.TButton', command=self.copy_study_text)
        copy_txt_btn.pack(pady=2)
        Tooltip(copy_txt_btn, "Click to copy the entire text.")
        ttk.Button(study_btn_frame, text="CLR-TXT", style='SmallRed.TButton', command=self.clear_study_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="Translate file", style='SmallDarkPurple.TButton', command=lambda: self.translate_study_text()).pack(pady=2)
        free_hand_trans_btn = ttk.Button(study_btn_frame, text="Free-Hand\nTranslation", style='SmallLightPurple.TButton', command=self.capture_text)
        free_hand_trans_btn.pack(pady=2)
        Tooltip(free_hand_trans_btn, "First load German text in the Study Text Box, then click button to translate into English.")
        ttk.Button(study_btn_frame, text="  LISTEN to\nthe Study Text", style='SmallBlue.TButton', command=self.create_listen_functionality).pack(pady=2)

        # Group 3: Translation Buttons
        translation_btn_frame = tk.Frame(middle_frame, bg="#222")
        translation_btn_frame.pack(pady=(25, 0))

        ttk.Button(translation_btn_frame, text="LOAD-TRA", style='SmallBlue.TButton', command=self.load_translation).pack(pady=2)
        ttk.Button(translation_btn_frame, text="SAVE-TRA", style='SmallGreen.TButton', command=self.save_translation).pack(pady=2)
        ttk.Button(translation_btn_frame, text="CLR-TRA", style='SmallRed.TButton', command=self.clear_translation).pack(pady=2)
        ttk.Button(translation_btn_frame, text="NOTES", style='SmallGoldBrown.TButton', command=self.add_notes).pack(pady=2)
        
        # Group 4: AI Response Buttons
        ai_responses_middle_btn_frame = tk.Frame(middle_frame, bg="#222")
        ai_responses_middle_btn_frame.pack(pady=(40, 0))

        ttk.Button(ai_responses_middle_btn_frame, text="Save AI\nResponses", style='SmallDarkPurple.TButton', command=self.save_ai_responses).pack(pady=2)
        ttk.Button(ai_responses_middle_btn_frame, text="Append AI\nResponses", style='SmallDarkPurple.TButton', command=self.append_ai_responses_to_file).pack(pady=2)
        ttk.Button(ai_responses_middle_btn_frame, text="Copy AI \nResponses", style='SmallDarkPurple.TButton', command=self.copy_ai_responses).pack(pady=2)
        ttk.Button(ai_responses_middle_btn_frame, text="Clear AI\nResponses", style='SmallRed.TButton', command=self.clear_ai_responses_textbox).pack(pady=2)

    def create_right_section(self):
        """Create the right section of the UI"""
        right_frame = tk.Frame(self.root, bg="#222")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5)

        # Example Sentences
        self.example_sentences_textbox = self.create_labeled_textbox(right_frame, "Find example sentences using the AI or the Glosbe dictionary, also Load and Append examples", True, height=6)

        # New Input Box for Glosbe Search
        self.glosbe_search_entry = tk.Entry(right_frame, bg="black", fg="white", insertbackground="white", font=("Helvetica", 11))
        self.glosbe_search_entry.pack(fill=tk.X, padx=10, pady=5)

        # Buttons for Example Sentences
        btn_frame = tk.Frame(right_frame, bg="#222")
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="AI Examples", style='SmallDarkPurple.TButton', command=self.fetch_ai_examples).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Glosbe Examples", style='SmallOliveGreen.TButton', command=self.fetch_glosbe_examples).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Examples", style='SmallBlue.TButton', command=self.load_examples).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Append", style='SmallGreen.TButton', command=self.save_examples).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Input", style='SmallOrange.TButton', command=self.clear_examples_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", style='SmallRed.TButton', command=self.clear_example_sentences).pack(side=tk.LEFT, padx=5)

        # Vocabulary Test Section
        test_frame = tk.Frame(right_frame, bg="#222")
        test_frame.pack(fill=tk.X, pady=10)
        tk.Label(test_frame, text="Take a test of the Vocabulary (Current) or choose other '_VOC.txt' file:", fg="gold", bg="#222").pack(anchor='w')

        btn_frame2 = tk.Frame(test_frame, bg="#222")
        btn_frame2.pack(fill=tk.X)
        ttk.Button(btn_frame2, text="Choose '_VOC.txt' File", style='SmallBlue.TButton', command=self.load_test_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Flip Words", style='SmallGoldBrown.TButton', command=self.toggle_flip_mode).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Clear Test", style='SmallOrange.TButton', command=self.clear_test).pack(side=tk.LEFT, padx=5)

        self.test_filename_label = tk.Label(test_frame, text="File is:", fg="white", bg="#222")
        self.test_filename_label.pack(anchor='w')

        self.test_textbox = scrolledtext.ScrolledText(test_frame, height=6, wrap=tk.WORD, bg="#333", fg="white", font=("Helvetica", 11))
        self.test_textbox.pack(fill=tk.X)

        # Answer Input
        tk.Label(right_frame, text="Type your answer below and then press the ENTER key. 'to' is added before the English verbs", fg="gold", bg="#222").pack(anchor='w')
        tk.Label(right_frame, text="For the 'Next Word' hold down SHIFT and press the ENTER key", fg="cyan", bg="#222").pack(anchor='w')
        self.answer_entry = tk.Entry(right_frame, bg="black", fg="white", insertbackground="white", font=("Helvetica", 11))
        self.answer_entry.pack(fill=tk.X)
        self.answer_entry.bind("<Return>", self.check_answer)
        self.answer_entry.bind("<Shift-Return>", self.trigger_next_word_and_refocus)

        answer_frame = tk.Frame(right_frame, bg="#222")
        answer_frame.pack(fill=tk.X)
        ttk.Button(answer_frame, text="Next Word", style='SmallBlue.TButton', command=self.next_word).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(answer_frame, text="Clear Input", style='SmallOrange.TButton', command=self.clear_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(answer_frame, text="Revise Mistakes", style='SmallGreenish.TButton', command=self.load_revision_file).pack(side=tk.LEFT, padx=5)
        tk.Label(answer_frame, text="Score:", fg="white", bg="#222").pack(side=tk.LEFT, padx=5)
        self.score_label = tk.Label(answer_frame, text="0%", fg="white", bg="#222")
        self.score_label.pack(side=tk.LEFT)
        tk.Label(answer_frame, text="Test Question Number", fg="white", bg="#222").pack(side=tk.LEFT, padx=5)
        self.count_test_num_label = tk.Label(answer_frame, text="0", fg="white", bg="#222")
        self.count_test_num_label.pack(side=tk.LEFT)

        # Dictionary Search
        tk.Label(right_frame, text="Search word using AI or Langenscheid online dictionary", fg="gold", bg="#222").pack(anchor='w', pady=5)
        self.dictionary_entry = tk.Entry(right_frame, bg="black", fg="white", insertbackground="white", font=("Helvetica", 11))
        self.dictionary_entry.pack(fill=tk.X)
        self.dictionary_entry.bind("<Return>", self.search_own_vocab)

        dict_btn_frame = tk.Frame(right_frame, bg="#222")
        dict_btn_frame.pack(fill=tk.X)
        ttk.Button(dict_btn_frame, text="AI word translation", style='SmallDarkPurple.TButton', command=self.ai_translate_word).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(dict_btn_frame, text="Langenscheidt", style='SmallGrayBlue.TButton', command=self.fetch_langenscheidt).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(dict_btn_frame, text="Search vocabulary (Current).", style='SmallDarkOlive.TButton', command=self.search_own_vocab).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(dict_btn_frame, text="Clear Input", style='SmallOrange.TButton', command=self.clear_entry).pack(side=tk.LEFT, padx=5)

        # AI Responses to prompts
        self.ai_responses_textbox = self.create_labeled_textbox(right_frame, "AI Responses from prompt on the left side", True, height=11, label_font="Helvetica")

    def create_labeled_textbox(self, parent, label_text, scrollbar=True, height=10, label_font="Helvetica", add_buttons=False):
        """Create a labeled textbox with optional scrollbar and highlight buttons"""
        frame = tk.Frame(parent, bg="#222")
        frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        label = tk.Label(frame, text=label_text, bg="#222", fg="gold", font=label_font)
        # Keep a reference to the vocabulary label so we can update it with the file path
        try:
            if isinstance(label_text, str) and label_text.strip().startswith("Vocabulary (Current)"):
                self.vocabulary_label = label
        except Exception:
            pass
        label.pack(anchor="w")
        
        if scrollbar:
            textbox = scrolledtext.ScrolledText(frame, height=height, bg="#333", fg="white", 
                                            insertbackground="white", font=label_font, wrap="word")
        else:
            textbox = tk.Text(frame, height=height, bg="#333", fg="white", 
                            insertbackground="white", font=label_font, wrap="word")
        
        textbox.pack(fill=tk.X, pady=(5, 0))
        
        # Configure highlight tag
        textbox.tag_configure("highlight", background="yellow", foreground="black")
        
        # Add buttons if requested
        if add_buttons:
            button_frame = tk.Frame(frame, bg="#222")
            button_frame.pack(fill=tk.X, pady=(0, 5))
            
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

            # ttk.Button(
            #     button_frame,
            #     text="🔍 Search Text",
            #     style='SmallGoldenSummer.TButton',
            #     command=self.search_text
            # ).pack(side='left', padx=3, pady=3)
            
            # Add the "READING Comprehension" button only for Study Text Box
            if label_text == "Study Text Box:":
                ttk.Button(
                    button_frame,
                    text="READING Comprehension",
                    style='SmallPurple.TButton',
                    command=self.generate_comprehension_questions
                ).pack(side='left', padx=(15, 3), pady=3)
            
            
            if label_text == "Study Text Box:":
                ttk.Button(
                    button_frame,
                    text="LISTENING Comprehension",
                    style='SmallGoldYellow.TButton',
                    command=self.create_listening_comprehension
                ).pack(side='left', padx=(15, 3), pady=3)

            # Add Listen-to-Translation button for the Translation Box
            if label_text == "Translation Box:":
                ttk.Button(
                    button_frame,
                    text="LISTEN to the translation",
                    style='SmallBlue.TButton',
                    command=self.create_translation_listen_popup
                ).pack(side='left', padx=(10, 3), pady=3)
        
        return textbox

    def update_vocabulary_label_path(self):
        """Update the Vocabulary label to include the current vocabulary file path (relative to Desktop)."""
        if not hasattr(self, 'vocabulary_label'):
            return

        if self.current_voc_file:
            try:
                home = os.path.expanduser("~")
                rel = os.path.relpath(self.current_voc_file, home)
                # Normalize separators and ensure it starts with a backslash as requested
                rel = rel.replace('/', '\\')
                display = "\\" + rel
            except Exception:
                display = self.current_voc_file
            new_text = f"Vocabulary (Current): {display}"
        else:
            new_text = "Vocabulary (Current):"

        try:
            self.vocabulary_label.config(text=new_text)
        except Exception:
            pass

    # === TEXT HIGHLIGHTING FUNCTIONALITY ===

    def add_highlight_functionality(self):
        """Add highlight functionality to textboxes"""
        self.root.bind('<Control-h>', self.highlight_selection)
        self.root.bind('<Control-Shift-H>', self.clear_highlight)

    def highlight_text(self, textbox):
        """Highlight selected text in the given textbox"""
        try:
            textbox.tag_remove("highlight", "1.0", tk.END)
            if textbox.tag_ranges(tk.SEL):
                start = textbox.index(tk.SEL_FIRST)
                end = textbox.index(tk.SEL_LAST)
                textbox.tag_add("highlight", start, end)
        except tk.TclError:
            pass

    def clear_text_highlight(self, textbox):
        """Clear highlight from the given textbox"""
        textbox.tag_remove("highlight", "1.0", tk.END)

    # def search_text(self): # debug -- I may have to remove this and the related button
    #     """Placeholder for search text functionality"""
    #     pass

    def highlight_selection(self, event=None):
        """Highlight selected text (keyboard shortcut)"""
        focused_widget = self.root.focus_get()
        if focused_widget in [self.vocabulary_textbox, self.study_textbox, self.translation_textbox]:
            self.highlight_text(focused_widget)
        return "break"

    def clear_highlight(self, event=None):
        """Clear highlight (keyboard shortcut)"""
        focused_widget = self.root.focus_get()
        if focused_widget in [self.vocabulary_textbox, self.study_textbox, self.translation_textbox]:
            self.clear_text_highlight(focused_widget)
        return "break"

    # === NOUN LOOK-UP FUNCTIONALITY ===

    def on_study_text_double_click(self, event):
        """Handle double-click on study text to lookup German nouns"""
        try:
            index = self.study_textbox.index(f"@{event.x},{event.y}")
            word_start = self.study_textbox.index(f"{index} wordstart")
            word_end = self.study_textbox.index(f"{index} wordend")
            word = self.study_textbox.get(word_start, word_end).strip()
            
            if word and word[0].isupper() and word.isalpha():
                self.lookup_german_noun(word)
        except Exception as e:
            print(f"Double-click error: {e}")

    def lookup_german_noun(self, noun):
        """Look up German noun declension using OpenAI API"""
        prompt = f"""
        For the word "{noun}" as used in the German language, provide the following information in this exact format:
        
        Article: [definite article - der, die, or das]
        Plural: [plural form]

        Declension Singular:
        Nominative: [article + noun]
        Genitive: [article + noun]  
        Dative: [article + noun]
        Accusative: [article + noun]

        Declension Plural:
        Nominative: [article + plural form]
        Genitive: [article + plural form]  
        Dative: [article + plural form]
        Accusative: [article + plural form]
        
        If "{noun}" is not commonly used as a noun in German, respond with: "Not a German noun"
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a German grammar expert. Provide concise, accurate noun information."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            noun_info = response.choices[0].message.content.strip()
            
            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title(f"Noun: {noun}")
            popup.configure(bg="#222")
            popup.geometry("350x250")
            
            # Center the window
            popup.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
            y = (self.root.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            
            # Display noun information
            text_widget = tk.Text(popup, bg="#333", fg="white", wrap=tk.WORD, font=("Arial", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, f"Noun: {noun}\n\n{noun_info}")
            text_widget.config(state=tk.DISABLED)
            
            ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("API Error", f"Failed to lookup noun: {str(e)}")

    # === CORE APPLICATION METHODS ===

    def prompt_inputbox(self):
        """Send user input to ChatGPT and display responses"""
        # Refuse to send prompts while a comprehension session is active
        if getattr(self, 'reading_comprehension_active', False) or getattr(self, 'current_questions', None):
            try:
                messagebox.showwarning("Busy", "A comprehension session is active. Use 'Eval.Answer' to evaluate answers.")
            except Exception:
                pass
            return

        content = self.input_textbox.get(1.0, tk.END).strip()
        if not content:
            return

        self.conversation_history.append({"role": "user", "content": content})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                temperature=0.7,
            )
            answer = response.choices[0].message.content.strip()

            self.conversation_history.append({"role": "assistant", "content": answer})
            self.ai_responses_textbox.insert(tk.END, f"You: {content} \n\n AI: {answer}\n\n")

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Chat Error", f"An error occurred: {e}")

    def clear_input_textbox(self):
        """Clear the input textbox"""
        self.input_textbox.delete(1.0, tk.END)

    def create_vocabulary(self):
        """AI creates vocabulary from txt file.

        Warn only if the `Vocabulary (Current)` textbox contains content. If it does,
        ask the user whether to save the existing vocabulary, overwrite it, or cancel.
        """
        self.check_vocabulary_and_warn(self._create_vocabulary_impl)

    def check_vocabulary_and_warn(self, operation_callback, *args):
        """Prompt the user only if the Vocabulary textbox already contains text.

        Yes = save current vocabulary (calls `save_vocabulary`) then continue
        No  = continue and overwrite without saving
        Cancel = abort
        """
        try:
            vocab_content = self.vocabulary_textbox.get(1.0, tk.END).strip()
        except Exception:
            vocab_content = ''

        if vocab_content:
            prompt = "Vocabulary textbox contains text. Save current vocabulary before creating a new one?"
            choice = messagebox.askyesnocancel("Vocabulary Not Empty", prompt, parent=self.root)
            if choice is None:
                return False
            elif choice:
                try:
                    self.save_vocabulary()
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save vocabulary: {e}", parent=self.root)

        operation_callback(*args)
        return True

    def _create_vocabulary_impl(self):
        """Actual implementation of create_vocabulary"""
        filename = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()

            configure_openai()

            prompt = """You are a German-English linguistic analysis tool. Your task is to process a German text, filter it based on a custom stopword list, and then generate a formatted vocabulary list with specific grammatical information and English translations.

            Objective:
            Analyze the provided German text file to create a unique vocabulary list. The order of the words in the final output must match the order in which the first instance of each word appeared in the source text. Each entry in the list must be formatted according to its part of speech (noun, verb, adjective, or other) and translated into English.

            Processing Workflow:

            Tokenize and Normalize: Read the entire text. Break it down into individual words (tokens). Treat all punctuation (e.g., , . ! ? ; : " ') as delimiters and remove it from the words.

            Filter Stopwords: Create a list of all words from the text, maintaining their original order of appearance. From this list, remove any word that appears in the stopword list below. Then, create a final unique list, keeping only the first occurrence of each word.

            Stopword List: der, die, das, Montag, Dienstag, Mittwoch, Donnerstag, Freitag, Samstag, Sonntag, Januar, Februar, März, April, Mai, Juni, Juli, August, September, Oktober, November, Dezember, ich, du, er, sie, es, wir, ihr, Sie, in, an, auf, unter, über, vor, hinter, neben, zwischen, mit, nach, bei, seit, von, zu, für, durch, um, und, aber, gegen, ohne, am, zur, Man, Frau, Kind, mich, dich, sich, uns, euch, ihnen, nicht, ja, nun, ob, ist, sein, war, waren, haben, hat, gehabt, wurde, wurden, wird, Frühling, Sommer, Herbst, Winter

            Lemmatize and Analyze: For each unique word in the ordered list, determine its base form (lemma) and its part of speech (noun, verb, adjective, adverb, etc.).

            Format and Translate: Generate the final output list. Follow the output formatting rules below precisely.

            Output Formatting Rules:

            General:

            DO NOT precede any entry with markup, numbers, bullets, hyphens, or any other characters. Each entry begins with the German word itself.

            Each entry must be on a new line.

            Provide a maximum of THREE English translations for each word.

            Do not sort the final list. The order of words must correspond to the order in which their first instance appeared in the original text.

            For Nouns:

            From any form of a noun found in the text (e.g., "Buches"), identify its SINGULAR, NOMINATIVE form.

            Format: SINGULAR Form, Article, [Plural Form, Plural Article] = translation1, translation2, translation3

            Example: Buch, das, [Bücher, die] = book, volume, ledger

            ================================================
            *** VERBS — VERY IMPORTANT ***
            ================================================

            From ANY finite or non-finite form of a verb found in the text (e.g., "spricht", "sprach", "gesprochen", "ging", "gegangen", "sprachts"), you MUST:

            1) Identify the INFINITIVE (base form).
            2) Identify:
            - the Präteritum (simple past, 1st/3rd person singular form),
            - the Partizip II (past participle, without auxiliary).

            3) Output the verb ALWAYS in this EXACT format:

            Infinitive, [Präteritum, Perfekt-Partizip] = to translation1, to translation2, to translation3

            CRITICAL VERB RULES (MUST FOLLOW):

            - The part inside the square brackets MUST contain exactly TWO German forms:
            1. First: Präteritum (1st/3rd person singular),
            2. Second: Partizip II (past participle only, WITHOUT "hat"/"ist").

            - Do NOT include any auxiliary verbs in the brackets:
            - WRONG: sprechen, [sprach, hat gesprochen]
            - CORRECT: sprechen, [sprach, gesprochen]

            - Always start each English translation with "to".
            - Example: to speak, to talk
            - If there is only one natural translation, you may give just one.
            - Maximum three translations.

            - If you are uncertain, still give your best guess for [Präteritum, Partizip II] but ALWAYS keep the same format.

            Examples (PAY CLOSE ATTENTION):

            - Encounter: "spricht", "sprach", "gesprochen", or "sprachts"
            Output: sprechen, [sprach, gesprochen] = to speak, to talk

            - Encounter: "ging", "geht", "gegangen"
            Output: gehen, [ging, gegangen] = to go, to walk

            - Encounter: "nahm", "nimmt", "genommen"
            Output: nehmen, [nahm, genommen] = to take

            - Encounter: "arbeitete", "arbeitet", "gearbeitet"
            Output: arbeiten, [arbeitete, gearbeitet] = to work

            - Modal verb:
            Encounter: "kann", "konnte", "gekonnt"
            Output: können, [konnte, gekonnt] = to be able, to can

            - Separable verb:
            Encounter: "stand auf", "aufgestanden", "steht auf"
            Output: aufstehen, [stand auf, aufgestanden] = to get up, to stand up

            - Prefix verb:
            Encounter: "verstand", "verstanden"
            Output: verstehen, [verstand, verstanden] = to understand

            Do NOT add extra grammatical information to verb lines.
            Do NOT add aspect, voice labels, or auxiliary forms.
            ONLY use: Infinitive, [Präteritum, Partizip II] = to ..., to ..., to ...

            For Adjectives:

            From any form of an adjective, identify its positive (base) form.

            Format: Positive Form, [Comparative Form, Superlative Form] = translation1, translation2, translation3

            Example: schnell, [schneller, schnellsten] = fast, quick, rapid

            For Adverbs and All Other Word Types:

            Display the word in its base/dictionary form.

            Format: German Word = translation1, translation2, translation3

            Example: oft = often, frequently."""

            response = client.chat.completions.create(model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for language study."},
                {"role": "user", "content": f"{prompt}\n\n{content}"}
            ],
            temperature=0.3)
            auto_vocabulary = response.choices[0].message.content

            self.vocabulary_textbox.delete(1.0, tk.END)
            self.vocabulary_textbox.insert(tk.END, auto_vocabulary)

        except FileNotFoundError:
            self.vocabulary_textbox.delete(1.0, tk.END)
            self.vocabulary_textbox.insert(tk.END, "Error: File not found.")
        except Exception as e:
            self.vocabulary_textbox.delete(1.0, tk.END)
            self.vocabulary_textbox.insert(tk.END, f"An error occurred: {e}")

    # === FILE OPERATION METHODS ===

    def load_vocabulary(self):
        """Load vocabulary file with related files"""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

        if filename.endswith("_VOC.txt") or "_VOC.txt" in filename:
            self.current_voc_file = filename
            # Update the UI label to show the loaded file path (relative to Desktop)
            try:
                self.update_vocabulary_label_path()
            except Exception:
                pass
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                self.vocabulary_textbox.delete(1.0, tk.END)
                self.vocabulary_textbox.insert(tk.END, content)
                self.vocabulary = [line.strip() for line in content.splitlines() if line.strip()]
                self.load_current_voc += 1
                self.load_test_file()
            
            # Ask user if they want to load related files
            response = messagebox.askyesno(
                "Load Related Files", 
                "Do you want to also load the corresponding Study Text and Translation files?"
            )
            
            if response:
                base_name = filename.replace("_VOC.txt", "")
                study_text_file = base_name + "_TXT.txt"
                translation_file = base_name + "_TRA.txt"
                
                # Load Study Text file if it exists
                if os.path.exists(study_text_file):
                    try:
                        with open(study_text_file, 'r', encoding='utf-8-sig') as file:
                            content = file.read()
                            self.current_study_file = study_text_file
                            title = self.extract_title_from_text(content)
                            self.update_study_text_label(title)
                            cleaned_content = self.remove_title_line(content)
                            self.study_textbox.delete(1.0, tk.END)
                            self.study_textbox.insert(tk.END, cleaned_content)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to load study text: {str(e)}")
                
                # Load Translation file if it exists
                if os.path.exists(translation_file):
                    try:
                        with open(translation_file, 'r', encoding='utf-8-sig') as file:
                            content = file.read()
                            self.current_translation_file = translation_file
                            title = self.extract_title_from_text(content)
                            self.update_translation_label(title)
                            cleaned_content = self.remove_title_line(content)
                            self.translation_textbox.delete(1.0, tk.END)
                            self.translation_textbox.insert(tk.END, cleaned_content)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to load translation: {str(e)}")
        
        else:
            messagebox.showwarning(
                "Invalid File Type",
                "The selected file is not a vocabulary file.\n\nPlease select a file that ends with '_VOC.txt'."
            )

    def save_vocabulary(self):
        """Save vocabulary to file"""
        filename = None  # Initialize filename to None
        
        if not self.current_voc_file:
            # First save - ask for filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if not filename:  # User cancelled
                return

            nwext = os.path.splitext(filename)[0]
            if '_VOC' not in filename:
                filename = nwext + '_VOC.txt'
            self.current_voc_file = filename
        else:
            # Subsequent saves - ask whether to overwrite or create new
            choice = messagebox.askyesnocancel(
                "Save Options",
                f"Overwrite existing file?\n{self.current_voc_file}\n\n"
                "Yes = Overwrite\nNo = Save as new file\nCancel = Abort")

            if choice is None:  # User cancelled
                return
            elif choice:  # Overwrite
                filename = self.current_voc_file
            else:  # Save as new file
                filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt")]
                )
                if filename:
                    nwext = os.path.splitext(filename)[0]
                    if '_VOC' not in filename:
                        filename = nwext + '_VOC.txt'
                    self.current_voc_file = filename
                else:
                    return  # User cancelled

        # Update label if we have a current filename set
        try:
            self.update_vocabulary_label_path()
        except Exception:
            pass

        if filename:  # Now filename is guaranteed to be defined
            with open(filename, 'w', encoding='utf-8-sig') as file:
                content = self.vocabulary_textbox.get(1.0, tk.END)
                file.write(content)
            messagebox.showinfo("Success", f"File saved successfully at:\n{filename}")

    # === VOCABULARY TESTING METHODS ===

    def load_test_file(self):
        """Load test file for vocabulary testing"""
        if self.load_current_voc > 0:
            filename = self.current_voc_file
        else:
            self.count_test_num = 0
            filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.test_filename_label.config(text=f"File is: {filename}")
            with open(filename, 'r', encoding='utf-8-sig') as file:
                self.vocabulary = [line.strip() for line in file.readlines() if line.strip()]
            self.display_random_word()
            self.load_current_voc = 0

    def display_random_word(self):
        """Display a random word for testing"""
        if not self.vocabulary:
            self.test_textbox.delete(1.0, tk.END)
            self.test_textbox.insert(tk.END, "No vocabulary loaded. Click again!\n")
            return

        self.current_word = random.choice(self.vocabulary)
        self.glosbe_search_entry.delete(0, tk.END)
        self.test_textbox.delete(1.0, tk.END)
        self.test_textbox.insert(tk.END, "Please translate the following:\n")

        self.count_test_num += 1
        self.count_test_num_label.config(text=f"{self.count_test_num}")

        try:
            parts = self.current_word.split('=')
            german_part = parts[0].strip()
            english_part = parts[1].strip()
        except IndexError:
            self.test_textbox.insert(tk.END, "⚠️ Malformed vocabulary line.\n")
            return

        if self.flip_mode:
            self.test_textbox.insert(tk.END, f"--> {english_part}\n")
        else:
            self.test_textbox.insert(tk.END, f"--> {german_part}\n")
            self.glosbe_search_entry.insert(tk.END, f"{german_part}\n")

        self.answer_entry.delete(0, tk.END)

        if not self.flip_mode:
            english_entries = [e.strip().lower() for e in english_part.split(',')]
            if any(entry.startswith("to ") for entry in english_entries):
                self.answer_entry.delete(0, tk.END)
                self.answer_entry.insert(0, "to ")
                self.answer_entry.update_idletasks()

    def toggle_flip_mode(self):
        """Toggle between German->English and English->German testing"""
        self.flip_mode = not self.flip_mode
        self.count_test_num = 0
        self.display_random_word()

    def next_word(self):
        """Display next word"""
        self.display_random_word()

    def clear_input(self):
        """Clear answer input"""
        self.answer_entry.delete(0, tk.END)

    def check_answer(self, event=None):
        """Check user's answer"""
        user_input_raw = self.answer_entry.get().strip()
        user_answer = user_input_raw.lower()

        if user_answer.startswith("to "):
            user_answer = user_answer[3:].strip()

        if self.flip_mode:
            correct_answers_raw = self.current_word.split(' = ')[0].split(', ')
        else:
            correct_answers_raw = self.current_word.split(' = ')[1].split(', ')

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
            self.save_failed_word()

        if self.total_questions > 0:
            self.score = round((self.correct_answers / self.total_questions) * 100)
            self.score_label.config(text=f"{self.score}%")

        self.clear_input()

    def save_failed_word(self):
        """Save failed word to revision file"""
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
        """Load revision file for mistake review"""
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

    # === READING COMPREHENSION ===

    def generate_comprehension_questions(self):
        """Generate comprehension questions based on study text"""
        study_text = self.study_textbox.get(1.0, tk.END).strip()
        
        if not study_text:
            messagebox.showwarning("No Text", "Please load some text into the Study Text Box first.")
            return
        
        prompt = f"""
        Based on the following German text, create 2-5 comprehension questions in German. 
        The questions should test understanding of the text and should be appropriate for a German language learner.
        
        Text:
        {study_text}
        
        Please provide only the questions, numbered, without any additional text or explanations.
        """
        
        self.conversation_history.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                temperature=0.7,
            )
            
            questions = response.choices[0].message.content.strip()
            # Parse and start a reading comprehension session
            self.parse_reading_questions(questions)
            self.start_reading_comprehension_session()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # === HELPER METHODS ===

    def extract_title_from_text(self, text_content):
        """Extract title from first line if it starts with 'Title:' or 'URL:'"""
        lines = text_content.split('\n')
        if lines and (lines[0].startswith('Title:') or lines[0].startswith('URL:')):
            return lines[0].split(':', 1)[1].strip()
        return 'Title?'

    def remove_title_line(self, text_content):
        """Remove the first line if it contains Title: or URL:"""
        lines = text_content.split('\n')
        if lines and (lines[0].startswith('Title:') or lines[0].startswith('URL:')):
            return '\n'.join(lines[1:])
        return text_content

    def update_study_text_label(self, title):
        """Find and update the study text box label"""
        def search_widgets(widget):
            if isinstance(widget, tk.Label) and "Study Text Box" in widget.cget('text'):
                widget.config(text=f"Study Text Box: {title}")
                return True
            for child in widget.winfo_children():
                if search_widgets(child):
                    return True
            return False
        search_widgets(self.root)

    def update_translation_label(self, title):
        """Find and update the translation box label"""
        def search_widgets(widget):
            if isinstance(widget, tk.Label) and "Translation Box" in widget.cget('text'):
                widget.config(text=f"Translation Box: {title}")
                return True
            for child in widget.winfo_children():
                if search_widgets(child):
                    return True
            return False
        search_widgets(self.root)

    def check_content_and_warn(self, operation_callback, *args):
        """Check if study or translation boxes have content and warn user"""
        study_content = self.study_textbox.get(1.0, tk.END).strip()
        translation_content = self.translation_textbox.get(1.0, tk.END).strip()
        
        has_content = bool(study_content or translation_content)
        
        if has_content:
            message = "Warning: One or both text boxes already contain content:\n\n"
            
            if study_content:
                study_preview = study_content[:50] + "..." if len(study_content) > 50 else study_content
                message += f"• Study Box: '{study_preview}'\n"
            
            if translation_content:
                translation_preview = translation_content[:50] + "..." if len(translation_content) > 50 else translation_content
                message += f"• Translation Box: '{translation_preview}'\n\n"
            
            message += "Proceeding may overwrite this content. Continue?"
            
            result = messagebox.askyesno("Content Warning", message, icon="warning")
            
            if not result:
                return False
        
        operation_callback(*args)
        return True

    # === PLACEHOLDER METHODS FOR UNCHANGED FUNCTIONALITY ===

    def translate_study_text(self):
        """AI: Translate study file conditionally with content warning"""
        self.check_content_and_warn(self._translate_study_text_impl)

    def _translate_study_text_impl(self):
        """Actual implementation of translate_study_text (moved from original method)"""
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

    def en_to_de_translation(self):
        """Get the contents of a vocabulary file (_VOC) to construct sentences"""
        self.check_content_and_warn(self._en_to_de_translation_impl)

    def _en_to_de_translation_impl(self):
        """Actual implementation of en_to_de_translation"""
        filename = None
        word_pairs = []
        
        # First, check if we already have vocabulary loaded in the textbox
        vocab_content = self.vocabulary_textbox.get(1.0, tk.END).strip()
        
        if vocab_content and self.vocabulary:  # Check if vocabulary textbox has content
            print("Using existing vocabulary from textbox")
            word_pairs = [line.strip() for line in vocab_content.splitlines() if line.strip()]
        else:
            # No vocabulary loaded, ask user to select a file
            filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            
            if not filename:  # User cancelled the dialog
                return
                
            if not (filename.endswith("_VOC.txt") or "_VOC.txt" in filename):
                messagebox.showwarning(
                    "Invalid File Type",
                    "Please select a vocabulary file with '_VOC.txt' in the filename.\n\n"
                    f"Selected file: {os.path.basename(filename)}"
                )
                return
                
            print(f"Selected file: {filename}")
            try:
                with open(filename, 'r', encoding='utf-8-sig') as file:
                    content = file.read()
                    word_pairs = [line.strip() for line in content.splitlines() if line.strip()]
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process file: {str(e)}", parent=self.root)
                return
        
        # Now create sentences from the word pairs
        if not word_pairs:
            messagebox.showwarning("Empty Vocabulary", "The vocabulary file or textbox is empty.")
            return
        
        # explain how to engage in this translation practice
        messagebox.showinfo("Instructions", 
                        "Study the sentences displayed in the 'Study Text Box'.\n\n"
                        "Use any other text box to write your translation per sentence.\n\n"
                        "DO NOT translate into the 'Translation Box' which can display "
                        "the correct translations by clicking 'Free-Hand Translation'")
        
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
        
        try:
            sentences = self.ask_chatgpt(prompt, model_name="gpt-4o", temperature=0.8)
            self.study_textbox.delete(1.0, tk.END)
            self.study_textbox.insert(tk.END, sentences)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate sentences: {str(e)}", parent=self.root)
    
    def search_vocabulary(self, vocab_text, search_term, search_type, case_sensitive):
        """Search for terms in vocabulary text"""
        lines = vocab_text.split('\n')
        matches = []
        
        if not case_sensitive:
            search_term = search_term.lower()
        
        for i, line in enumerate(lines):
            if not line.strip() or '=' not in line:
                continue
                
            try:
                german, english = line.split('=', 1)
                german = german.strip()
                english = english.strip()
                
                if search_type in ["german", "both"]:
                    text_to_search = german if case_sensitive else german.lower()
                    if search_term in text_to_search:
                        matches.append((i, line, "german"))
                
                if search_type in ["english", "both"]:
                    text_to_search = english if case_sensitive else english.lower()
                    if search_term in text_to_search:
                        matches.append((i, line, "english"))
                        
            except ValueError:
                continue
        
        return matches
    
    def highlight_vocabulary_matches(self, matches, search_term, case_sensitive):
        """Highlight search matches in the vocabulary textbox"""
        self.clear_vocabulary_highlights()
        
        # Configure highlight tag
        self.vocabulary_textbox.tag_configure("search_highlight", background="yellow", foreground="black")
        
        for line_num, line, language in matches:
            # Calculate start position of the line
            start_pos = f"{line_num + 1}.0"
            
            if language == "german":
                # Highlight German part (before =)
                if '=' in line:
                    german_part = line.split('=', 1)[0]
                    start_idx = line.find(search_term) if case_sensitive else line.lower().find(search_term.lower())
                    if start_idx != -1 and start_idx < len(german_part):
                        start = f"{line_num + 1}.{start_idx}"
                        end = f"{line_num + 1}.{start_idx + len(search_term)}"
                        self.vocabulary_textbox.tag_add("search_highlight", start, end)
            else:
                # Highlight English part (after =)
                if '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) > 1:
                        english_part = parts[1]
                        start_idx = line.find(search_term) if case_sensitive else line.lower().find(search_term.lower())
                        if start_idx != -1 and start_idx >= len(parts[0]):
                            # Adjust for the = sign
                            adjusted_start = start_idx
                            start = f"{line_num + 1}.{adjusted_start}"
                            end = f"{line_num + 1}.{adjusted_start + len(search_term)}"
                            self.vocabulary_textbox.tag_add("search_highlight", start, end)
        
        # Scroll to first match
        if matches:
            first_line = matches[0][0] + 1
            self.vocabulary_textbox.see(f"{first_line}.0")

    def clear_vocabulary_highlights(self):
        """Clear all search highlights"""
        self.vocabulary_textbox.tag_remove("search_highlight", "1.0", tk.END)

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
            # Insert examples without a leading blank line
            self.example_sentences_textbox.insert(tk.END, examples)

        except Exception as e:
            self.root.after(0, messagebox.showerror, "Examples Error", f"An error occurred: {e}")

    def fetch_glosbe_examples(self):
        """Get example sentences from Glosbe"""
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

    def fetch_langenscheidt(self):
        """Search word in Langenscheidt dictionary"""
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

    def search_own_vocab(self, event=None):
        """Search in own vocabulary"""
        # Get the word to search from the input field
        search_word = self.dictionary_entry.get().strip().lower()
        
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

    def show_vocabulary_search(self):
        """Simplified vocabulary search popup"""
        # Check if vocabulary textbox is empty
        vocab_content = self.vocabulary_textbox.get(1.0, tk.END).strip()
        if not vocab_content:
            messagebox.showwarning("Empty Vocabulary", "Please load a vocabulary file (_VOC.txt) first.")
            return
        
        # Only create the search window if vocabulary has content
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Vocabulary")
        search_window.configure(bg="#222")
        search_window.geometry("450x200")  # Increased height to 200
        search_window.transient(self.root)
        
        # Center the window
        search_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (search_window.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (search_window.winfo_height() // 2)
        search_window.geometry(f"+{x+400}+{y-300}")
        
        # Variables for navigation
        self.current_match_index = 0
        self.search_matches = []
        self.current_search_term = ""
        
        # Simple layout without nested frames
        tk.Label(search_window, text="Search for word:", bg="#222", fg="white").pack(pady=(10, 5))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_window, textvariable=search_var, width=40, bg="#333", fg="white") # this is input field
        search_entry.pack(pady=5)
        search_entry.focus()
        
        # Navigation frame (initially hidden)
        nav_frame = tk.Frame(search_window, bg="#222")
        
        # Navigation label to show current position
        nav_label = tk.Label(nav_frame, text="", bg="#222", fg="yellow", font=("Arial", 9))
        nav_label.pack(pady=5)
        
        # Navigation buttons
        nav_btn_frame = tk.Frame(nav_frame, bg="#222")
        nav_btn_frame.pack(pady=5)
        
        # Simple button frame
        btn_frame = tk.Frame(search_window, bg="#222")
        btn_frame.pack(pady=10)
        
        def jump_to_match(match_info):
            """Jump to the specific match in the vocabulary textbox"""
            try:
                # match_info is a tuple: (line_number, line_text, language)
                line_number = match_info[0]  # This is the line index (0-based)
                match_text = match_info[1]   # This is the full line text
                
                # Convert 0-based line number to 1-based for tkinter
                start_index = f"{line_number + 1}.0"
                end_index = f"{line_number + 1}.{len(match_text)}"
                
                # Scroll to the match and set focus
                self.vocabulary_textbox.focus_set()
                self.vocabulary_textbox.tag_remove(tk.SEL, "1.0", tk.END)
                self.vocabulary_textbox.tag_add(tk.SEL, start_index, end_index)
                self.vocabulary_textbox.mark_set(tk.INSERT, start_index)
                self.vocabulary_textbox.see(start_index)
                
            except Exception as e:
                print(f"Error jumping to match: {e}")
                # Fallback: just show the beginning
                self.vocabulary_textbox.see("1.0")
        
        def navigate_match(direction):
            """Navigate to next or previous match"""
            if direction == "next":
                self.current_match_index = (self.current_match_index + 1) % len(self.search_matches)
            elif direction == "prev":
                self.current_match_index = (self.current_match_index - 1) % len(self.search_matches)
            
            # Update highlights and navigation label
            self.highlight_vocabulary_matches(self.search_matches, self.current_search_term, False)
            jump_to_match(self.search_matches[self.current_match_index])
            nav_label.config(text=f"Match {self.current_match_index + 1} of {len(self.search_matches)}")
        
        # Search function
        def perform_search():
            search_term = search_var.get().strip()
            if search_term:
                vocab_text = self.vocabulary_textbox.get(1.0, tk.END)
                matches = self.search_vocabulary(vocab_text, search_term, "both", False)
                
                if matches:
                    # Store matches and reset navigation
                    self.search_matches = matches
                    self.current_search_term = search_term
                    self.current_match_index = 0
                    
                    # Show navigation if multiple matches
                    if len(matches) > 1:
                        nav_frame.pack(pady=5)
                        nav_label.config(text=f"Match 1 of {len(matches)}")
                        # Jump to first match
                        jump_to_match(matches[0])
                    else:
                        nav_frame.pack_forget()  # Hide navigation for single match
                        jump_to_match(matches[0])
                    
                    self.highlight_vocabulary_matches(matches, search_term, False)
                    messagebox.showinfo("Search Results", f"Found {len(matches)} matches")
                else:
                    self.search_matches = []
                    nav_frame.pack_forget()  # Hide navigation
                    messagebox.showinfo("Search Results", "No matches found")

        def clear_highlights():
            """Clear the search highlights from vocabulary"""
            self.clear_vocabulary_highlights()
            self.search_matches = []
            nav_frame.pack_forget()  # Hide navigation
            # messagebox.showinfo("Cleared", "All highlights cleared")
        
        def new_entry():
            """Clear the input field to search for new word"""
            search_entry.delete(0, tk.END)

        
        # Navigation buttons
        ttk.Button(nav_btn_frame, text="◀ Previous", 
                command=lambda: navigate_match("prev")).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_btn_frame, text="Next ▶", 
                command=lambda: navigate_match("next")).pack(side=tk.LEFT, padx=5)
        
        # Main buttons
        ttk.Button(btn_frame, text="Search", command=perform_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Word", command=new_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Highlights", command=clear_highlights).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=search_window.destroy).pack(side=tk.LEFT, padx=5)
        
        search_entry.bind('<Return>', lambda e: perform_search())

    # === FILE OPERATION PLACEHOLDERS ===

    def copy_study_text(self):
        """Copy the Study Text Box content to the clipboard."""
        try:
            content = self.study_textbox.get(1.0, tk.END).strip()

            if not content:
                messagebox.showwarning("No Text", "Study Text Box is empty.", parent=self.root)
                return

            # Update the clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(content)

            # Optional feedback to the user
            messagebox.showinfo("Copied", "Study text copied to clipboard!", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy study text: {e}", parent=self.root)

    def load_study_text(self):
        """Load study text file"""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

        if filename.endswith("_TXT.txt") or "_TXT.txt" in filename:
            self.current_study_file = filename
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                
                # Extract title
                title = self.extract_title_from_text(content)
                
                # Update the label - search more broadly
                self.update_study_text_label(title)
                
                # Remove title line and insert cleaned content
                cleaned_content = self.remove_title_line(content)
                self.study_textbox.delete(1.0, tk.END)
                self.study_textbox.insert(tk.END, cleaned_content)

    def save_study_text(self):
        """Save study text to file"""
        filename = None  # Initialize filename to None
        
        if not self.current_study_file:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )

            if filename:
                nwext = os.path.splitext(filename)[0]
                if '_TXT' not in filename:
                    filename = nwext + '_TXT.txt'
                self.current_study_file = filename
            else:
                return  # User cancelled
        else:
            filename = self.current_study_file

        if filename:  # Now filename is guaranteed to be defined
            with open(filename, 'w', encoding='utf-8-sig') as file:
                content = self.study_textbox.get(1.0, tk.END)
                file.write(content)
            messagebox.showinfo("Success", f"File saved successfully at:\n{filename}")

    def clear_study_text(self):
        """Clear study text"""
        self.current_study_file = None
        self.study_textbox.delete(1.0, tk.END)
        self.current_study_file = None

    def load_translation(self):
        """Load translation file"""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

        if filename.endswith("_TRA.txt") or "_TRA.txt" in filename:
            self.current_translation_file = filename  # Save the loaded filename
            self.translation_content_cleared = False  # Reset flag when file is loaded
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                self.translation_textbox.insert(tk.END, content)

        else:
            messagebox.showwarning(
            "Invalid File Type",
            "The selected file is not a vocabulary file.\n\n"
            "Please select a file that ends with '_TRA.txt'.\n\n"
        )
            return

    def save_translation(self):
        """Save translation to file.
        
        Behavior:
        - If a translation file is loaded and content is NOT cleared, save to that file without prompting
        - If content is cleared/deleted and new content is added, prompt for a new filename
        - Otherwise, prompt for a filename
        """
        content = self.translation_textbox.get(1.0, tk.END).strip()
        
        # If no content, don't save
        if not content:
            messagebox.showwarning("No Content", "Translation box is empty. Nothing to save.")
            return
        
        # Check if we have a known file AND the content hasn't been cleared
        if hasattr(self, 'current_translation_file') and self.current_translation_file:
            # Check if content was cleared by looking at the flag
            if getattr(self, 'translation_content_cleared', False):
                # Content was cleared, so prompt for a new filename
                filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt")],
                    initialfile="translation.txt"
                )
                if filename:
                    nwext = os.path.splitext(filename)[0]
                    if '_TRA' not in filename:
                        filename = nwext + '_TRA.txt'
                    self.current_translation_file = filename
                    self.translation_content_cleared = False  # Reset flag
                    try:
                        with open(filename, 'w', encoding='utf-8-sig') as file:
                            file.write(content)
                        messagebox.showinfo("Success", f"Translation saved to:\n{filename}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save translation: {str(e)}")
                return
            else:
                # Content not cleared, save to the known file
                try:
                    with open(self.current_translation_file, 'w', encoding='utf-8-sig') as file:
                        file.write(content)
                    messagebox.showinfo("Success", f"Translation saved to:\n{self.current_translation_file}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save translation: {str(e)}")
                return
        
        # No known file, prompt for filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="translation.txt"
        )
        if filename:
            nwext = os.path.splitext(filename)[0]
            if '_TRA' not in filename:
                filename = nwext + '_TRA.txt'
            self.current_translation_file = filename
            self.translation_content_cleared = False  # Reset flag
            try:
                with open(filename, 'w', encoding='utf-8-sig') as file:
                    file.write(content)
                messagebox.showinfo("Success", f"Translation saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save translation: {str(e)}")

    def clear_translation(self):
        """Clear translation"""
        self.translation_content_cleared = True  # Set flag to indicate content was cleared
        self.translation_textbox.delete(1.0, tk.END)
        

    def beautify_vocabulary(self):
        """Beautify vocabulary: remove preceding numbers and duplicates"""
        import re
        
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
            
            # Remove preceding numbers (e.g., "1. ", "23. ")
            # This regex removes any number followed by a period and optional whitespace at the start
            cleaned_line = re.sub(r'^\d+\.\s*', '', stripped_line)
                
            # Only add if we haven't seen this line before
            if cleaned_line not in seen:
                seen.add(cleaned_line)
                unique_lines.append(cleaned_line)
        
        # Join with newlines and update the textbox (preserve original order, don't sort)
        beautified_content = '\n'.join(unique_lines) + '\n'  # Add final newline
        self.vocabulary_textbox.delete(1.0, tk.END)
        self.vocabulary_textbox.insert(tk.END, beautified_content)
        
        # Show how many duplicates were removed
        duplicate_count = len(content.splitlines()) - len(unique_lines)
        if duplicate_count > 0:
            messagebox.showinfo("Beautify Complete", 
                            f"Removed {duplicate_count} duplicate entries\n"
                            f"Removed preceding numbers from entries")
        else:
            messagebox.showinfo("Beautify Complete", 
                            f"Removed preceding numbers from entries")

    def fix_verbs(self):
        """Use the AI to find German verbs in the current Vocabulary textbox,
        convert them to the exact format required and replace the textbox contents
        with the AI-corrected content.
        """
        content = self.vocabulary_textbox.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("No Vocabulary", "The vocabulary box is empty.")
            return

        # Strategy:
        # 1) Ask the AI which numbered lines are verbs.
        # 2) Send only those verb lines to the AI to be fixed according to the CRITICAL VERB RULES.
        # 3) Append the corrected verb lines to the non-verb lines (preserving original order of non-verbs).
        try:
            lines = content.splitlines()

            rules = (
                "CRITICAL VERB RULES (MUST FOLLOW):\n\n"
                "- The part inside the square brackets MUST contain exactly TWO German forms:\n"
                "  1. First: Präteritum (1st/3rd person singular),\n"
                "  2. Second: Partizip II (past participle only, WITHOUT \"hat\"/\"ist\").\n\n"
                "- Do NOT include any auxiliary verbs in the brackets.\n"
                "- Always start each English translation with \"to\". Maximum three translations.\n"
                "- If uncertain, still give your best guess for [Präteritum, Partizip II] but ALWAYS keep the same format.\n"
                "- Examples and required output format: Infinitive, [Präteritum, Partizip II] = to ..., to ...\n\n"
            )

            # Step 1: Ask which lines are verbs
            numbered = "\n".join(f"{i+1}: {ln}" for i, ln in enumerate(lines))
            detect_prompt = (
                "Identify which lines in the numbered vocabulary are German verbs (including separable/prefixed/modal verbs).\n"
                + "Return ONLY the line numbers, one per line, in ascending order, no extra text.\n\n"
                + "Numbered Vocabulary:\n"
                + numbered
            )

            detect_resp = self.ask_chatgpt(detect_prompt, model_name="gpt-4o", temperature=0.0)

            import re
            verb_indices = []
            for l in detect_resp.splitlines():
                l = l.strip()
                if not l:
                    continue
                m = re.match(r"^(\d+)$", l)
                if m:
                    idx = int(m.group(1)) - 1
                    if 0 <= idx < len(lines):
                        verb_indices.append(idx)

            if not verb_indices:
                messagebox.showinfo("Fix Verbs", "No verbs detected. No changes made.")
                return

            # Step 2: Collect verb lines and ask AI to correct them per rules
            verb_lines = [lines[i] for i in verb_indices]
            verbs_input = "\n".join(verb_lines)

            correction_prompt = (
                rules
                + "You will be given only verb lines (one per line). For each input line produce a single corrected output line in the exact format:\n"
                + "Infinitive, [Präteritum, Partizip II] = to ..., to ...\n"
                + "Return exactly the same number of non-empty lines as inputs, in the same order, and NO other text.\n\n"
                + "Verb lines:\n"
                + verbs_input
            )

            correction_resp = self.ask_chatgpt(correction_prompt, model_name="gpt-4o", temperature=0.0)
            corrected_verbs = [ln.strip() for ln in correction_resp.splitlines() if ln.strip()]

            # Ensure we have at least as many corrected lines as inputs; otherwise try to salvage by taking first N non-empty
            if len(corrected_verbs) < len(verb_lines):
                # fallback: take first len(verb_lines) non-empty lines
                corrected_verbs = corrected_verbs[:len(verb_lines)]

            # Step 3: Build merged output: non-verb lines (in original order) followed by corrected verbs
            non_verb_lines = [lines[i] for i in range(len(lines)) if i not in verb_indices]
            final_lines = non_verb_lines + corrected_verbs

            merged = "\n".join(final_lines) + ("\n" if final_lines and not final_lines[-1].endswith("\n") else "")
            self.vocabulary_textbox.delete(1.0, tk.END)
            self.vocabulary_textbox.insert(tk.END, merged)
            messagebox.showinfo("Fix Verbs", "Verbs processed and appended to the vocabulary.")

        except Exception as e:
            messagebox.showerror("Fix Verbs Error", f"An error occurred while fixing verbs: {e}")

    def clear_vocabulary(self):
        """Clear vocabulary"""
        self.current_voc_file = None
        self.vocabulary_textbox.delete(1.0, tk.END)
        # Update the vocabulary label to remove the path
        try:
            self.update_vocabulary_label_path()
        except Exception:
            pass
        self.current_voc_file = None

    def capture_text(self):
        """Translate text using AI"""
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
        """Open notes editor"""
        NotesEditor(self.root)

    def clear_test(self):
        """Clear test section"""
        self.vocabulary = []
        self.score_label.config(text="0%")
        self.score = 0
        self.total_questions = 0  # Total number of questions asked
        self.correct_answers = 0  # Number of correct answers
        self.test_filename_label.config(text="File is: ")
        self.test_textbox.delete(1.0, tk.END)

    def clear_entry(self):
        """Clear dictionary entry"""
        self.dictionary_entry.delete(0, tk.END)

    def load_examples(self):
        """Load example sentences"""
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
        """Save example sentences"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            title="Select file to append to"
        )
        
        if filename: # debug
                try:
                    with open(filename, 'a+', encoding='utf-8-sig') as file:
                        content = self.example_sentences_textbox.get(1.0, tk.END)
                        file.write("\n\n")  # Add separation from previous content
                        file.write(content)
                    messagebox.showinfo("Success", f"Content appended to:\n{filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to append to file:\n{str(e)}")

    def clear_example_sentences(self):
        """Clear example sentences"""
        self.current_example_sentences_file = None
        self.example_sentences_textbox.delete(1.0, tk.END)

    def clear_examples_input(self):
        """Clear examples input"""
        self.glosbe_search_entry.delete(0, tk.END)

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
        """Copy AI responses to clipboard"""
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
        """Clear AI responses textbox"""
        self.ai_responses_textbox.delete(1.0, tk.END)


class NotesEditor:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Notes Editor")
        self.window.geometry("500x400")
        self.current_notes_file = None

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

    def open_default_file(self):
        filename = notes_filename
        self.current_notes_file = filename
        if filename:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                self.text.insert(tk.END, content)
        
    def save_file(self):
        """Save to current file or prompt for new file if none exists"""
        if not self.current_notes_file:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")]
            )
            if filename:
                self.current_notes_file = filename
        else:
            filename = self.current_notes_file

        if filename:
            with open(filename, 'w', encoding='utf-8-sig') as file:
                content = self.text.get(1.0, tk.END)
                file.write(content)
            messagebox.showinfo("Success", f"File saved successfully at:\n{filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VocabularyApp(root)
    root.mainloop()