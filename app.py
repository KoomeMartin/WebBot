import streamlit as st
from bs4 import BeautifulSoup
import requests
from groq import Groq
import os
from dotenv import load_dotenv
import json

# scraping pipeline
class Website:
    """
    A utility class to represent a Website that we have scraped, now with links
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]  # links found in home page
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"


# first lets get relevant links from the home page for a broad information about the website provided

# system prompt of the first call 
link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to the website, \
such as links to an About page, or a Company page, or Careers/Jobs pages. Limit the number of extracted links to seven most important links\n"
link_system_prompt += "You should respond in JSON as in this example: \n"
link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page": "url": "https://another.full.url/careers"}
    ]
}
"""

#pre defined user prompt to extract only important links in about the website 
def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links to the website, respond with the full https URL in JSON format. \
                    Do not include Terms of Service, Privacy\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt

# make the first call to get the important links 
def get_links(url):
    website = Website(url)
    response = client.chat.completions.create(
    messages=[
       {"role": "system", "content":link_system_prompt },
       {"role": "user", "content": get_links_user_prompt(website)}
    ],
    model="llama3-groq-70b-8192-tool-use-preview",
    temperature=1,
    max_tokens=2048,
    stop=None,
    stream=False,
    response_format = {"type" : "json_object" })
    result = response.choices[0].message.content
    return json.loads(result)

#all the content required to generate information from user about the website
@st.cache_resource
def get_all_details(url):
    result = "Home page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    print("Available links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result


# Initialize Groq client
# load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

# Streamlit UI
st.title("Welcome to WebBot🌍")
st.write("Enter a website URL and ask questions about its content!")

# Input fields
url = st.text_input("Website URL:", " " )
user_query = st.text_area("What would you like to know about this website")

if user_query:
    # Scrape website content
    with st.spinner("Scraping website..."):
        
        try:
            website = get_all_details(url)
            st.success("Website loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load website: {e}")
        
        # Second to Call Groq API for processing
        st.write("Querying the website...")
        with st.spinner("Processing your query..."):
            try:
                chat_streaming = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant specializing in extracting and analyzing website content. Provide information required by the user based on the website information provided. Ensure responses are clear, concise, and formatted in Markdown for better readability. use your knowledge to add relevant inforation to the users query"},
                        {"role": "user", "content": f"Here's the content to use:\n {website} \n Now respond appropriately to the query: {user_query}\n"}
                    ],
                    model="llama3-groq-70b-8192-tool-use-preview",
                    temperature=0.8,
                    max_tokens=2042,
                    top_p=0.6,
                    stream=False,
                )
                # st.write('Passed model')

            except Exception as e:
                st.error(f"Failed to process query to model: {e}")
            response = ""
            try:
                # for chunk in chat_streaming:
                #     content = chunk.choices[0].delta.content
                #     if content:  # Ensure content is not None
                response=chat_streaming.choices[0].message.content
                # response += content
                st.write("🤖:")
                st.write(response)
            except Exception as e:
                st.error(f"Failed to process query: {e}")



st.markdown("-----")
st.write("© 2024 Application")
st.warning("Disclaimer: This application currently does not support Javascript websites!!")
