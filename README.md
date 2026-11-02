# simpleRAGAgent

A simple RAG (Retrieval-Augmented Generation) model built using Flask and Ollama. This application allows users to interact with a chat interface, leveraging a knowledge context to answer questions, and maintaining conversational memory and history.

## Prerequisites

- **Python 3.14**: Ensure you have Python 3.14 installed on your system.
- **Ollama**: A tool for managing and running machine learning models.

## Installation

1. **Install Python 3.14**:
   - Download and install Python 3.14 from the [official website](https://www.python.org/downloads/).

2. **Install Ollama**:
   - Follow the installation instructions for Ollama from the [Ollama documentation](https://ollama.com/docs/installation).

3. **Install Required Python Packages**:
   - Navigate to the root directory of the project and run the following command to install the necessary Python packages:
     ```bash
     pip install -r requirements.txt
     ```

4. **Install Ollama Models**:
   - Install the required models using Ollama. Run the following commands in your terminal:
     ```bash
     ollama install llama3.1:8b
     ollama install all-minilm:l6-v2
     ```

## Running the Application

1. **Start the Flask Application**:
   - Navigate to the root directory of the project and run the following command to start the Flask server:
     ```bash
     python src/app.py
     ```

2. **Access the Application**:
   - Open a web browser and go to `http://localhost:5000` to access the chat interface.

## Features

- **Chat Interface**: Users can interact with the chatbot through a web-based interface.
- **Knowledge Context**: The application uses a knowledge context to answer questions, ensuring that responses are based on the provided data.
- **Conversational Memory**: The chatbot maintains memory of previous interactions, allowing for context-aware responses.
- **Conversation History**: Users can view and manage their conversation history.

## Usage

1. **Drop Text Files into Data Directory**:
   - Place any text files containing knowledge context into the `data` directory. The application will use these files to answer questions.

2. **Interact with the Chatbot**:
   - Use the chat interface to ask questions. The chatbot will respond based on the knowledge context and conversational history.

3. **Manage Conversations**:
   - Users can view and create conversations through the API endpoints provided by the application.

## Contribution

This free and open-source software was created by developers at Qubrick Studios. Find us on our website [Qubrick Studios](https://qubrickstudios.com) for more information and updates.