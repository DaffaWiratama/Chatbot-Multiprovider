# 💬 Chatbot Multiprovider

A simple Streamlit app that act as a chatbot using OpenAI Groq or Gemini API. The app supports choosing provider and supplying the corresponding API key. Some basic model from Groq and Gemini already included.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### Prerequisites
Ensure you have Python installed. It is recommended to use `miniconda` or `conda` for environment management.

### How to run it on your own machine

1. Install the requirements

   Navigate to the project directory and install the necessary packages:

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_with_groq.py
   ```

   The application will open in your web browser.
   
## Code Structure

- streamlit_app.py: Default Streamlit template file, provided by Streamlit.
- streamlit_with_groq.py: Streamlit app modified by me.
- streamlit_groq_only.py: Streamlit app that I host on Streamlit Cloud Community with secret.toml (not require API Key)
- requirements.txt: Lists all Python dependencies required for the project.

## Try without Installation from StreamlitCloud Community!
https://daffachatbot.streamlit.app/
