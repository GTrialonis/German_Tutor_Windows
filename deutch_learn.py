from openai import OpenAI
import tkinter as tk
from tkinter import ttk # Add this line
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
import threading
import time

# Add these imports at the top of your file
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

        # Add TTS voice options
        self.tts_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.current_voice = "nova"  # Default voice (sounds good for German)

        # --------- LISTENING COMPREHENSION ---------
        # Add these variables for listening comprehension
        # Add these variables for listening comprehension
        self.listening_comprehension_text = ""
        self.current_questions = []
        self.current_question_index = 0
        self.listening_score = 0
        self.total_listening_questions = 0
    
        # ADD THIS - Create the list_compr_files directory if it doesn't exist
        self.listening_dir = "list_compr_files"
        os.makedirs(self.listening_dir, exist_ok=True)

        # Create a smaller font for the highlight buttons
        self.small_button_font = tkFont.Font(family="Helvetica", size=8, weight="normal")
        
        # MANUAL CONFIGURATION OF COLOR BUTTONS
        # ... inside __init__ method ...
        self.style = ttk.Style()
        # Define a custom style for a purple button
        self.style.theme_use('default') # Ensure a base theme is used
        self.style.configure('SmallPurple.TButton',
                            background="#ca74ea", # Your desired background color
                            foreground='black',   # Your desired text color
                            font=self.small_button_font) # Use your defined font object
        # Define a custom style for a red button
        self.style.configure('SmallRed.TButton',
                            background='#AA0000', # Your desired background color
                            foreground='white',   # Your desired text color
                            font=self.small_button_font) # Use your defined font object
        # Define a custom style for a green button
        self.style.configure('SmallGreen.TButton',
                            background='#008844', # Your desired background color
                            foreground='black',   # Your desired text color
                            font=self.small_button_font) # Use your defined font object
        # ... you'll need to define similar styles for all your button colors

        # Add these variables for text-to-speech functionality
        self.is_reading = False
        self.current_audio_file = None
        self.reading_paused = False
        self.reading_thread = None

        # Inside your __init__(self, root) method:
        self.style = ttk.Style()
        self.style.theme_use('default') # Ensure a base theme is used

        # Define styles for all your button colors
        self.style.configure('SmallDarkPurple.TButton',
                            background='#ca74ea',
                            foreground='black',
                            font=self.small_button_font)

        self.style.configure('SmallBlue.TButton',
                            background="#73A2D0",
                            foreground='black',
                            font=self.small_button_font)

        self.style.configure('SmallGreen.TButton',
                            background='#008844',
                            foreground='black',
                            font=self.small_button_font)

        self.style.configure('SmallRed.TButton',
                            background='#AA0000',
                            foreground='black',
                            font=self.small_button_font)

        self.style.configure('SmallGoldBrown.TButton', # For SORT, NOTES, Flip Sentences
                            background='#AA8800',
                            foreground='black', # Check your specific fg for these
                            font=self.small_button_font)

        self.style.configure('SmallLightPurple.TButton', # For Free-Hand Translation
                            background='#cbb0e0',
                            foreground='black', # Check your specific fg for this
                            font=self.small_button_font)

        self.style.configure('SmallOrange.TButton', # For Clear Input, Clear Test
                            background='orange',
                            foreground='black', # Check your specific fg for these
                            font=self.small_button_font)

        self.style.configure('SmallDarkBlue.TButton', # For Next Word
                            background='#005588',
                            foreground='black',
                            font=self.small_button_font)

        self.style.configure('SmallGrayBlue.TButton', # For Langenscheidt
                            background="#9DC1E4",
                            foreground='black',
                            font=self.small_button_font)

        self.style.configure('SmallDarkOlive.TButton', # For Search OWN vocab.
                            background="#95C068",
                            foreground='black',
                            font=self.small_button_font)

        self.style.configure('SmallOliveGreen.TButton', # For Glosbe Examples
                            background='#95946A',
                            foreground='black',
                            font=self.small_button_font)
        
        self.style.configure('SmallGreenish.TButton', # For Glosbe Examples
                            background="#AABD7E",
                            foreground='black',
                            font=self.left_section_font)
        
        self.style.configure('SmallWhiteBlue.TButton', # For SORT, NOTES, Flip Sentences
                            background="#AACCC6",
                            foreground='black', # Check your specific fg for these
                            font=self.small_button_font)
        
        self.style.configure('SmallDarkOrange.TButton', # For SORT, NOTES, Flip Sentences
                            background="#AA5200",
                            foreground='black', # Check your specific fg for these
                            font=self.small_button_font)
        
        # In your __init__ method, add these style definitions
        self.style.configure('SmallWhite.TButton',
                    background='#7B7D7D',
                    foreground='white',
                    font=self.small_button_font)

        self.style.configure('SmallGoldYellow.TButton',
                    background="#EBCE65",
                    foreground='black',
                    font=self.small_button_font) # For LISTENING Comprehension Button
        
        self.style.configure('SmallBlueish.TButton',
                    background='#5D6D7E',
                    foreground='white',
                    font=self.small_button_font)

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

        self.evaluated_questions = set()  # Track which questions have been evaluated

        # Ensure Prompt AI button is enabled on startup
        self.root.after(100, self.ensure_prompt_ai_enabled)
    
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
    
    # ------------- LISTENING ONLY ----------
    def create_listen_functionality(self):
        """Create popup for text-to-speech only (no comprehension questions)"""
        listen_window = tk.Toplevel(self.root)
        listen_window.title("Listen to Text")
        listen_window.configure(bg="#222")
        listen_window.geometry("400x300")
        listen_window.transient(self.root)
        listen_window.grab_set()
        
        # Center the window
        listen_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (listen_window.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (listen_window.winfo_height() // 2)
        listen_window.geometry(f"+{x}+{y}")
        
        # Voice selection
        tk.Label(listen_window, text="Select Voice:", bg="#222", fg="white", font=("Arial", 12, "bold")).pack(pady=(15, 8))
        
        voice_var = tk.StringVar(value="alloy")
        voices_frame = tk.Frame(listen_window, bg="#222")
        voices_frame.pack(pady=8)
        
        voice_colors = {
            "alloy": "#4A90E2",    # Blue
            "echo": "#50E3C2",     # Teal
            "fable": "#B8E986",    # Green
            "onyx": "#BD10E0",     # Purple
            "nova": "#F5A623"      # Orange
        }
        
        for voice in ["alloy", "echo", "fable", "onyx", "nova"]:
            tk.Radiobutton(voices_frame, text=voice.capitalize(), variable=voice_var, 
                        value=voice, bg="#222", fg="white", selectcolor=voice_colors[voice],
                        font=("Arial", 10)).pack(side=tk.LEFT, padx=8)
        
        # Button frame
        btn_frame = tk.Frame(listen_window, bg="#222")
        btn_frame.pack(pady=25)
        
        # Track if speech is playing
        self.speech_playing = False
        
        def listen_from_file():
            if not self.speech_playing:
                filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
                if filename:
                    try:
                        with open(filename, 'r', encoding='utf-8') as file:
                            text = file.read()
                            self.speech_playing = True
                            listen_window.attributes('-disabled', True)  # Disable window during speech
                            self.speak_text(text, voice_var.get(), listen_window)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to read file: {str(e)}")
        
        def listen_from_study_box():
            if not self.speech_playing:
                text = self.study_textbox.get(1.0, tk.END).strip()
                if text:
                    self.speech_playing = True
                    listen_window.attributes('-disabled', True)
                    self.speak_text(text, voice_var.get(), listen_window)
                else:
                    messagebox.showwarning("No Text", "Study Text Box is empty.")
        
        def listen_from_clipboard():
            if not self.speech_playing:
                try:
                    text = self.root.clipboard_get()
                    if text.strip():
                        self.speech_playing = True
                        listen_window.attributes('-disabled', True)
                        self.speak_text(text, voice_var.get(), listen_window)
                    else:
                        messagebox.showwarning("Empty Clipboard", "Clipboard is empty or contains no text.")
                except:
                    messagebox.showwarning("Clipboard Error", "Cannot access clipboard or no text available.")
        
        def cancel_listen():
            if not self.speech_playing:
                listen_window.destroy()
        
        # Colorful buttons with styles
        ttk.Button(btn_frame, text="📁 Load TXT File", style='SmallBlue.TButton', 
                command=listen_from_file).pack(pady=6, fill=tk.X)
        ttk.Button(btn_frame, text="📖 Read from Study Text Box", style='SmallGreen.TButton', 
                command=listen_from_study_box).pack(pady=6, fill=tk.X)
        ttk.Button(btn_frame, text="📋 Read from Clipboard", style='SmallPurple.TButton', 
                command=listen_from_clipboard).pack(pady=6, fill=tk.X)
        ttk.Button(btn_frame, text="❌ Cancel", style='SmallRed.TButton', 
                command=cancel_listen).pack(pady=10, fill=tk.X)
        
        # Handle window close (X button)
        def on_closing():
            if not self.speech_playing:
                listen_window.destroy()
            else:
                messagebox.showinfo("Speech Playing", "Please wait for speech to finish.")
        
        listen_window.protocol("WM_DELETE_WINDOW", on_closing)

    def create_listening_comprehension(self):
        """Create the listening comprehension popup window with voice selection"""
        listen_comp_window = tk.Toplevel(self.root)
        listen_comp_window.title("Listening Comprehension")
        listen_comp_window.configure(bg="#222")
        listen_comp_window.geometry("400x250")
        listen_comp_window.transient(self.root)
        listen_comp_window.grab_set()
        
        # Center the window
        listen_comp_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (listen_comp_window.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (listen_comp_window.winfo_height() // 2)
        listen_comp_window.geometry(f"+{x}+{y}")
        
        # Create buttons
        frame = tk.Frame(listen_comp_window, bg="#222")
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Voice selection - DEFINE THIS FIRST
        voice_label = tk.Label(frame, text="Select Voice:", bg="#222", fg="white")
        voice_label.pack(anchor=tk.W, pady=(0, 5))
        
        voice_var = tk.StringVar(value="alloy")  # Default voice
        
        voice_frame = tk.Frame(frame, bg="#222")
        voice_frame.pack(fill=tk.X, pady=(0, 15))
        
        voices = [("Alloy", "alloy"), ("Echo", "echo"), ("Fable", "fable"), 
                ("Onyx", "onyx"), ("Nova", "nova"), ("Shimmer", "shimmer")]
        
        for i, (name, value) in enumerate(voices):
            rb = tk.Radiobutton(voice_frame, text=name, variable=voice_var, value=value,
                            bg="#222", fg="white", selectcolor="#444")
            rb.pack(side=tk.LEFT, padx=(0, 10))
        
        # NOW create buttons that use voice_var - it's defined now
        ttk.Button(frame, text="Load German Text File", 
                style='SmallBlue.TButton',
                command=lambda v=voice_var.get(): self.start_listening_from_file(listen_comp_window, v)).pack(pady=5, fill=tk.X)
        
        ttk.Button(frame, text="Search Internet for German Text", 
                style='SmallGreen.TButton',
                command=lambda v=voice_var.get(): self.search_german_text(listen_comp_window, v)).pack(pady=5, fill=tk.X)
        
        ttk.Button(frame, text="Cancel", 
                style='SmallRed.TButton',
                command=listen_comp_window.destroy).pack(pady=5, fill=tk.X)
    
    def set_voice(self, voice):
        """Set the TTS voice"""
        self.current_voice = voice
        print(f"Voice set to: {voice}")

    def test_current_voice(self):
        """Test the currently selected voice"""
        test_text = "Hallo! Dies ist eine Testnachricht um die Stimme zu prüfen."
        threading.Thread(
            target=self.speak_text, 
            args=(test_text,),
            daemon=True
        ).start()
    

    def safe_ui_update(self, widget, method, *args, **kwargs):
        """Safely update UI elements from threads"""
        try:
            if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                if method == "config":
                    widget.config(**kwargs)
                elif method == "set":
                    widget.set(*args)
                else:
                    getattr(widget, method)(*args, **kwargs)
        except Exception as e:
            print(f"UI update failed (widget probably destroyed): {e}")
    
    def start_reading_from_file(self, parent_window, voice):
        """Start reading from a selected text file"""
        filename = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    text_content = file.read()
                parent_window.destroy()
                self.show_reading_controls(text_content, f"File: {os.path.basename(filename)}", voice)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")
    

    def start_reading_from_textbox(self, parent_window, voice):
        """Start reading from the Study Text Box"""
        text_content = self.study_textbox.get(1.0, tk.END).strip()
        
        if not text_content:
            messagebox.showwarning("No Text", "Study Text Box is empty.")
            return
        
        parent_window.destroy()
        self.show_reading_controls(text_content, "Study Text Box", voice)
    

    def show_listening_text_reading_controls(self):
        """Show reading controls for the listening comprehension text"""
        if not self.listening_comprehension_text:
            messagebox.showwarning("No Text", "No German text available to read.")
            return
        
        # Use the selected voice (default to alloy if not set)
        voice = getattr(self, 'current_voice', 'alloy')
        
        # Show reading controls popup
        self.show_reading_controls(
            self.listening_comprehension_text, 
            "Listening Comprehension Text", 
            voice
        )
        
        # After reading is done, generate questions
        self.check_reading_complete_and_generate_questions()

    def check_reading_complete_and_generate_questions(self):
        """Check if reading is complete and then generate questions"""
        def check():
            if not self.is_reading:
                # Reading is complete, now generate questions
                self.root.after(1000, self.generate_listening_questions)
            else:
                # Check again in 1 second
                self.root.after(1000, check)
        
        check()

    def show_reading_controls(self, text_content, source_name, voice):
        """Show the reading controls window"""
        # Stop any current reading
        self.stop_reading()
        
        # Create controls window
        controls_window = tk.Toplevel(self.root)
        controls_window.title(f"Reading: {source_name}")
        controls_window.configure(bg="#222")
        controls_window.geometry("400x200")
        controls_window.transient(self.root)
        
        # Make window stay on top
        controls_window.attributes('-topmost', True)
        
        # Center the window
        controls_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (controls_window.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (controls_window.winfo_height() // 2)
        controls_window.geometry(f"+{x}+{y}")
        
        # Content frame
        content_frame = tk.Frame(controls_window, bg="#222")
        content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Source label
        source_label = tk.Label(content_frame, text=f"Source: {source_name}", 
                            bg="#222", fg="white", font=("Helvetica", 10, "bold"))
        source_label.pack(pady=(0, 10))
        
        # Status label
        status_label = tk.Label(content_frame, text="Ready to read", 
                            bg="#222", fg="lightgreen", font=("Helvetica", 9))
        status_label.pack(pady=(0, 10))
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(content_frame, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        # Control buttons frame
        button_frame = tk.Frame(content_frame, bg="#222")
        button_frame.pack(fill=tk.X)
        
        # Control buttons - UPDATE the play_button command to generate questions after reading
        play_button = ttk.Button(button_frame, text="Start Reading", 
                                style='SmallGreen.TButton',
                                command=lambda: self.start_reading_and_generate_questions(
                                    text_content, play_button, pause_button, status_label, progress_var, voice, controls_window
                                ))
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
        
        # Store references for cleanup
        controls_window.protocol("WM_DELETE_WINDOW", 
                            lambda: self.stop_reading_ui(controls_window, play_button, pause_button, status_label, progress_var))
        
        self.current_controls_window = controls_window

    
    def start_reading_and_generate_questions(self, text_content, play_button, pause_button, status_label, progress_var, voice, controls_window):
        """Start reading and set up question generation after completion"""
        # Start the reading
        self.toggle_reading(text_content, play_button, pause_button, status_label, progress_var, voice)
        
        # Set up completion handler
        def check_reading_complete():
            if not self.is_reading:
                # Reading complete, close reading window and generate questions
                controls_window.destroy()
                self.generate_listening_questions()
            else:
                # Check again in 1 second
                self.root.after(1000, check_reading_complete)
        
        check_reading_complete()

    
    def handle_listening_answer(self):
        """Handle when user submits an answer during listening comprehension"""
        if not hasattr(self, 'current_questions') or not self.current_questions:
            self.prompt_ai()
            return
        
        user_answer = self.input_textbox.get(1.0, tk.END).strip()
        
        if not user_answer:
            messagebox.showwarning("No Answer", "Please type your answer before submitting.")
            return
        
        if len(user_answer.split()) < 3:
            messagebox.showwarning("Short Answer", "Please provide a more detailed answer (at least 3 words).")
            return
        
        # Check if this question has already been evaluated
        current_q_index = self.current_question_index
        if current_q_index in self.evaluated_questions:
            messagebox.showinfo("Already Evaluated", "This question has already been evaluated. Please proceed to next question.")
            return
        
        # Evaluate and mark as evaluated
        self.evaluate_answer(user_answer)
        self.evaluated_questions.add(current_q_index)
        
        # Check if this was the last question
        if len(self.evaluated_questions) >= len(self.current_questions):
            # Last question evaluated - end session
            self.end_listening_comprehension_session()
    

    def end_listening_comprehension_session(self):
        """End the listening comprehension session and reset button states"""
        # Reset button states
        if hasattr(self, 'eval_answer_btn'):
            self.eval_answer_btn.config(state="disabled")
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state="normal")
        
        # Clear session data
        self.current_questions = []
        self.evaluated_questions = set()
        self.current_question_index = 0
        
        # Close any open popup windows
        try:
            if hasattr(self, 'listening_window') and self.listening_window:
                self.listening_window.destroy()
        except:
            pass
        
        messagebox.showinfo("Session Complete", "All questions have been evaluated. Listening comprehension session ended.")
    

    def toggle_reading(self, text_content, play_button, pause_button, status_label, progress_var, voice):
        """Start or resume reading"""
        if not self.is_reading:
            # Start reading
            self.is_reading = True
            self.reading_paused = False
            
            # --- SAFE UI UPDATES FOR START ---
            def safe_start_ui():
                try:
                    if play_button and play_button.winfo_exists():
                        play_button.config(state=tk.DISABLED)
                    if pause_button and pause_button.winfo_exists():
                        pause_button.config(state=tk.NORMAL)
                    if status_label and status_label.winfo_exists():
                        status_label.config(text="Reading...", fg="lightgreen")
                    if progress_var and progress_var._root.winfo_exists():
                        progress_var.set(0)
                except Exception as e:
                    print(f"UI update error in safe_start_ui: {e}")
            
            # Execute UI updates
            safe_start_ui()
            
            # Start reading in a separate thread
            self.reading_thread = threading.Thread(
                target=self.read_text, 
                args=(text_content, status_label, progress_var, play_button, pause_button, voice),
                daemon=True
            )
            self.reading_thread.start()
            
        elif self.reading_paused:
            # Resume reading
            self.reading_paused = False
            pygame.mixer.music.unpause()
            
            # --- SAFE UI UPDATES FOR RESUME ---
            def safe_resume_ui():
                try:
                    if pause_button and pause_button.winfo_exists():
                        pause_button.config(text="Pause")
                    if status_label and status_label.winfo_exists():
                        status_label.config(text="Reading...", fg="lightgreen")
                except Exception as e:
                    print(f"UI update error in safe_resume_ui: {e}")
            
            safe_resume_ui()
    
    def toggle_pause(self, pause_button, status_label):
        """Pause or resume reading"""
        if self.is_reading and not self.reading_paused:
            # Pause reading
            self.reading_paused = True
            pygame.mixer.music.pause()
            pause_button.config(text="Resume")
            status_label.config(text="Paused", fg="yellow")
        elif self.is_reading and self.reading_paused:
            # Resume reading
            self.reading_paused = False
            pygame.mixer.music.unpause()
            pause_button.config(text="Pause")
            status_label.config(text="Reading...", fg="lightgreen")
    
    def read_text(self, text_content, status_label, progress_var, play_button=None, pause_button=None, voice="alloy"):
        """Unified read_text function with OpenAI TTS and proper cleanup"""
        try:
            # Store UI references for safe cleanup
            ui_elements = {
                'status_label': status_label,
                'progress_var': progress_var,
                'play_button': play_button,
                'pause_button': pause_button
            }
            
            # Generate speech using OpenAI TTS
            if status_label and status_label.winfo_exists():
                status_label.after(0, lambda: status_label.config(text="Generating speech...", fg="yellow"))
            
            # Use OpenAI TTS instead of gTTS - SINGLE FILE APPROACH
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                audio_file = temp_audio.name
            
            try:
                # Generate speech with OpenAI
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text_content,
                )
                
                response.stream_to_file(audio_file)
                
            except Exception as e:
                # Fallback to gTTS if OpenAI fails
                print(f"OpenAI TTS failed, using gTTS: {e}")
                tts = gTTS(text=text_content, lang='de', slow=False)
                tts.save(audio_file)
            
            # Stop any current playback
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.time.wait(200)
            
            # Load and play the audio
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            if status_label and status_label.winfo_exists():
                status_label.after(0, lambda: status_label.config(text="Reading...", fg="lightgreen"))
            
            # Wait for playback to finish, respecting pause/resume
            start_time = time.time()
            estimated_duration = len(text_content) * 0.1  # Rough estimate
            
            while (pygame.mixer.music.get_busy() or self.reading_paused) and self.is_reading:
                if not self.reading_paused and progress_var and progress_var._root.winfo_exists():
                    elapsed = time.time() - start_time
                    progress = min((elapsed / estimated_duration) * 100, 100) if estimated_duration > 0 else 0
                    try:
                        progress_var.set(progress)
                    except:
                        pass
                
                time.sleep(0.1)
            
            # --- RESET UI STATE WHEN READING FINISHES (only if buttons were provided) ---
            if self.is_reading:
                if progress_var and progress_var._root.winfo_exists():
                    progress_var.set(100)
                if status_label and status_label.winfo_exists():
                    status_label.after(0, lambda: status_label.config(text="Reading complete", fg="lightblue"))
            
        except Exception as e:
            print(f"Error in read_text: {e}")
            # --- RESET UI STATE ON ERROR TOO ---
            if status_label and status_label.winfo_exists():
                status_label.after(0, lambda: status_label.config(text=f"Error: {str(e)}", fg="red"))
        
        finally:
            # --- ALWAYS RESET STATE AND CLEAN UP ---
            self.is_reading = False
            self.reading_paused = False
            
            # --- SAFE UI UPDATES ---
            def safe_ui_update():
                try:
                    if play_button and play_button.winfo_exists():
                        play_button.config(state=tk.NORMAL)
                    if pause_button and pause_button.winfo_exists():
                        pause_button.config(state=tk.DISABLED, text="Pause")
                except Exception as e:
                    print(f"UI update error in safe_ui_update: {e}")
            
            # Only attempt UI updates if we have button references
            if play_button or pause_button:
                try:
                    if play_button and play_button.winfo_exists():
                        play_button.after(0, safe_ui_update)
                    elif pause_button and pause_button.winfo_exists():
                        pause_button.after(0, safe_ui_update)
                    else:
                        # If no valid buttons, just call directly
                        safe_ui_update()
                except Exception as e:
                    print(f"Error scheduling UI update: {e}")
                    safe_ui_update()  # Fallback
            
            # --- CLEAN UP THE SINGLE AUDIO FILE ---
            self.safe_cleanup_audio_file(audio_file)

    def split_text_for_tts(self, text, max_length=1000):
        """Split text into chunks for TTS, trying to keep sentences intact"""
        import re
        
        # Split by sentences first
        sentences = re.split(r'([.!?]+[\s$])', text)
        
        # Reconstruct sentences with their punctuation
        reconstructed = []
        i = 0
        while i < len(sentences):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i+1]
                i += 2
            else:
                sentence = sentences[i]
                i += 1
            reconstructed.append(sentence.strip())
        
        # Group sentences into chunks
        chunks = []
        current_chunk = ""
        
        for sentence in reconstructed:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [text]
    
    def safe_cleanup_audio_file(self, audio_file):
        """Simple file cleanup - just try once and log if it fails"""
        if not audio_file or not os.path.exists(audio_file):
            return
        
        try:
            # Just try to delete it once
            os.unlink(audio_file)
        except Exception as e:
            # If it fails, schedule one retry after 10 seconds
            print(f"Initial cleanup failed for {audio_file}: {e}")
            self.root.after(10000, lambda: self.final_cleanup(audio_file))

    def delayed_cleanup(self, audio_file):
        """Delayed cleanup attempt"""
        if os.path.exists(audio_file):
            try:
                os.unlink(audio_file)
                print(f"Delayed cleanup successful: {audio_file}")
            except:
                print(f"Delayed cleanup failed: {audio_file}")

    def final_cleanup(self, audio_file):
        """Final cleanup attempt"""
        if os.path.exists(audio_file):
            try:
                os.unlink(audio_file)
                print(f"Final cleanup successful: {audio_file}")
            except Exception as e:
                print(f"Permanent cleanup failure for {audio_file}: {e}")
                # Don't retry further - these are temp files that will be cleaned up by system eventually


    def read_single_chunk(self, text, chunk_info=""):
        """Read a single chunk of text reliably"""
        temp_file = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_file = temp_audio.name
            
            # Generate speech
            tts = gTTS(text=text, lang='de', slow=False)
            tts.save(temp_file)
            
            # Ensure pygame mixer is ready
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Stop any current playback
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.time.wait(200)
            
            # Load and play
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            start_time = pygame.time.get_ticks()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                # Safety timeout
                if pygame.time.get_ticks() - start_time > 30000:  # 30 second timeout per chunk
                    pygame.mixer.music.stop()
                    break
            
            # Success
            return True
            
        except Exception as e:
            print(f"Error reading chunk {chunk_info}: {e}")
            return False
            
        finally:
            # Always try to clean up the temp file
            if temp_file and os.path.exists(temp_file):
                self.safe_delete_file_delayed(temp_file)


    def safe_delete_file_delayed(self, filepath, delay=1000):
        """Delete a file after a delay to ensure it's not in use"""
        def delete_file():
            if filepath and os.path.exists(filepath):
                try:
                    os.unlink(filepath)
                except:
                    pass  # Ignore cleanup errors
        
        self.root.after(delay, delete_file)

    def finish_reading_and_start_questions(self, reading_window):
        """Close reading window and start question session"""
        if reading_window:
            reading_window.destroy()
        
        # Start the question session
        self.generate_questions_after_reading()


    def stop_reading(self):
        """Stop reading completely"""
        self.is_reading = False
        self.reading_paused = False
        
        # Stop audio playback with proper cleanup
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.time.wait(100)  # Give time for playback to stop
        
        # Note: We don't delete the current_audio_file here anymore since we're using chunk files
        # The cleanup will happen in the read_text method
    
    def stop_reading_ui(self, controls_window, play_button, pause_button, status_label, progress_var):
        """Stop reading and clean up UI"""
        # Stop reading first
        self.stop_reading()
        
        # --- SAFE UI UPDATES FOR STOP ---
        def safe_stop_ui():
            try:
                if progress_var and progress_var._root.winfo_exists():
                    progress_var.set(0)
                if status_label and status_label.winfo_exists():
                    status_label.config(text="Stopped", fg="red")
                if play_button and play_button.winfo_exists():
                    play_button.config(state=tk.NORMAL)
                if pause_button and pause_button.winfo_exists():
                    pause_button.config(state=tk.DISABLED, text="Pause")
            except Exception as e:
                print(f"UI update error in safe_stop_ui: {e}")
        
        safe_stop_ui()
        
        # Close the controls window if it exists
        if controls_window and controls_window.winfo_exists():
            try:
                controls_window.destroy()
            except:
                pass
    
    def stop_reading(self):
        """Stop reading completely"""
        self.is_reading = False
        self.reading_paused = False
        
        # Stop audio playback with proper cleanup
        if pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.stop()
                pygame.time.wait(200)  # Give time for playback to stop
            except:
                pass
   
    def cleanup_audio_files_delayed(self, audio_files, delay=500):
        """Clean up audio files after a delay to ensure pygame has released them"""
        def delayed_cleanup():
            for audio_file in audio_files:
                if audio_file and os.path.exists(audio_file):
                    self.safe_delete_file(audio_file)
        
        # Schedule cleanup after a delay
        self.root.after(delay, delayed_cleanup)

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
        """AI creates vocabulary from txt file with content warning"""
        # Use the warning check before proceeding
        self.check_content_and_warn(self._create_vocabulary_impl)

    def _create_vocabulary_impl(self):
        """Actual implementation of create_vocabulary (moved from original method)"""
        filename = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()

            configure_openai()

            prompt = (
            """You are a German-English linguistic analysis tool. Your task is to process a German text, filter it based on a custom stopword list, and then generate a formatted vocabulary list with specific grammatical information and English translations.

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

            For Verbs:

            From any form of a verb found in the text (e.g., "spricht"), identify its infinitive (base form).

            Format: Infinitive, [Präteritum, Perfekt] = to translation1, to translation2, to translation3

            Always include "to" before the English translations.

            Example: sprechen, [sprach, gesprochen] = to speak, to talk

            For Adjectives:

            From any form of an adjective, identify its positive (base) form.

            Format: Positive Form, [Comparative Form, Superlative Form] = translation1, translation2, translation3

            Example: schnell, [schneller, schnellsten] = fast, quick, rapid

            For Adverbs and All Other Word Types:

            Display the word in its base/dictionary form.

            Format: German Word = translation1, translation2, translation3

            Example: oft = often, frequently
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
        """AI: Translate study file conditionally with content warning"""
        # Use the warning check before proceeding
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
        """Get the contents of a vocabulary file (_VOC) to construct sentences"""
        # Use the warning check before proceeding
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
        
        # Create vocabulary section with search functionality
        vocab_frame = tk.Frame(left_frame, bg="#222")
        vocab_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Vocabulary label and search button
        # label_frame = tk.Frame(vocab_frame, bg="#222")
        # label_frame.pack(fill=tk.X)
        
        
        # Create textboxes - only add highlight buttons to Study Text Box and Translation Box
        self.vocabulary_textbox = self.create_labeled_textbox(left_frame, "Vocabulary (Current):", True, height=10, label_font=font, add_buttons=False)
        self.study_textbox = self.create_labeled_textbox(left_frame, "Study Text Box:", True, height=10, label_font=font, add_buttons=True)
        self.translation_textbox = self.create_labeled_textbox(left_frame, "Translation Box:", True, height=10, label_font=font, add_buttons=True)
        self.input_textbox = self.create_labeled_textbox(left_frame, "Prompt the AI by writing below", True, height=5, label_font=font, add_buttons=False)


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
            command=self.handle_listening_answer,
            state="disabled"  # Initially disabled
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
        search_window.geometry(f"+{x}+{y}")
        
        # Variables for navigation
        self.current_match_index = 0
        self.search_matches = []
        self.current_search_term = ""
        
        # Simple layout without nested frames
        tk.Label(search_window, text="Search for word:", bg="#222", fg="white").pack(pady=(10, 5))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_window, textvariable=search_var, width=40, bg="#333", fg="white")
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
            messagebox.showinfo("Cleared", "All highlights cleared")
        
        # Navigation buttons
        ttk.Button(nav_btn_frame, text="◀ Previous", 
                command=lambda: navigate_match("prev")).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_btn_frame, text="Next ▶", 
                command=lambda: navigate_match("next")).pack(side=tk.LEFT, padx=5)
        
        # Main buttons
        ttk.Button(btn_frame, text="Search", command=perform_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Highlights", command=clear_highlights).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=search_window.destroy).pack(side=tk.LEFT, padx=5)
        
        search_entry.bind('<Return>', lambda e: perform_search())


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


    def create_middle_section(self):
        middle_frame = tk.Frame(self.root, bg="#222")
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=12)
        
    # --- Group 1: Vocabulary Buttons ---
    # Create a frame for the Vocabulary buttons
        vocab_btn_frame = tk.Frame(middle_frame, bg="#222")
        vocab_btn_frame.pack(pady=(0, 25)) # <--- TOP & BOTTOM PADDING for this GROUP (e.g., 25 pixels at bottom)

    # Buttons for Vocabulary Box - pack into vocab_btn_frame
        ttk.Button(vocab_btn_frame, text="LOAD-VOC", style='SmallBlue.TButton', command=self.load_vocabulary).pack(pady=2)
        ttk.Button(vocab_btn_frame, text="AI-create VOC\nfrom _TXT file", style='SmallDarkPurple.TButton', command=lambda: self.create_vocabulary()).pack(pady=2)
        ttk.Button(vocab_btn_frame, text="SAVE-VOC", style='SmallGreen.TButton', command=self.save_vocabulary).pack(pady=2)
        ttk.Button(vocab_btn_frame, text="Sort-Remove\nDuplicates", style='SmallGoldBrown.TButton', command=self.sort_vocabulary).pack(pady=2)
        ttk.Button(vocab_btn_frame, text="CLR-VOC", style='SmallRed.TButton', command=self.clear_vocabulary).pack(pady=2) # Adjusted from 17, as group padding will handle overall spacing
    # Search button
        ttk.Button(vocab_btn_frame, text="🔍 Search Vocab.", style='SmallBlue.TButton',
                command=self.show_vocabulary_search).pack(side=tk.RIGHT, padx=(0, 5))

    # --- Group 2: Study Text Buttons ---
    # Create a frame for the Study Text buttons
        study_btn_frame = tk.Frame(middle_frame, bg="#222")
        study_btn_frame.pack(pady=(15, 15)) # <--- TOP & BOTTOM PADDING for this GROUP

    # Buttons for Study Text Box - pack into study_btn_frame
        ttk.Button(study_btn_frame, text="LOAD-TXT", style='SmallBlue.TButton', command=self.load_study_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="SAVE-TXT", style='SmallGreen.TButton', command=self.save_study_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="CLR-TXT", style='SmallRed.TButton', command=self.clear_study_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="Translate file", style='SmallDarkPurple.TButton', command=lambda: self.translate_study_text()).pack(pady=2)
        ttk.Button(study_btn_frame, text="Free-Hand\nTranslation", style='SmallLightPurple.TButton', command=self.capture_text).pack(pady=2)
        ttk.Button(study_btn_frame, text="  LISTEN to\nthe Study Text", style='SmallBlue.TButton', command=self.create_listen_functionality).pack(pady=2) # <---- new


    # --- Group 3: Translation Buttons ---
    # Create a frame for the Translation buttons
        translation_btn_frame = tk.Frame(middle_frame, bg="#222")
        translation_btn_frame.pack(pady=(25, 0)) # <--- TOP PADDING for this GROUP

    # Buttons for Translation Box - pack into translation_btn_frame
        ttk.Button(translation_btn_frame, text="LOAD-TRA", style='SmallBlue.TButton', command=self.load_translation).pack(pady=2) # Adjusted from 20
        ttk.Button(translation_btn_frame, text="SAVE-TRA", style='SmallGreen.TButton', command=self.save_translation).pack(pady=2)
        ttk.Button(translation_btn_frame, text="CLR-TRA", style='SmallRed.TButton', command=self.clear_translation).pack(pady=2) # Adjusted from 15
        ttk.Button(translation_btn_frame, text="NOTES", style='SmallGoldBrown.TButton', command=self.add_notes).pack(pady=2) # Adjusted from 15
        
        # --- NEW Group 4: AI Response Buttons (Middle Section) ---
        # Create a separate frame for these 4 buttons
        ai_responses_middle_btn_frame = tk.Frame(middle_frame, bg="#222")
        # Pack this new frame with padding at the top to create separation
        ai_responses_middle_btn_frame.pack(pady=(40, 0)) # <--- Adjust this top padding for desired space

        # Buttons for AI Responses - pack into ai_responses_middle_btn_frame
        ttk.Button(ai_responses_middle_btn_frame, text="Save AI\nResponses", style='SmallDarkPurple.TButton', command=self.save_ai_responses).pack(pady=2)
        ttk.Button(ai_responses_middle_btn_frame, text="Append AI\nResponses", style='SmallDarkPurple.TButton', command=self.append_ai_responses_to_file).pack(pady=2)
        ttk.Button(ai_responses_middle_btn_frame, text="Copy AI \nResponses", style='SmallDarkPurple.TButton', command=self.copy_ai_responses).pack(pady=2)
        ttk.Button(ai_responses_middle_btn_frame, text="Clear AI\nResponses", style='SmallRed.TButton', command=self.clear_ai_responses_textbox).pack(pady=2)
    

    def create_right_section(self):
        right_frame = tk.Frame(self.root, bg="#222")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5) # Added padx=5

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
        ttk.Button(btn_frame2, text="Clear Test", style='SmallOrange.TButton', command=self.find_wrong_read_text_calls).pack(side=tk.LEFT, padx=5)
    

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
        self.answer_entry.bind("<Shift-Return>", self.trigger_next_word_and_refocus) # debuging / refocus entry input
        

        answer_frame = tk.Frame(right_frame, bg="#222")
        answer_frame.pack(fill=tk.X)
        ttk.Button(answer_frame, text="Next Word", style='SmallBlue.TButton', command=self.next_word).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(answer_frame, text="Clear Input", style='SmallOrange.TButton', command=self.clear_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(answer_frame, text="Revise Mistakes", style='SmallGreenish.TButton', command=self.load_revision_file).pack(side=tk.LEFT, padx=5)
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
        self.dictionary_entry.bind("<Return>", self.search_own_vocab)

        dict_btn_frame = tk.Frame(right_frame, bg="#222")
        dict_btn_frame.pack(fill=tk.X)
        ttk.Button(dict_btn_frame, text="AI word translation", style='SmallDarkPurple.TButton', command=self.ai_translate_word).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(dict_btn_frame, text="Langenscheidt", style='SmallGrayBlue.TButton', command=self.fetch_langenscheidt).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(dict_btn_frame, text="Search vocabulary (Current).", style='SmallDarkOlive.TButton', command=self.search_own_vocab).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(dict_btn_frame, text="Clear Input", style='SmallOrange.TButton', command=self.clear_entry).pack(side=tk.LEFT, padx=5)

        # AI Responses to prompts
        self.ai_responses_textbox = self.create_labeled_textbox(right_frame, "AI Responses from prompt on the left side", True, height=11, label_font="Helvetica")


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

    def create_labeled_textbox(self, parent, label_text, scrollbar=True, height=10, label_font="Helvetica", add_buttons=False):
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
                    text="READING Comprehension",
                    style='SmallPurple.TButton',
                    command=self.generate_comprehension_questions
                ).pack(side='left', padx=(20, 3), pady=3)  # Added 20px left padding to position it to the right
            
            if label_text == "Study Text Box:":
                ttk.Button(
                    button_frame,
                    text="LISTENING Comprehension",
                    style='SmallGoldYellow.TButton',
                    command=self.create_listening_comprehension
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
    
    def generate_listening_comprehension_questions(self):
        pass
        

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
# ------------- Added extra blocks of code to automate _TXT and _TRA loading ---
    # def load_vocabulary(self):
    #     filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

    #     if filename.endswith("_VOC.txt") or "_VOC.txt" in filename:
    #         self.current_voc_file = filename  # Save the loaded filename
    #         with open(filename, 'r', encoding='utf-8-sig') as file:
    #             content = file.read()
    #             self.vocabulary_textbox.delete(1.0, tk.END)  # Clear before inserting
    #             self.vocabulary_textbox.insert(tk.END, content)
    #             self.vocabulary = [line.strip() for line in content.splitlines() if line.strip()]
    #             self.load_current_voc += 1
    #             self.load_test_file()
    #     else:
    #         messagebox.showwarning(
    #         "Invalid File Type",
    #         "The selected file is not a vocabulary file.\n\n"
    #         "Please select a file that ends with '_VOC.txt'.\n\n"
    #     )
    #         return
# ------------------ These are the extra blocks of code -------------
    def load_vocabulary(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

        if filename.endswith("_VOC.txt") or "_VOC.txt" in filename:
            self.current_voc_file = filename  # Save the loaded filename
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                self.vocabulary_textbox.delete(1.0, tk.END)  # Clear before inserting
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
                # Extract base filename (everything before _VOC.txt)
                base_name = filename.replace("_VOC.txt", "")
                
                # Construct related filenames
                study_text_file = base_name + "_TXT.txt"
                translation_file = base_name + "_TRA.txt"
                
                # Load Study Text file if it exists
                if os.path.exists(study_text_file):
                    try:
                        with open(study_text_file, 'r', encoding='utf-8-sig') as file:
                            content = file.read()
                            
                            # Extract and display title in label
                            title = self.extract_title_from_text(content)
                            # Update the study text label
                            self.update_study_text_label(title)
                            
                            # Remove title line and insert cleaned content
                            cleaned_content = self.remove_title_line(content)
                            self.study_textbox.delete(1.0, tk.END)
                            self.study_textbox.insert(tk.END, cleaned_content)
                            
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to load study text: {str(e)}")
                else:
                    messagebox.showinfo("File Not Found", f"Study text file not found:\n{study_text_file}")
                
                # Load Translation file if it exists
                if os.path.exists(translation_file):
                    try:
                        with open(translation_file, 'r', encoding='utf-8-sig') as file:
                            content = file.read()
                            
                            # Extract and display title in label
                            title = self.extract_title_from_text(content)
                            # Update the translation label
                            self.update_translation_label(title)
                            
                            # Remove title line and insert cleaned content
                            cleaned_content = self.remove_title_line(content)
                            self.translation_textbox.delete(1.0, tk.END)
                            self.translation_textbox.insert(tk.END, cleaned_content)
                            
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to load translation: {str(e)}")
                else:
                    messagebox.showinfo("File Not Found", f"Translation file not found:\n{translation_file}")
        
        else:
            messagebox.showwarning(
                "Invalid File Type",
                "The selected file is not a vocabulary file.\n\n"
                "Please select a file that ends with '_VOC.txt'.\n\n"
            )
            return
# -------------------- Helper Functions to the above ----------
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
#     
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

        if filename.endswith("_TXT.txt") or "_TXT.txt" in filename:
            self.current_study_file = filename
            with open(filename, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                
                # Extract title
                title = self.extract_title_from_text(content)
                
                # Update the label - search more broadly
                self.update_study_textbox_label(title)
                
                # Remove title line and insert cleaned content
                cleaned_content = self.remove_title_line(content)
                self.study_textbox.delete(1.0, tk.END)
                self.study_textbox.insert(tk.END, cleaned_content)
        
        else:
            messagebox.showwarning(
                "Invalid File Type",
                "The selected file is not a Study Text file.\n\n"
                "Please select a file that ends with '_TXT.txt'.\n\n"
            )
            return
    
    def update_study_textbox_label(self, title):
        """Find and update the study text box label"""
        # Search through all widgets to find the study text label
        def search_widgets(widget):
            if isinstance(widget, tk.Label) and "Study Text Box" in widget.cget('text'):
                widget.config(text=f"Study Text Box: {title}")
                return True
            # Recursively search children
            for child in widget.winfo_children():
                if search_widgets(child):
                    return True
            return False
        
        # Start search from root
        search_widgets(self.root)
        
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
            return '\n'.join(lines[1:])  # Return text without first line
        return text_content  # Return original text if no title line found
        
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

    def check_content_and_warn(self, operation_callback, *args):
        """
        Check if study or translation boxes have content and warn user before proceeding
        with the specified operation.
        
        Args:
            operation_callback: The function to call if user confirms
            *args: Arguments to pass to the operation_callback
        """
        # Check if either textbox has content
        study_content = self.study_textbox.get(1.0, tk.END).strip()
        translation_content = self.translation_textbox.get(1.0, tk.END).strip()
        
        has_content = bool(study_content or translation_content)
        
        if has_content:
            # Create warning message
            message = (
                "Warning: One or both text boxes already contain content:\n\n"
            )
            
            if study_content:
                # Get first 50 chars of study content for preview
                study_preview = study_content[:50] + "..." if len(study_content) > 50 else study_content
                message += f"• Study Box: '{study_preview}'\n"
            
            if translation_content:
                # Get first 50 chars of translation content for preview
                translation_preview = translation_content[:50] + "..." if len(translation_content) > 50 else translation_content
                message += f"• Translation Box: '{translation_preview}'\n\n"
            
            message += "Proceeding may overwrite this content. Continue?"
            
            # Show confirmation dialog
            result = messagebox.askyesno("Content Warning", message, icon="warning")
            
            if not result:
                # User clicked No or Cancel
                self.status_bar.config(text="Operation cancelled")
                return False
        
        # Either no content or user confirmed
        operation_callback(*args)
        return True

    def add_notes(self):
        NotesEditor(self.root)

    def load_translation(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

        if filename.endswith("_TRA.txt") or "_TRA.txt" in filename:
            self.current_translated_file = filename  # Save the loaded filename
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


    def find_wrong_read_text_calls(self):
        """Temporary function to find where read_text is called with wrong arguments"""
        try:
            with open(__file__, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # Look for read_text calls
            lines = content.split('\n')
            found_calls = []
            for i, line in enumerate(lines, 1):
                if 'read_text' in line and ('self.read_text' in line or 'target=self.read_text' in line):
                    found_calls.append((i, line.strip()))
            
            print("=== ALL READ_TEXT CALLS ===")
            for line_num, line_text in found_calls:
                print(f"Line {line_num}: {line_text}")
            print("=== END ===")
            
            return found_calls
            
        except Exception as e:
            print(f"Error reading file: {e}")
            return []

    def clear_translation(self):
        self.current_translated_file = None
        self.translation_textbox.delete(1.0, tk.END)
    

    def search_own_vocab(self, event=None):
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

# ---------------- LARGE BLOCK FOR LISTENING COMPREHENSION ---------------
        
    def create_listening_comprehension(self):
        """Create the listening comprehension popup window with voice selection"""
        listen_comp_window = tk.Toplevel(self.root)
        listen_comp_window.title("Listening Comprehension")
        listen_comp_window.configure(bg="#222")
        listen_comp_window.geometry("400x250")
        listen_comp_window.transient(self.root)
        listen_comp_window.grab_set()
        
        # Center the window
        listen_comp_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (listen_comp_window.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (listen_comp_window.winfo_height() // 2)
        listen_comp_window.geometry(f"+{x}+{y}")
        
        # Create buttons
        frame = tk.Frame(listen_comp_window, bg="#222")
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Voice selection - DEFINE THIS FIRST
        voice_label = tk.Label(frame, text="Select Voice:", bg="#222", fg="white")
        voice_label.pack(anchor=tk.W, pady=(0, 5))
        
        voice_var = tk.StringVar(value="alloy")  # Default voice
        
        voice_frame = tk.Frame(frame, bg="#222")
        voice_frame.pack(fill=tk.X, pady=(0, 15))
        
        voices = [("Alloy", "alloy"), ("Echo", "echo"), ("Fable", "fable"), 
                ("Onyx", "onyx"), ("Nova", "nova"), ("Shimmer", "shimmer")]
        
        for i, (name, value) in enumerate(voices):
            rb = tk.Radiobutton(voice_frame, text=name, variable=voice_var, value=value,
                            bg="#222", fg="white", selectcolor="#444")
            rb.pack(side=tk.LEFT, padx=(0, 10))

        # Set button states for the entire listening session
        if hasattr(self, 'eval_answer_btn'):
            self.eval_answer_btn.config(state="normal")
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state="disabled")

        # ------------- NEW CODE FROM HERE ------
        # ------------- CORRECTED CODE FROM HERE ------
        tk.Label(frame, text="Select a text file for listening comprehension:", 
            bg="#222", fg="white").pack(pady=20)

        btn_frame = tk.Frame(frame, bg="#222")
        btn_frame.pack(pady=20)

        def on_cancel():
            """Re-enable Prompt AI button and close window"""
            if hasattr(self, 'prompt_ai_button'):
                self.prompt_ai_button.config(state="normal")
            listen_comp_window.destroy()  # Fixed variable name
        
        def on_file_select():
            # Only proceed if user actually selects a file
            filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            if filename:
                # Process the file and start listening comprehension
                # Call your existing function that processes the file
                self.start_listening_from_file(listen_comp_window, voice_var.get(), filename)
            else:
                # If user cancels file selection, re-enable Prompt AI button
                if hasattr(self, 'prompt_ai_button'):
                    self.prompt_ai_button.config(state="normal")
                listen_comp_window.destroy()

        ttk.Button(btn_frame, text="Select Text File", 
                command=on_file_select).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", 
                command=on_cancel).pack(side=tk.LEFT, padx=10)
        
        # Also handle window close (X button)
        def on_window_close():
            if hasattr(self, 'prompt_ai_button'):
                self.prompt_ai_button.config(state="normal")
            listen_comp_window.destroy()  # Fixed variable name
        
        listen_comp_window.protocol("WM_DELETE_WINDOW", on_window_close)  # Fixed variable name
            
        # Reset evaluation tracking for new session
        self.evaluated_questions = set()
        
        # Create buttons - use a different approach to get the voice value
        # ttk.Button(frame, text="Load German Text File", 
        #         style='SmallBlue.TButton',
        #         command=lambda: self.start_listening_from_file(listen_comp_window, voice_var.get())).pack(pady=5, fill=tk.X)
        
        # ttk.Button(frame, text="Search Internet for German Text", 
        #         style='SmallGreen.TButton',
        #         command=lambda: self.search_german_text(listen_comp_window, voice_var.get())).pack(pady=5, fill=tk.X)
        
        # ttk.Button(frame, text="Cancel", 
        #         style='SmallRed.TButton',
        #         command=listen_comp_window.destroy).pack(pady=5, fill=tk.X)
    

    def use_study_text_for_comprehension(self, parent_window):
        """Use the Study Text Box content for listening comprehension"""
        study_text = self.study_textbox.get(1.0, tk.END).strip()
        
        if not study_text:
            messagebox.showwarning("No Text", "Study Text Box is empty.")
            return
        
        self.listening_comprehension_text = study_text
        parent_window.destroy()
        self.generate_listening_questions()


    def ensure_prompt_ai_enabled(self):
        """Safety function to ensure Prompt AI button is always enabled"""
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state=tk.NORMAL)
    

    def start_listening_from_file(self, parent_window, voice="alloy"):
        """Start listening comprehension from a selected German text file and play it aloud."""
        filename = filedialog.askopenfilename(
            title="Select German Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                self.listening_comprehension_text = file.read()

            parent_window.destroy()
            self.current_voice = voice  # Store selected voice

            # Show reading controls FIRST
            self.show_reading_controls(
                self.listening_comprehension_text, 
                f"File: {os.path.basename(filename)}", 
                voice
            )

        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")


    def speak_text_with_tts(self, text, voice="alloy"):
        """Generate and play speech from text using OpenAI TTS safely, even for long input."""
        import re, tempfile, os, time, pygame
        from openai import OpenAI

        client = OpenAI()

        # --- Split text into safe chunks (~400 chars each, on sentence boundaries)
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        chunks = []
        current = ""
        for s in sentences:
            if len(current) + len(s) < 400:
                current += " " + s
            else:
                chunks.append(current.strip())
                current = s
        if current:
            chunks.append(current.strip())

        pygame.mixer.init()

        try:
            for chunk in chunks:
                # Create temp MP3 file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    temp_path = tmp.name

                # Generate and save speech
                with client.audio.speech.with_streaming_response.create(
                    model="gpt-4o-mini-tts",
                    voice=voice,
                    input=chunk
                ) as response:
                    response.stream_to_file(temp_path)

                # Play the MP3
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()

                # Wait until finished
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                # Stop music and safely delete file
                pygame.mixer.music.unload()
                try:
                    os.remove(temp_path)
                    print(f"Cleaned up {temp_path}")
                except PermissionError:
                    print(f"Could not delete {temp_path}, will retry later")

        except Exception as e:
            print(f"TTS playback error: {e}")

        finally:
            pygame.mixer.quit()



    
    def search_german_text(self, parent_window, voice):
        """Search for a German text online"""
        try:
            # Common German news and content websites
            sources = [
                "https://www.dw.com/de/themen/s-9077",
                "https://www.tagesschau.de/",
                "https://www.spiegel.de/thema/aktuelles/",
                "https://www.zeit.de/aktuelles",
                "https://www.giz.de/de/regionen?r=africa",
                "https://www.giz.de/de/regionen?r=asia",
                "https://www.giz.de/de/regionen?r=europe",
                "https://www.giz.de/de/regionen?r=southamerica"
            ]
            
            source = random.choice(sources)
            response = requests.get(source, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text from paragraphs
            paragraphs = soup.find_all('p')
            german_text = ""
            
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 50:  # Only take substantial paragraphs
                    german_text += text + " "
                    if len(german_text.split()) > 150:  # Target length
                        break
            
            if not german_text or len(german_text.split()) < 50:
                # Fallback: Use AI to generate text if web scraping fails
                german_text = self.generate_german_text_with_ai()
            
            self.listening_comprehension_text = german_text[:2000]  # Limit length
            parent_window.destroy()
            
            # Show reading window first, then offer comprehension questions
            self.show_listening_comprehension_reading_window()

            self.current_voice = voice  # Store the selected voice
            parent_window.destroy()
            # self.generate_listening_questions()

            # self.current_voice = voice  # Store the selected voice
            # parent_window.destroy()
            
            # SHOW READING POPUP FIRST instead of directly generating questions
            self.show_listening_text_reading_controls()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch German text: {e}")
    

    def show_listening_comprehension_reading_window(self):
        """Show the reading window for listening comprehension text"""
        # Create controls window similar to create_listen_functionality
        controls_window = tk.Toplevel(self.root)
        controls_window.title("Listen to German Text")
        controls_window.configure(bg="#222")
        controls_window.geometry("500x250")  # Wider to accommodate new button
        controls_window.transient(self.root)
        
        # Make window stay on top
        controls_window.attributes('-topmost', True)
        
        # Center the window
        controls_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (controls_window.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (controls_window.winfo_height() // 2)
        controls_window.geometry(f"+{x}+{y}")
        
        # Content frame
        content_frame = tk.Frame(controls_window, bg="#222")
        content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Source label
        source_label = tk.Label(content_frame, text="Listen to the German text first, then answer questions", 
                            bg="#222", fg="white", font=("Helvetica", 10, "bold"))
        source_label.pack(pady=(0, 10))
        
        # Status label
        status_label = tk.Label(content_frame, text="Ready to read", 
                            bg="#222", fg="lightgreen", font=("Helvetica", 9))
        status_label.pack(pady=(0, 10))
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(content_frame, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, pady=(0, 15))
        
        # Control buttons frame
        button_frame = tk.Frame(content_frame, bg="#222")
        button_frame.pack(fill=tk.X)
        
        # Control buttons - using the robust reading functionality
        play_button = ttk.Button(button_frame, text="Start Reading", 
                                style='SmallGreen.TButton',
                                command=lambda: self.toggle_reading_listening_comprehension(
                                    self.listening_comprehension_text, play_button, pause_button, 
                                    status_label, progress_var, generate_button))
        play_button.pack(side=tk.LEFT, padx=(0, 10))
        
        pause_button = ttk.Button(button_frame, text="Pause", 
                                style='SmallGoldBrown.TButton',
                                command=lambda: self.toggle_pause(pause_button, status_label),
                                state=tk.DISABLED)
        pause_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # NEW: Generate Questions button
        generate_button = ttk.Button(button_frame, text="Generate Questions", 
                                    style='SmallDarkPurple.TButton',
                                    command=lambda: self.generate_listening_questions_after_reading(controls_window),
                                    state=tk.NORMAL)
        generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        stop_button = ttk.Button(button_frame, text="Close", 
                                style='SmallRed.TButton',
                                command=controls_window.destroy)
        stop_button.pack(side=tk.LEFT)
        
        # Store references
        self.current_controls_window = controls_window
    

    def toggle_reading_listening_comprehension(self, text_content, play_button, pause_button, status_label, progress_var, generate_button):
        """Start or resume reading"""
        if not self.is_reading:
            # Start reading
            self.is_reading = True
            self.reading_paused = False
            play_button.config(state=tk.DISABLED)
            pause_button.config(state=tk.NORMAL)
            status_label.config(text="Reading...", fg="lightgreen")
            
            # Reset progress bar
            progress_var.set(0)
            
            # Start reading in a separate thread - use the unified read_text
            self.reading_thread = threading.Thread(
                target=self.read_text, 
                args=(text_content, status_label, progress_var, play_button, pause_button),
                daemon=True
            )
            self.reading_thread.start()
        elif self.reading_paused:
            # Resume reading
            self.reading_paused = False
            pygame.mixer.music.unpause()
            pause_button.config(text="Pause")
            status_label.config(text="Reading...", fg="lightgreen")
    

    def generate_listening_questions_after_reading(self, parent_window):
        """Generate questions after the user has listened to the text"""
        parent_window.destroy()
        self.generate_listening_questions()
    
    def generate_german_text_with_ai(self):
        """Generate German text using OpenAI as fallback"""
        try:
            themes = [
                "Umwelt und Naturschutz in Deutschland",
                "Alltagsleben in einer deutschen Stadt", 
                "Deutsche Geschichte und Kultur",
                "Sport und Freizeitaktivitäten",
                "Wissenschaft und Technologie",
                "Philosophie und Psychologie im modernen Leben",
                "Kurze Geschichte oder Märchen",
                "Politische Themen in Europa"
            ]
            
            theme = random.choice(themes)
            
            prompt = f"""
            Schreibe einen deutschen Text von 70-150 Wörtern zum Thema: {theme}.
            Der Text sollte für Deutschlernende geeignet sein, aber nicht zu einfach.
            Verwende korrekte Grammatik und einen klaren Aufbau.
            Der Text sollte selbstständig verständlich sein.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Final fallback: pre-written text
            return self.get_fallback_german_text()
    
    
    def get_fallback_german_text(self):
        """Provide a fallback German text"""
        fallback_texts = [
            "In Deutschland spielt Umweltschutz eine große Rolle. Viele Menschen trennen ihren Müll sorgfältig und nutzen öffentliche Verkehrsmittel. Die erneuerbaren Energien wie Wind- und Solarkraft werden immer wichtiger. In den Städten sieht man viele Fahrradfahrer, die umweltfreundlich unterwegs sind. Der Schutz der Natur ist den Deutschen sehr wichtig, deshalb gibt es viele Naturschutzgebiete. Jeder kann durch kleine Veränderungen im Alltag zum Umweltschutz beitragen.",
            "Das deutsche Schulsystem beginnt mit der Grundschule. Danach gehen Schüler auf verschiedene weiterführende Schulen wie Gymnasium, Realschule oder Hauptschule. Die Ausbildung ist in Deutschland sehr praxisorientiert. Viele junge Menschen machen eine Lehre in einem Betrieb. Die Universitäten bieten akademische Bildung und forschen in vielen Bereichen. Bildung hat in Deutschland einen hohen Stellenwert und ist meist kostenlos.",
            "Berlin ist die Hauptstadt von Deutschland und eine sehr vielfältige Stadt. Hier leben Menschen aus vielen verschiedenen Kulturen zusammen. Die Stadt hat eine reiche Geschichte, die man an vielen Orten sehen kann. Das Brandenburger Tor und die Berliner Mauer sind bekannte Sehenswürdigkeiten. Berlin ist auch für seine Kunstszene und sein Nachtleben berühmt. Jedes Jahr besuchen Millionen Touristen diese lebendige Stadt."
        ]
        return random.choice(fallback_texts)
    
    def generate_listening_questions(self):
        """Generate comprehension questions based on the German text"""
        try:
            # Save the text to a file for later review
            self.save_listening_text()
            
            prompt = f"""
            Basierend auf dem folgenden deutschen Text, erstelle 3-5 Verständnisfragen auf Deutsch.
            Die Fragen sollten das Hörverständnis testen und für Deutschlernende geeignet sein.
            
            WICHTIG: Gib die Fragen in einem sehr spezifischen Format zurück:
            
            FRAGE 1: [Hier kommt die erste Frage]
            FRAGE 2: [Hier kommt die zweite Frage]
            FRAGE 3: [Hier kommt die dritte Frage]
            
            Text:
            {self.listening_comprehension_text}
            
            Stelle sicher, dass jede Frage mit "FRAGE X:" beginnt und keine zusätzlichen Erklärungen enthält.
            Die Fragen sollten unterschiedliche Aspekte des Textes abdecken.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            
            questions_text = response.choices[0].message.content.strip()
            self.parse_questions(questions_text)
            self.start_listening_session()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate questions: {e}")
    
    
    
    def start_reading_for_comprehension(self, text, reading_window, status_label, progress_var):
        """Start reading the text for comprehension"""
        threading.Thread(
            target=self.read_text_for_comprehension,
            args=(text, reading_window, status_label, progress_var),
            daemon=True
        ).start()
    
    def read_text_for_comprehension(self, text_content):
        """Specialized read_text for comprehension questions without UI elements"""
        try:
            # Simple TTS for comprehension questions
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_file = temp_audio.name
            
            tts = gTTS(text=text_content, lang='de', slow=False)
            tts.save(temp_file)
            
            # Stop any current playback
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
        except Exception as e:
            print(f"TTS error in comprehension: {e}")
    
    def skip_to_questions(self, reading_window):
        """Skip the reading and go directly to questions"""
        reading_window.destroy()
        self.generate_questions_after_reading()

# ------ Started adding revised blocks of code -------



    def generate_questions_after_reading(self):
        """Generate questions after the text has been read"""
        try:
            # Show generating message
            messagebox.showinfo("Generating Questions", "The text has been read. Now generating comprehension questions...")
            
            prompt = f"""
            Basierend auf dem folgenden deutschen Text, erstelle 3-5 Verständnisfragen auf Deutsch.
            Die Fragen sollten das Hörverständnis testen und für Deutschlernende geeignet sein.
            
            WICHTIG: Gib die Fragen in einem sehr spezifischen Format zurück:
            
            FRAGE 1: [Hier kommt die erste Frage]
            FRAGE 2: [Hier kommt die zweite Frage]
            FRAGE 3: [Hier kommt die dritte Frage]
            
            Text:
            {self.listening_comprehension_text}
            
            Stelle sicher, dass jede Frage mit "FRAGE X:" beginnt und keine zusätzlichen Erklärungen enthält.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            
            questions_text = response.choices[0].message.content.strip()
            print(f"Generated questions: {questions_text}")  # Debug print
            
            self.parse_questions(questions_text)
            
            # Start the listening session
            self.start_listening_session()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate questions: {e}")
            print(f"Question generation error: {e}")

    def start_listening_session(self):
        """Start the listening comprehension session"""
        # Reset evaluation tracking
        self.evaluated_questions = set()
        
        # Disable Prompt AI button
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state=tk.DISABLED)
            # ------- FINISH DISABLE BUTTON ---------------

        print(f"Starting listening session with {len(self.current_questions)} questions")  # Debug
        
        if not self.current_questions:
            messagebox.showwarning("No Questions", "No questions were generated.")
            print("No questions available")  # Debug
            return
        
        # Create listening session window
        session_window = tk.Toplevel(self.root)
        session_window.title("Listening Comprehension Session")
        session_window.configure(bg="#222")
        session_window.geometry("500x300")
        session_window.transient(self.root)
        
        # Center the window
        session_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (session_window.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (session_window.winfo_height() // 2)
        session_window.geometry(f"+{x}+{y}")
        
        # Make sure window stays on top
        session_window.attributes('-topmost', True)
        
        print("Session window created")  # Debug
        
        # Content frame
        content_frame = tk.Frame(session_window, bg="#222")
        content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Question display
        question_label = tk.Label(content_frame, text="Current Question:", 
                                bg="#222", fg="white", font=("Helvetica", 10, "bold"))
        question_label.pack(anchor=tk.W, pady=(0, 5))
        
        question_text = tk.Text(content_frame, height=4, width=50, wrap=tk.WORD,
                            bg="#333", fg="white", font=("Helvetica", 9))
        question_text.pack(fill=tk.X, pady=(0, 15))
        question_text.config(state=tk.NORMAL)
        
        # Progress label
        progress_label = tk.Label(content_frame, text="", 
                                bg="#222", fg="lightblue", font=("Helvetica", 9))
        progress_label.pack(pady=(0, 10))
        
        # Score label
        score_label = tk.Label(content_frame, text="Score: 0/0", 
                            bg="#222", fg="lightgreen", font=("Helvetica", 9, "bold"))
        score_label.pack(pady=(0, 15))
        
        # Control buttons frame
        button_frame = tk.Frame(content_frame, bg="#222")
        button_frame.pack(fill=tk.X)
        
        # Control buttons
        repeat_button = ttk.Button(button_frame, text="Repeat Question", 
                                style='SmallBlue.TButton',
                                command=lambda: self.speak_current_question())
        repeat_button.pack(side=tk.LEFT, padx=(0, 10))
        
        next_button = ttk.Button(button_frame, text="Next Question", 
                        style='SmallGreen.TButton',
                        command=lambda: self.next_listening_question(session_window))
        next_button.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_button = ttk.Button(button_frame, text="Exit", 
                        style='SmallRed.TButton',
                        command=lambda: self.stop_listening_session(session_window))
        
        exit_button.pack(side=tk.LEFT)
        
        # Store references
        self.current_session_window = session_window
        self.current_question_text = question_text
        self.current_progress_label = progress_label
        self.current_score_label = score_label
        
        print("About to display first question")  # Debug
        
        # Display first question
        self.display_current_question()
        
        print("First question displayed")  # Debug


    def finish_listening_session(self):
        """Display final score and session summary"""
        # Re-enable Prompt AI button
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state=tk.NORMAL)
        
        final_score = f"""
    Listening Comprehension Session Completed!
    Final Score: {self.listening_score}/{self.total_listening_questions * 5}
    Percentage: {(self.listening_score / (self.total_listening_questions * 5)) * 100:.1f}%
    """
        self.ai_responses_textbox.insert(tk.END, final_score)
        self.ai_responses_textbox.see(tk.END)
        
        messagebox.showinfo("Session Complete", 
                        f"Listening comprehension session completed!\n"
                        f"Final score: {self.listening_score}/{self.total_listening_questions * 5}")
        
    def stop_listening_session(self, session_window):
        """Stop the listening session early (when user clicks Exit) - ADD THIS NEW FUNCTION"""
        # Re-enable Prompt AI button
        if hasattr(self, 'prompt_ai_button'):
            self.prompt_ai_button.config(state=tk.NORMAL)
        
        # Stop any current speech
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Clear session state
        self.is_reading = False
        self.reading_paused = False
        
        # Close session window if it exists
        if session_window and session_window.winfo_exists():
            session_window.destroy()
        
        # Clear references
        if hasattr(self, 'current_session_window'):
            del self.current_session_window
        if hasattr(self, 'current_questions'):
            self.current_questions = []
        if hasattr(self, 'evaluated_questions'):
            self.evaluated_questions = set()
        
        print("Listening session stopped and cleaned up")

    def display_current_question(self):
        """Display the current question and speak it"""
        if self.current_question_index < len(self.current_questions):
            question = self.current_questions[self.current_question_index]
            self.current_question_text.delete(1.0, tk.END)
            self.current_question_text.insert(tk.END, question)
            
            # Update progress
            progress_text = f"Question {self.current_question_index + 1} of {len(self.current_questions)}"
            self.current_progress_label.config(text=progress_text)
            
            # Update score
            score_text = f"Score: {self.listening_score}/{self.current_question_index}"
            self.current_score_label.config(text=score_text)
            
            # Speak the question
            self.speak_current_question()
        else:
            self.finish_listening_session()

    def speak_current_question(self):
        """Speak the current question using TTS"""
        if self.current_question_index < len(self.current_questions):
            question = self.current_questions[self.current_question_index]
            
            # Stop any current speech first
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.time.wait(200)  # Wait for stop to complete
            
            # Use the selected voice
            voice = getattr(self, 'current_voice', 'alloy')
            
            # Speak in a new thread
            threading.Thread(
                target=self.speak_text, 
                args=(question, voice),
                daemon=True
            ).start()

    def speak_text(self, text, voice="alloy", window=None):
        """Speak text using TTS - simplified version for questions and general use"""
        try:
            # Set speech playing flag
            self.speech_playing = True
            
            # Ensure pygame mixer is initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Use OpenAI TTS
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                audio_file = temp_audio.name
            
            try:
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                )
                # FIX: Use write_to_file instead of stream_to_file
                response.write_to_file(audio_file)
            except Exception as e:
                # Fallback to gTTS if OpenAI fails
                print(f"OpenAI TTS failed, using gTTS: {e}")
                tts = gTTS(text=text, lang='de', slow=False)
                tts.save(audio_file)
            
            # Stop any current playback
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.time.wait(100)
            
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish in a non-blocking way
            def wait_for_playback():
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                
                # Clean up with safe method
                self.safe_cleanup_audio_file(audio_file)
                
                # Reset speech playing flag and re-enable window
                self.speech_playing = False
                if window and window.winfo_exists():
                    window.attributes('-disabled', False)
                    # Show completion message if window still exists
                    try:
                        messagebox.showinfo("Playback Complete", "Text reading finished.")
                    except:
                        pass  # Window might be closed
            
            # Use threading to avoid blocking the GUI
            import threading
            playback_thread = threading.Thread(target=wait_for_playback)
            playback_thread.daemon = True
            playback_thread.start()
                
        except Exception as e:
            print(f"TTS error: {e}")
            # Reset speech playing flag and re-enable window on error
            self.speech_playing = False
            if window and window.winfo_exists():
                window.attributes('-disabled', False)
            messagebox.showerror("TTS Error", f"Failed to generate speech: {str(e)}")

    def safe_delete_file(self, filepath):
        """Safely delete a file with retries and error handling"""
        if not filepath or not os.path.exists(filepath):
            return
            
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Try to close any pygame resources first
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                
                # Small delay before attempting deletion
                pygame.time.wait(100 * (attempt + 1))  # Increasing delay
                
                os.unlink(filepath)
                return  # Success!
                
            except PermissionError:
                if attempt < max_retries - 1:
                    # Try to force pygame to release the file
                    try:
                        pygame.mixer.music.stop()
                        pygame.mixer.quit()
                        pygame.mixer.init()  # Reinitialize mixer
                    except:
                        pass
                    continue
                else:
                    print(f"Could not delete audio file {filepath} after {max_retries} attempts")
                    # Don't show error to user for cleanup failures
            except Exception as e:
                print(f"Error deleting file {filepath}: {e}")
                break
    
    def parse_questions(self, questions_text):
        """Parse the questions from the AI response"""
        try:
            questions = []
            lines = questions_text.split('\n')
            
            for line in lines:
                line = line.strip()
                # More flexible parsing to handle different formats
                if line.startswith('FRAGE') and (':' in line or '.' in line):
                    # Handle both "FRAGE 1:" and "FRAGE 1." formats
                    if ':' in line:
                        question = line.split(':', 1)[1].strip()
                    else:
                        question = line.split('.', 1)[1].strip()
                    
                    if question:  # Only add non-empty questions
                        questions.append(question)
            
            # If no questions were found with the expected format, try alternative parsing
            if not questions:
                # Split by numbers or bullet points
                import re
                question_pattern = r'^(?:\d+\.\s*|FRAGE\s*\d+\s*[:.]\s*)(.+)$'
                for line in lines:
                    match = re.match(question_pattern, line.strip(), re.IGNORECASE)
                    if match:
                        questions.append(match.group(1).strip())
            
            # If still no questions, use the entire text as one question
            if not questions:
                questions = ["Was ist die Hauptidee des Textes?"]
            
            self.current_questions = questions
            self.total_listening_questions = len(questions)
            self.current_question_index = 0
            self.listening_score = 0
            
            print(f"Parsed {len(questions)} questions: {questions}")  # Debug print
            
        except Exception as e:
            print(f"Error parsing questions: {e}")
            # Fallback questions
            self.current_questions = [
                "Was ist die Hauptidee des Textes?",
                "Welche wichtigen Informationen wurden erwähnt?",
                "Was können Sie über das Thema sagen?"
            ]
            self.total_listening_questions = len(self.current_questions)
            self.current_question_index = 0
            self.listening_score = 0
    
    def save_listening_text(self):
        """Save the listening text to the list_compr_files folder"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Make sure directory exists
            if not hasattr(self, 'listening_dir'):
                self.listening_dir = "list_compr_files"
            os.makedirs(self.listening_dir, exist_ok=True)
            
            filename = os.path.join(self.listening_dir, f"listening_text_{timestamp}.txt")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.listening_comprehension_text)
            
            messagebox.showinfo("Text Saved", f"German text saved to {filename} for later review.")
            return f"list_compr_files/listening_text_{timestamp}.txt"
            
        except Exception as e:
            print(f"Could not save listening text: {e}")
            return "Unknown source"
    
    def search_german_text(self, parent_window, voice):
        """Search for a German text online"""
        try:
            # Common German news and content websites
            sources = [
                "https://www.dw.com/de/themen/s-9077",
                "https://www.tagesschau.de/",
                "https://www.spiegel.de/thema/aktuelles/",
                "https://www.zeit.de/aktuelles"
                "https://www.giz.de/de/regionen?r=africa",
                "https://www.giz.de/de/regionen?r=asia",
                "https://www.giz.de/de/regionen?r=europe",
                "https://www.giz.de/de/regionen?r=southamerica"
            ]
            
            source = random.choice(sources)
            response = requests.get(source, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text from paragraphs
            paragraphs = soup.find_all('p')
            german_text = ""
            
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 50:  # Only take substantial paragraphs
                    german_text += text + " "
                    if len(german_text.split()) > 150:  # Target length
                        break
            
            if not german_text or len(german_text.split()) < 50:
                # Fallback: Use AI to generate text if web scraping fails
                german_text = self.generate_german_text_with_ai()
            
            self.listening_comprehension_text = german_text[:2000]  # Limit length
            parent_window.destroy()
            self.current_voice = voice  # Store the selected voice
            
            # Save the text FIRST
            self.save_listening_text()
            
            # THEN show reading controls (same as file loading)
            self.show_reading_controls(
                self.listening_comprehension_text, 
                "Internet German Text", 
                voice
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch German text: {e}")
    
    def evaluate_answer(self, user_answer):
        """Evaluate the user's answer using AI with context of the original text"""
        try:
            current_question = self.current_questions[self.current_question_index]
            
            prompt = f"""
                Evaluate the following response to the question. The answer should be factually correct, grammatically accurate, \
                    and in complete sentences in German.

                FRAGE: {current_question}
                ANTWORD DES LERNENDEN: {user_answer}

                Evaluation criteria:
                1. Factual accuracy (0-2 points)
                2. Linguistic appropriateness and completeness (0-1 point) 
                3. Grammar and syntax (0-1 point)
                4. Vocabulary and expression (0-1 point)

                Maximum score: 5 points per question.

                IF the answer contains grammatical or syntactical errors, you MUST return a corrected version. Only if the \
                    user's answer is grammatically and syntactically correct should you leave KORREKTUR empty.

                Return your evaluation in this format:
                PUNKTE: [Score]/5
                KOMMENTAR: [Your constructive feedback in German]
                KORREKTUR: [Provide a grammatically corrected version of the user's answer if errors were present, \
                    otherwise leave empty]
                """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            
            evaluation = response.choices[0].message.content.strip()
            self.process_evaluation(evaluation, user_answer)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not evaluate answer: {e}")
    
    def process_evaluation(self, evaluation, user_answer):
        """Process the AI evaluation and update score - show only evaluation"""
        try:
            lines = evaluation.split('\n')
            points = 0
            comment = ""
            evaluation_found = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('PUNKTE:'):
                    points_text = line.split(':')[1].strip()
                    points = int(points_text.split('/')[0])
                    evaluation_found = True
                elif line.startswith('KOMMENTAR:'):
                    comment = line.split(':', 1)[1].strip()
                    evaluation_found = True
                elif line.startswith('Question') or line.startswith('Your answer') or line.startswith('Score') or line.startswith('Feedback'):
                    evaluation_found = True
            
            # Only update score and display if we found evaluation content
            if evaluation_found:
                # Update score
                self.listening_score += points
                
                # Display ONLY the evaluation in AI responses textbox
                evaluation_text = f"""
                    Question {self.current_question_index + 1}: {self.current_questions[self.current_question_index]}
                    Your answer: {user_answer}
                    Score: {points}/5
                    Feedback: {comment}
                    {'-'*50}
                    """
                self.ai_responses_textbox.insert(tk.END, evaluation_text)
                self.ai_responses_textbox.see(tk.END)
            else:
                # If no evaluation format found, show raw response but indicate it's the full response
                self.ai_responses_textbox.insert(tk.END, f"\nFull AI Response:\n{evaluation}\n{'-'*50}\n")
                self.ai_responses_textbox.see(tk.END)
                
        except Exception as e:
            print(f"Error processing evaluation: {e}")
            # Show error message
            self.ai_responses_textbox.insert(tk.END, f"\nError processing evaluation: {e}\n{'-'*50}\n")
            self.ai_responses_textbox.see(tk.END)
    
    def next_listening_question(self, session_window):
        """Move to the next question"""
        if self.current_question_index >= len(self.current_questions):
            self.finish_listening_session()
            return
        
        # Get user's answer
        user_answer = self.input_textbox.get(1.0, tk.END).strip()
        
        # Only evaluate if not already evaluated and answer exists
        current_q_index = self.current_question_index
        if user_answer and current_q_index not in self.evaluated_questions:
            if len(user_answer.split()) >= 3:
                self.evaluate_answer(user_answer)
                self.evaluated_questions.add(current_q_index)
            else:
                messagebox.showwarning("Short Answer", "Please provide a more detailed answer (at least 3 words) or clear the box to proceed.")
                return
        
        # Clear input and move to next question
        self.input_textbox.delete(1.0, tk.END)
        self.current_question_index += 1
        
        if self.current_question_index < len(self.current_questions):
            self.display_current_question()
        else:
            self.finish_listening_session()
            session_window.destroy()

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