from flask import Flask, render_template
import requests


app = Flask(__name__)


# Route to fetch and display memes
@app.route('/')
def home():
   # Fetch meme data
   url = "https://meme-api.com/gimme/wholesomememes"
   response = requests.get(url)
   meme_data = response.json()
  
   meme_url = meme_data['url']  # Meme image URL
   meme_source = meme_data['subreddit']  # Meme source (subreddit)
  
   return render_template('index.html', meme_url=meme_url, meme_source=meme_source)


if __name__ == "__main__":
   app.run(debug=True)
