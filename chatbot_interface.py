import tkinter as tk
from tkinter import scrolledtext
import pandas as pd

class ChatbotApp:
    def __init__(self, master):
        self.master = master
        master.title("Regulatory Compliance Chatbot")

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(master, state='disabled', width=50, height=20)
        self.chat_display.pack(pady=10)

        # User input area
        self.user_input = tk.Entry(master, width=50)
        self.user_input.pack(pady=10)
        self.user_input.bind("<Return>", self.send_message)  # Bind Enter key to send message

        # Load data button
        self.load_button = tk.Button(master, text="Load Data", command=self.load_data)
        self.load_button.pack(pady=5)

        self.data_df = None  # Placeholder for the data

    def load_data(self):
        """Load data from the Excel file."""
        try:
            self.data_df = pd.read_excel(r"C:\Users\104288\.cursor-tutor\Cursor_GCM\Compare_ByCountry.xlsx", sheet_name='Data')
            self.display_message("Data loaded successfully!")
        except Exception as e:
            self.display_message(f"Error loading data: {e}")

    def send_message(self, event=None):
        """Send the user's message and display the response."""
        user_message = self.user_input.get()
        self.display_message(f"You: {user_message}")
        self.user_input.delete(0, tk.END)  # Clear input field

        # Process the user's message
        response = self.process_message(user_message)
        self.display_message(f"Bot: {response}")

    def display_message(self, message):
        """Display a message in the chat area."""
        self.chat_display.config(state='normal')  # Enable editing
        self.chat_display.insert(tk.END, message + "\n")  # Add message
        self.chat_display.config(state='disabled')  # Disable editing
        self.chat_display.yview(tk.END)  # Scroll to the end

    def process_message(self, message):
        """Process the user's message and generate a response."""
        if self.data_df is None:  # Check if data_df is None
            return "Please load the data first."

        # Check for specific queries about safety regulations
        if "safety regulation" in message.lower():
            return self.get_safety_regulation_info(message)
        else:
            return "I'm sorry, I didn't understand that. Please ask about safety regulations."

    def get_safety_regulation_info(self, message):
        """Retrieve safety regulation information based on the user's query."""
        # Example: Extract the country from the message
        for country in self.data_df.columns[2:]:  # Assuming first two columns are not countries
            if country.lower() in message.lower():
                return self.get_regulation_details(country)
        return "Please specify a valid country."

    def get_regulation_details(self, country):
        """Get details about the safety regulation for a specific country."""
        if country in self.data_df.columns:
            details = self.data_df[country].dropna()
            formatted_details = "\n".join([f"- {detail}" for detail in details])  # Format each detail with a bullet point
            return f"Regulation details for {country}:\n{formatted_details}"
        else:
            return f"No regulation details found for {country}."

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop() 