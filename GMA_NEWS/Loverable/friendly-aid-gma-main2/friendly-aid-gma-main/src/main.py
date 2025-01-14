import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import customtkinter as ctk
from tkinter import scrolledtext

class AIResearchTool:
    def __init__(self):
        self.root = ThemedTk(theme="arc")  # Modern looking theme
        self.root.title("AI Assisted Research Tool")
        self.root.geometry("1200x800")
        
        # Configure colors and styles
        self.bg_color = "#ffffff"
        self.accent_color = "#646cff"
        self.root.configure(bg=self.bg_color)
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=20, fill='x')
        
        ttk.Label(
            header_frame, 
            text="AI Assisted Research Tool",
            font=('Helvetica', 24, 'bold')
        ).pack()
        
        ttk.Label(
            header_frame,
            text="Analyze regulatory compliance with advanced AI",
            font=('Helvetica', 12)
        ).pack()

        # Input Section
        input_card = ttk.LabelFrame(self.root, text="Research Parameters")
        input_card.pack(padx=20, pady=10, fill='x')

        # Topic Input
        topic_frame = ttk.Frame(input_card)
        topic_frame.pack(padx=10, pady=5, fill='x')
        ttk.Label(topic_frame, text="Topic").pack(anchor='w')
        self.topic_entry = ttk.Entry(topic_frame)
        self.topic_entry.pack(fill='x')

        # URL Input
        url_frame = ttk.Frame(input_card)
        url_frame.pack(padx=10, pady=5, fill='x')
        ttk.Label(url_frame, text="URL").pack(anchor='w')
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(fill='x')

        # Buttons
        button_frame = ttk.Frame(input_card)
        button_frame.pack(padx=10, pady=10, fill='x')
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear",
            command=self.clear_inputs,
            fg_color="transparent",
            border_width=1
        )
        clear_btn.pack(side='right', padx=5)
        
        analyze_btn = ctk.CTkButton(
            button_frame,
            text="Analyze",
            command=self.analyze
        )
        analyze_btn.pack(side='right', padx=5)

        # Analysis Results Section
        results_card = ttk.LabelFrame(self.root, text="Analysis Results")
        results_card.pack(padx=20, pady=10, fill='both', expand=True)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_card)
        self.notebook.pack(padx=10, pady=5, fill='both', expand=True)

        # Create tabs for each attribute
        attributes = [
            "Title", "Summary", "Affected Products", "Summary Details",
            "Conformity Assessment", "Marking Requirement", "Technical Requirement",
            "Publish Date", "Effective Date", "Mandatory Date", "Consultation Closing"
        ]

        for attr in attributes:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=attr)
            
            # Add content to each tab
            self.create_tab_content(tab)

    def create_tab_content(self, tab):
        # LLM Prompt
        ttk.Label(tab, text="LLM Prompt").pack(anchor='w', padx=10, pady=2)
        prompt_text = scrolledtext.ScrolledText(tab, height=3)
        prompt_text.pack(fill='x', padx=10, pady=2)
        prompt_text.configure(state='disabled')

        # AI Generated Analysis
        ttk.Label(tab, text="AI Generated Analysis").pack(anchor='w', padx=10, pady=2)
        ai_analysis = scrolledtext.ScrolledText(tab, height=4)
        ai_analysis.pack(fill='x', padx=10, pady=2)

        # Expert Analysis
        ttk.Label(tab, text="Expert Analysis").pack(anchor='w', padx=10, pady=2)
        expert_analysis = scrolledtext.ScrolledText(tab, height=4)
        expert_analysis.pack(fill='x', padx=10, pady=2)

        # Feedback and Accuracy
        feedback_frame = ttk.Frame(tab)
        feedback_frame.pack(fill='x', padx=10, pady=5)

        # Feedback
        feedback_left = ttk.Frame(feedback_frame)
        feedback_left.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Label(feedback_left, text="Feedback").pack(anchor='w')
        ttk.Entry(feedback_left).pack(fill='x')

        # Accuracy
        feedback_right = ttk.Frame(feedback_frame)
        feedback_right.pack(side='left', fill='x', expand=True, padx=5)
        ttk.Label(feedback_right, text="Accuracy (%)").pack(anchor='w')
        ttk.Entry(feedback_right).pack(fill='x')

    def clear_inputs(self):
        self.topic_entry.delete(0, tk.END)
        self.url_entry.delete(0, tk.END)

    def analyze(self):
        # Here you would implement the analysis logic
        # For now, we'll just show a message
        tk.messagebox.showinfo("Processing", "Analyzing content...")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AIResearchTool()
    app.run()