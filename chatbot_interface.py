import tkinter as tk
from tkinter import ttk, scrolledtext, Frame
from tkinter.font import Font
import pandas as pd
from PIL import Image, ImageTk
import os

class ChatbotApp:
    def __init__(self, master):
        self.master = master
        master.title("Global Compliance Management")
        
        # Configure the window
        master.configure(bg='#FFFFFF')
        master.geometry("1200x800")
        
        # Create main styles
        self.style = ttk.Style()
        self.style.configure('Header.TFrame', background='#FFFFFF')  # Changed to white
        self.style.configure('Content.TFrame', background='#FFFFFF')
        self.style.configure('Button.TButton', 
                           background='#CC0000',
                           foreground='white',
                           padding=10)
        
        # Header Frame
        self.header_frame = ttk.Frame(master, style='Header.TFrame', height=60)
        self.header_frame.pack(fill='x', side='top')
        
        # Header Title
        self.title_label = tk.Label(self.header_frame, 
                                  text="Compliance Portfolio",
                                  font=('Segoe UI', 24, 'bold'),
                                  fg='#CC0000',  # Changed text color to UL Red
                                  bg='#FFFFFF')  # Changed to white
        self.title_label.pack(side='left', padx=20, pady=10)
        
        # Main Content Frame
        self.content_frame = ttk.Frame(master, style='Content.TFrame')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left Panel - Categories
        self.left_panel = ttk.Frame(self.content_frame)
        self.left_panel.pack(side='left', fill='y', padx=(0, 20))
        
        self.category_label = tk.Label(self.left_panel,
                                     text="Regulatory Categories",
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='#FFFFFF')
        self.category_label.pack(pady=(0, 10))
        
        self.category_list = tk.Listbox(self.left_panel,
                                      font=('Segoe UI', 10),
                                      width=30,
                                      height=15,
                                      selectmode='single',
                                      bd=0,
                                      highlightthickness=1)
        self.category_list.pack(fill='y', expand=True)
        self.category_list.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Chat Area Frame
        self.chat_frame = ttk.Frame(self.content_frame)
        self.chat_frame.pack(side='right', fill='both', expand=True)
        
        # Chat Display
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            width=70,
            height=25,
            bg='#F8F9FA'
        )
        self.chat_display.pack(fill='both', expand=True, pady=(0, 10))
        self.chat_display.config(state='disabled')
        
        # Input Frame
        self.input_frame = ttk.Frame(self.chat_frame)
        self.input_frame.pack(fill='x', side='bottom')
        
        # User Input
        self.user_input = ttk.Entry(
            self.input_frame,
            font=('Segoe UI', 10),
            width=60
        )
        self.user_input.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)
        
        # Send Button
        self.send_button = ttk.Button(
            self.input_frame,
            text="Send",
            command=lambda: self.send_message(None),
            style='Button.TButton'
        )
        self.send_button.pack(side='right')
        
        # Load Data Button
        self.load_button = ttk.Button(
            self.header_frame,
            text="Load Data",
            command=self.load_data,
            style='Button.TButton'
        )
        self.load_button.pack(side='right', padx=20, pady=10)
        
        self.data_df = None
        self.current_category = None
        
        # Initial welcome message
        self.display_message("Welcome to the Global Compliance Management chatbot! Please load your data to begin.")

    def load_data(self):
        """Load data from the Excel file."""
        try:
            self.data_df = pd.read_excel(r"C:\Users\104288\.cursor-tutor\Cursor_GCM\Compare_ByCountry.xlsx", sheet_name='Data')
            
            # Populate categories
            categories = self.data_df['Regulation_Category'].unique()
            self.category_list.delete(0, tk.END)
            for category in categories:
                self.category_list.insert(tk.END, category)
            
            self.display_message("Data loaded successfully! Please select a regulatory category or ask a question.")
        except Exception as e:
            self.display_message(f"Error loading data: {e}")

    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.category_list.curselection()
        if selection:
            self.current_category = self.category_list.get(selection[0])
            self.display_message(f"\nSelected category: {self.current_category}")
            self.show_category_info()

    def show_category_info(self):
        """Display information about the selected category"""
        if self.data_df is not None and self.current_category:
            category_data = self.data_df[self.data_df['Regulation_Category'] == self.current_category]
            info = f"\nRegulatory requirements for {self.current_category}:\n"
            for _, row in category_data.iterrows():
                info += f"\n• {row['Attribute_Name']}"
            self.display_message(info)

    def send_message(self, event=None):
        """Send the user's message and display the response."""
        user_message = self.user_input.get().strip()
        if user_message:
            self.display_message(f"\nYou: {user_message}")
            self.user_input.delete(0, tk.END)
            
            response = self.process_message(user_message)
            self.display_message(f"\nBot: {response}")

    def display_message(self, message):
        """Display a message in the chat area."""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{message}\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def process_message(self, message):
        """Process the user's message and generate a response."""
        if self.data_df is None:
            return "Please load the data first using the 'Load Data' button."

        message = message.lower()
        
        # Check for category-specific queries
        if self.current_category:
            category_data = self.data_df[self.data_df['Regulation_Category'] == self.current_category]
            
            # Look for country mentions
            countries = [col for col in self.data_df.columns if col not in ['Regulation_Category', 'Regulation_Subcategory', 'Attribute_Name']]
            mentioned_countries = [country for country in countries if country.lower() in message]
            
            if mentioned_countries:
                country = mentioned_countries[0]
                requirements = category_data[['Attribute_Name', country]].dropna()
                response = f"Requirements for {country} in {self.current_category} category:\n\n"
                for _, row in requirements.iterrows():
                    response += f"• {row['Attribute_Name']}: {row[country]}\n"
                return response
            
            return f"Please specify a country to get {self.current_category} requirements."
        
        # General queries
        if "help" in message:
            return ("I can help you with regulatory compliance information. Please:\n"
                   "1. Select a category from the left panel\n"
                   "2. Ask about specific requirements for a country\n"
                   "3. Use keywords like 'requirements', 'regulations', or 'standards'")
        
        return "Please select a regulatory category from the left panel to begin."

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop() 