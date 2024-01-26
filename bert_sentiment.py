import os
import xml.etree.ElementTree as ET
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from torch.nn.functional import softmax
import logging
import pandas as pd
import urllib.request

# Set up logging
log_file_path = os.path.join(os.path.dirname(__file__), 'news_processing.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the database model
Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = 'news_articles'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    pub_date = Column(DateTime)
    source_url = Column(String)
    category = Column(String)

# Use an SQLite database file in the VSCode project directory
db_file_path = os.path.join(os.path.dirname(__file__), 'news_database.db')
engine = create_engine(f'sqlite:///{db_file_path}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Load pre-trained BERT model and tokenizer for sentiment analysis
tokenizer = BertTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = BertForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

def map_sentiment_to_category(sentiment_label):
    if sentiment_label == 0:
        return "Terrorism/Protest/Political Unrest/Riot"
    elif sentiment_label == 1:
        return "Positive/Uplifting"
    elif sentiment_label == 2:
        return "Natural Disasters"
    else:
        return "Others"

def process_article(article_data):
    try:
        combined_text = f"{article_data['title']} {article_data['content']}"
        inputs = tokenizer(combined_text, return_tensors='pt', truncation=True)

        with torch.no_grad():
            outputs = model(**inputs)
            predictions = softmax(outputs.logits, dim=1).tolist()[0]

        predicted_sentiment_index = predictions.index(max(predictions))
        predicted_category = map_sentiment_to_category(predicted_sentiment_index)

        logging.info(f"Processing Article - Title: {article_data['title']}, Source URL: {article_data['source_url']}, Predicted Category: {predicted_category}")

        existing_article = session.query(NewsArticle).filter_by(source_url=article_data['title']).first()
        if not existing_article:
            new_article = NewsArticle(
                title=article_data['title'],
                content=article_data['content'],
                pub_date=datetime.strptime(article_data['pub_date'], '%a, %d %b %Y %H:%M:%S GMT'),
                source_url=article_data['source_url'],
                category=predicted_category
            )
            session.add(new_article)
            session.commit()

            logging.info(f"Article Added to Database - Title: {new_article.title}, Source URL: {new_article.source_url}, Category: {new_article.category}")

    except Exception as e:
        logging.error(f"Error processing article: {str(e)}")

def parse_xml_feed(feed_url):
    try:
        with urllib.request.urlopen(feed_url) as response:
            xml_content = response.read()

        tree = ET.ElementTree(ET.fromstring(xml_content))
        root = tree.getroot()

        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else ''
            content = item.find('description').text if item.find('description') is not None else ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
            source_url = item.find('link').text if item.find('link') is not None else ''

            article_data = {
                'title': title,
                'content': content,
                'pub_date': pub_date,
                'source_url': source_url,
            }
            process_article(article_data)

    except ET.ParseError as pe:
        logging.error(f"Error parsing XML feed {feed_url}: {str(pe)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

if __name__ == '__main__':
    session.query(NewsArticle).delete()
    session.commit()

    xml_feeds = [
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "http://qz.com/feed",
        "http://feeds.foxnews.com/foxnews/politics",
        "http://feeds.reuters.com/reuters/businessNews",
        "http://feeds.feedburner.com/NewshourWorld",
        "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
    ]

    for feed_url in xml_feeds:
        parse_xml_feed(feed_url)

    articles = session.query(NewsArticle).all()
    articles_data = [{'Title': article.title, 'Content': article.content, 'Pub Date': article.pub_date, 'Source URL': article.source_url, 'Category': article.category} for article in articles]
    df = pd.DataFrame(articles_data)
    excel_file_path = os.path.join(os.path.dirname(__file__), 'news_articles.xlsx')
    df.to_excel(excel_file_path, index=False, engine='openpyxl')

    logging.info(f"Database content exported to Excel file: {excel_file_path}")
