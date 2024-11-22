# WebBot

Used web scraping tool, `BeautifulSoup` to extract information from a website specified by the user then provide this data to a `llama3-70b` model as context, where the user can prompt the model and retrieve real time information from the website instantly from.

This app is currently hosted on <a href='https://huggingface.co/spaces/Koomemartin/WebBot'>HuggingFace Spaces</a>

## Local Usage

Fork this repository and run the `app.py` script using the following code

First create a secure tunnel to run the streamlit app

```bash
wget -q -O - ipv4.icanhazip.com
```
This provides an IP address that autheticates you to access the app in your browser

```bash
streamlit run app.y & npx localtunnel --port 8501
```
This code runs the `app.y` in the secure tunnel and provides the link to acess it in your browser



