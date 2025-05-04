import pandas as pd
from datetime import datetime
from langchain_community.llms import Ollama
from langchain.output_parsers.json import parse_json_markdown
from langchain.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
import json
import smtplib
from email.message import EmailMessage
import os

class WeatherBasedPackaging:
    def __init__(self):
        # Initialize embedding model
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        # Initialize LLM
        self.llm = Ollama(model="llama3.2")
        # Vector store path
        self.vector_store_path = "weather_vector_store"
        
    def prepare_weather_context(self, df, next_4_months):
        # Create context strings for each month's weather
        contexts = []
        for idx in next_4_months:
            context = f"""
            Month: {df.iloc[idx]['month']}
            Weather: {df.iloc[idx]['weather']}
            """
            contexts.append(context)
        return contexts

    def get_weather_data(self):
        # Load weather data
        df = pd.read_csv("dubai_2024_monthly_weather.csv")
        
        # Find May's index
        may_index = df[df['month'] == 'May'].index[0]
        
        # Get next 4 months starting from May
        next_4_months = [(may_index + i) % 12 for i in range(4)]
        next_month_names = df.iloc[next_4_months]['month'].tolist()
        
        return df, next_4_months, next_month_names

    def create_or_load_vector_store(self, df, next_4_months):
        if os.path.exists(self.vector_store_path):
            print("Loading existing weather vector store...")
            try:
                vector_store = FAISS.load_local(
                    self.vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Error loading vector store: {e}")
                print("Creating new weather vector store...")
                vector_store = self._create_vector_store(df, next_4_months)
        else:
            print("Creating new weather vector store...")
            vector_store = self._create_vector_store(df, next_4_months)
        
        return vector_store

    def _create_vector_store(self, df, next_4_months):
        contexts = self.prepare_weather_context(df, next_4_months)
        vector_store = FAISS.from_texts(contexts, self.embeddings)
        vector_store.save_local(self.vector_store_path)
        return vector_store

    def generate_packaging_list(self, df, next_4_months, next_month_names):
        # Build weather context for the prompt
        weather_context = ", ".join(
            [f"{df.iloc[idx]['month']}: {df.iloc[idx]['weather']}" for idx in next_4_months]
        )

        # Enhanced prompt with product considerations
        prompt = f"""
        Based on the weather conditions for the next 4 months: {', '.join(next_month_names)},
        and their weather conditions: {weather_context},
        
        List the packaging materials required for inventory, considering:
        1. Weather protection needs (rain, heat, humidity)
        2. Common product types in our inventory
        3. Seasonal variations in packaging requirements
        
        Return a JSON array of material names only. Example format:
        [
            {{"material": "Waterproof Bubble Wrap"}},
            {{"material": "Insulated Boxes"}},
            {{"material": "Moisture Absorbent Packets"}}
        ]
        
        Important:
        - Each item MUST have only the "material" field
        - The "material" field must be a descriptive string
        - Return ONLY the JSON array, no other text
        """

        response = self.llm.invoke(prompt)
        try:
            # First try to parse as JSON directly
            parsed_data = json.loads(response)
        except json.JSONDecodeError:
            try:
                # If that fails, try to parse markdown JSON
                parsed_data = parse_json_markdown(response)
            except Exception as e:
                print(f"Error parsing response: {e}")
                # Return a default list if parsing fails
                parsed_data = [
                    {"material": "Waterproof Bubble Wrap"},
                    {"material": "Insulated Boxes"},
                    {"material": "Moisture Absorbent Packets"},
                    {"material": "Weather-resistant Tape"},
                    {"material": "Thermal Insulation Sheets"},
                    {"material": "Desiccant Packs"}
                ]
        
        # Ensure all items have the material field
        for item in parsed_data:
            if 'material' not in item:
                item['material'] = "Unknown Material"
        
        return parsed_data

    def send_email(self, packaging_list):
        EMAIL_ADDRESS = "YOUR-MAIL"
        EMAIL_PASSWORD = "PASSWORD"  

        msg = EmailMessage()
        msg['Subject'] = 'Required Packaging Materials for the next quarter'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS_TO
        msg.set_content('Please find attached the required list of packaging materials for the next quarter.')

        # Save packaging list to JSON
        filename = 'packaging_materials_list.json'
        with open(filename, 'w') as f:
            json.dump(packaging_list, f, indent=4)

        # Attach the file
        with open(filename, 'rb') as f:
            file_data = f.read()
            msg.add_attachment(file_data, maintype='text', subtype='json', filename=filename)

        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print("Email sent successfully with attachment.")

def main():
    # Initialize the packaging predictor
    packaging_predictor = WeatherBasedPackaging()
    
    # Get weather data
    df, next_4_months, next_month_names = packaging_predictor.get_weather_data()
    
    # Create or load vector store
    vector_store = packaging_predictor.create_or_load_vector_store(df, next_4_months)
    
    # Generate packaging list
    packaging_list = packaging_predictor.generate_packaging_list(df, next_4_months, next_month_names)
    
    # Send email with packaging list
    packaging_predictor.send_email(packaging_list)

if __name__ == "__main__":
    main()

