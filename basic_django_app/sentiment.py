from textblob import TextBlob

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return 'positive'
    elif polarity < -0.1:
        return 'negative'
    else:
        return 'neutral'

def get_post_sentiment(post):
    # Combine title and body for sentiment analysis
    content = f"{post.title}\n{post.body}"
    return analyze_sentiment(content)
