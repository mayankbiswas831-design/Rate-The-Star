import feedparser
import json
from datetime import datetime
from transformers import pipeline

# Load a pre-trained HuggingFace sentiment model
# For production, you might want a RoBERTa model specific to finance/news
print("Loading AI Model...")
sentiment_engine = pipeline("sentiment-analysis")
import spacy

# Load the spaCy English model for Named Entity Recognition (NER)
print("Loading Entity Extraction Model...")
nlp = spacy.load("en_core_web_sm")

def extract_main_entity(text):
    """
    Scans the news text and extracts the primary Organization, Person, or Product.
    """
    doc = nlp(text)
    entities = []
    
    # Loop through the text to find proper nouns and entities
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PERSON", "PRODUCT"]:
            entities.append(ent.text)
            
    # If it finds a specific entity, return the first one. 
    # Otherwise, classify it as "General News"
    if entities:
        return entities[0]
    else:
        return "General News"
    
def calculate_rating(text):
        # Run text through HuggingFace
        result = sentiment_engine(text)[0]
        label = result['label']
        score = result['score'] # This is the confidence (0.0 to 1.0)
        
        # Convert POSITIVE/NEGATIVE to 1-5 Stars
        if label == "POSITIVE":
            # Map higher confidence to 4 or 5 stars
            stars = 5 if score > 0.8 else 4
        else: # NEGATIVE
            # Map higher confidence to 1 or 2 stars
            stars = 1 if score > 0.8 else 2
            
        # Convert confidence to a percentage for your UI
        confidence_percent = round(score * 100, 1)
        
        return stars, confidence_percent
def fetch_live_news():
    print("Fetching latest articles from RSS feed...")
    # Using Google News RSS for live headlines
    feed_url = "https://news.google.com/rss"
    parsed_feed = feedparser.parse(feed_url)
    
    articles = []
    # Grab the top 10 most recent articles
    for entry in parsed_feed.entries[:10]:
        articles.append({
            "title": entry.title,
            "link": entry.link
        })
        
    return articles
    
def process_and_save_news():
    print(f"[{datetime.now()}] Fetching live news...")
    articles = fetch_live_news()
    
    # Load existing data
    try:
        with open("news_data.json", "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    new_entries_count = 0

    for article in articles:
        # Check if we already have this article to avoid duplicates
        if not any(item.get("title") == article["title"] for item in existing_data):
            
            # Rate the entity/article based on its title
            stars, confidence = calculate_rating(article["title"])
            
            new_entry = {
                "title": article["title"],
                "stars": stars,
                "confidence_score": f"{confidence}%",
                "timestamp": datetime.now().isoformat(),
                "source_url": article["link"]
            }
            
            existing_data.insert(0, new_entry) # Put newest at the top
            new_entries_count += 1

    # Save back to JSON
    with open("news_data.json", "w") as file:
        json.dump(existing_data, file, indent=4)
        
    print(f"Successfully processed and added {new_entries_count} new ratings.")
    # Run the function immediately once
process_and_save_news()

