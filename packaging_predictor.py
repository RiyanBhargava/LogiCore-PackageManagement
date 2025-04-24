import pandas as pd
import numpy as np
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os

class PackagingPredictor:
    def __init__(self):
        # Initialize embedding model
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        # Initialize LLM
        self.llm = Ollama(model="llama3.2")
        # Vector store path
        self.vector_store_path = "vector_store"
        
        # Load the vector store if it exists
        if os.path.exists(self.vector_store_path):
            print("Loading existing vector store...")
            try:
                self.vector_store = FAISS.load_local(
                    self.vector_store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                # Create prompt template
                self.prompt_template = PromptTemplate(
                    input_variables=["context", "question"],
                    template="""
                    Based on the following product information and similar products from our database, 
                    determine the most appropriate packaging material and explain why.
                    
                    Context:
                    {context}
                    
                    Question:
                    {question}
                    
                    Please provide:
                    1. The recommended packaging material
                    2. A detailed explanation of why this packaging material is suitable
                    """
                )
                
                # Create retrieval chain
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=self.vector_store.as_retriever(),
                    return_source_documents=True,
                    chain_type_kwargs={"prompt": self.prompt_template}
                )
            except Exception as e:
                print(f"Error loading vector store: {e}")
                raise Exception("Failed to load vector store. Please ensure the vector store files exist in the correct location.")

    def prepare_training_data(self, df):
        # Create context strings for each product
        contexts = []
        for _, row in df.iterrows():
            context = f"""
            Product Type: {row['Product_Type']}
            Weight: {row['Weight_kg']} kg
            Fragile: {row['Fragile']}
            Temperature Condition: {row['Temp_Condition']}
            Humidity Level: {row['Humidity_Level']}
            Packaging Material: {row['Packaging_Material']}
            """
            contexts.append(context)
        return contexts

    def predict(self, test_data):
        # Create query string
        query = f"""
        Product Type: {test_data['Product_Type']}
        Weight: {test_data['Weight_kg']} kg
        Fragile: {test_data['Fragile']}
        Temperature Condition: {test_data['Temp_Condition']}
        Humidity Level: {test_data['Humidity_Level']}
        
        What is the most appropriate packaging material for this product?
        """
        
        # Get prediction and reasoning
        result = self.qa_chain({"query": query})
        return result

def main():
    # Initialize predictor
    predictor = PackagingPredictor()
    
    # Load test data
    test_df = pd.read_csv("test_package.csv")
    test_data = test_df.iloc[0]
    
    # Make prediction
    result = predictor.predict(test_data)
    
    # Print results
    print("\nProduct Details:")
    print(f"Product ID: {test_data['Product_ID']}")
    print(f"Product Type: {test_data['Product_Type']}")
    print(f"Weight: {test_data['Weight_kg']} kg")
    print(f"Fragile: {test_data['Fragile']}")
    print(f"Temperature Condition: {test_data['Temp_Condition']}")
    print(f"Humidity Level: {test_data['Humidity_Level']}")
    
    print("\nPrediction and Reasoning:")
    print(result['result'])

if __name__ == "__main__":
    main() 