# Sentiment Analysis and News Categorization with BERT

## Overview

The `bert_sentiment.py` script is designed to fetch news articles from various RSS feeds, perform sentiment analysis using a pre-trained BERT (Bidirectional Encoder Representations from Transformers) model, and categorize the articles based on their predicted sentiments. The processed data is then stored in an SQLite database and exported to an Excel file for further analysis.

## Logic Flow

1. **Database Setup**: The script initializes an SQLite database (`news_database.db`) and defines a `NewsArticle` model using SQLAlchemy. This model represents the structure of the news articles to be stored in the database.

2. **BERT Model and Tokenizer Setup**: A pre-trained BERT model and tokenizer for sentiment analysis are loaded using the Hugging Face `transformers` library. The model is configured to classify text into different sentiment labels.

3. **Sentiment Mapping**: A mapping function (`map_sentiment_to_category`) is defined to map sentiment labels to human-readable categories. Currently, the categories are:
    - Category 0: "Terrorism/Protest/Political Unrest/Riot"
    - Category 1: "Positive/Uplifting"
    - Category 2: "Natural Disasters"
    - Category 3: "Others"

4. **Article Processing**: The script defines a function (`process_article`) to process individual news articles. It tokenizes the article's title and content, feeds it to the BERT model, and determines the predicted sentiment category. The processed articles are then stored in the database.

5. **XML Feed Parsing**: The script fetches news articles from various RSS feeds specified in the `xml_feeds` list. It uses the `xml.etree.ElementTree` module to parse XML content, extracts relevant information (title, content, pub date, source URL), and calls the `process_article` function for each article.

6. **Database Cleaning**: Before processing new articles, the script clears the existing data in the database.

7. **Export to Excel**: After processing all articles, the script exports the database content to an Excel file (`news_articles.xlsx`). The exported file contains columns for title, content, pub date, source URL, and category.

## Design Choices

- **SQLite Database**: SQLite is chosen for simplicity and portability. The database is created in the project directory.

- **BERT Model**: The script uses a pre-trained BERT model for sentiment analysis. BERT is a powerful language model capable of capturing context and relationships in text.

- **Logging**: Logging is implemented to record information, errors, and events during script execution. Logs are stored in a file (`news_processing.log`) for debugging and monitoring.

- **Pandas for Data Handling**: Pandas is used to create a DataFrame for easy manipulation of data before exporting it to an Excel file.

- **XML Parsing**: The `xml.etree.ElementTree` module is used for parsing XML feeds. Error handling is implemented to handle parsing errors.

## Usage

1. Install required libraries: `pip install -r requirements.txt`

2. Run the script: `python bert_sentiment.py`

3. Check the generated logs (`news_processing.log`) for information on processed articles and potential errors.

4. The final processed data is exported to an Excel file (`news_articles.xlsx`) for further analysis.

## Notes

- Make sure to have an internet connection to fetch RSS feeds and download the pre-trained BERT model and tokenizer.

- Ensure the specified RSS feeds (`xml_feeds`) are accessible.

- Customize the sentiment categories in the `map_sentiment_to_category` function if needed.

- For troubleshooting, refer to the logs in `news_processing.log` for detailed information.

**Note**: This README assumes basic familiarity with Python, SQLite, BERT, and XML parsing.
