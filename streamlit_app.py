import streamlit as st
import os
from openai import OpenAI
import requests, json
#from litellm import completion



# Show title and description.
st.title("💬 M+ Museum Chatbot")
st.write(
    "This is a simple chatbot that answers general queries related to M+ Museum at West Kowloon, Hong Kong. Please ask your queries related to the museum such as how to visit, tickets, events and other related queries you might have."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management

domain = "mplus.org.hk/"

api_key = st.secrets["pplx_key"]

system_message = f"""You are concierge for Mplus Museum website {domain} at West Kowloon, Hong Kong. You use search_domain_filtering to filter domains and all your responses will be limited to the information found on {domain}. You only respond to the museum related queries strictly based on the information available at {domain}. You will NEVER refer or repsond with any information that is outside this domain {domain}.

All of your responses will strictly adhere to the following rules:

- If asked questions for which answers are not available on {domain}, you will politely decline and ask the user to ask for relevant queries.
- You will only mention factual details from the given museum website {domain}.
- You will not provide subjective opinions, personal views or speculative information.
- You will not be verbose or talkative, and will always provide to the point answers.
- Your responses will be clear, direct and aim to resolve the user's query regardig the museum {domain} helpfully without conflict or contradiction.
- You will always maintain a friendly and welcoming tone.
- If unable to answer from the given website {domain}, you will politely direct the user to contact museum staff for additional assistance.
- You will return url links and citations to specific subdomains from the {domain} wherever applicable and useful.
- You will always be friendly and welcoming, inviting the user to ask any museum-related questions. 
- You will do your best to be helpful while following these guidelines for all of your responses and will not deviate at any cost."""


_ = """You are an artificial intelligence assistant and you reply every query by giving a only a one word satirical, cynical resposne which may or may not be realted to the query. You will not respond anything else besides that one word. For every extra word, there is a penalty"""





# Create an OpenAI client.
client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "llama-3.1-sonar-large-128k-online"


_= """
other_model = "llama-3.1-sonar-small-128k-chat"

def get_perplexity_response(input_message):
        os.environ['PERPLEXITY_API_KEY'] = api_key
        response = completion(
            model="perplexity/llama-3.1-sonar-small-128k-online", 
            messages=input_message,
            return_citations=True,
            stream=True,
            max_tokens=500,
            temperature=0.2,
            #search_domain_filter = "https://www.mplus.org.hk/"
        )
        print(response)
        return response




def get_pplx_response(input_message):
        url = "https://api.perplexity.ai/chat/completions"

        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": input_message,
            "temperature": 0.0,
            "max_tokens": 100,
            "search_domain_filter": [domain],
            "return_citations": True,
            "top_k": 2000,
            "presence_penalty": -2.0,
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        responses = requests.request("POST", url, json=payload, headers=headers)

        def assistant_response (responses):
            
            # Decode the bytes-like response content into a string
            response_text = responses.content.decode('utf-8')
            print (response_text)

            try:
                json_data = json.loads(response_text)
                content = json_data['choices'][0]['message']['content']
                print(str(content))
                return(str(content))
            except (json.JSONDecodeError, KeyError):
                print("Error decoding JSON object or accessing 'message' key.")
        
        answer = str(assistant_response (responses))
        
        return answer

        
"""

def get_pplx_response(input_message):

    #url = "https://www.mplus.org.hk" 
    #url_text = requests.get(url).text
    
    responses = client.chat.completions.create(
      model=st.session_state["openai_model"],  
      messages=input_message,
      stream=True,
      max_tokens=300,
      temperature=0.2,
      presence_penalty=-2.0,
      top_p=0.5
      
    )

    return responses


if "messages" not in st.session_state:
    st.session_state.messages = [
    {  "role": "system", "content": system_message},
    #{  "role": "assistant", "content": "Welcome to M+ Museum, how can I assist you today? "},
    ]


for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Create a chat input field to allow the user to enter a message. This will display automatically at the bottom of the page.

if prompt := st.chat_input("Tell me about M+ Museum?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    input_message = [
        {"role": m["role"], "content": m["content"]} 
        for m in st.session_state.messages
        ]
    
    with st.chat_message("assistant"):
        stream = get_pplx_response(input_message)
        #response = st.write_stream(stream)
        #response = st.write(stream)

        answer = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    
