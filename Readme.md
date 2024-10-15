# YouTube Channel Analysis Application

This is a Streamlit web application for analyzing YouTube channels. The app retrieves data from the YouTube API (via RapidAPI), including video statistics and comments, and applies sentiment analysis to comments using NLTK's Vader lexicon. Additionally, it provides visual insights for channel statistics, video popularity, and allows comparison between multiple channels.

## Features
- **Channel Insights**: 
  - Displays total subscribers, views, and videos of a YouTube channel.
  - Provides a detailed breakdown of each video's statistics (views, likes, comments).
  - Visualizations for comments per video, views per video, most and least liked videos, and more.

- **Sentiment Analysis**:
  - Analyzes the sentiment of comments (positive, negative, or neutral) using NLTK's Vader sentiment analyzer.
  - Provides insights such as the distribution of comment sentiments and average sentiment per video.
  - Displays most positive and most negative comments.

- **Spam Comment Filtering**:
  - Filters out comments containing common spam keywords like "subscribe", "follow me", etc.

- **Channel Comparison**:
  - Compare multiple YouTube channels based on subscriber count, total views, and number of videos.
  - Visual comparison using bar charts.

## Setup Instructions

### Prerequisites
1. **YouTube Data API via RapidAPI**: Obtain an API key from the [RapidAPI Dashboard](https://rapidapi.com/).
2. **Python 3.x** installed on your system.
3. **Required Python Libraries**: Install the following libraries using `pip`:
    ```bash
    pip install streamlit requests nltk plotly pandas
    ```


"# Sentiment-analysis" 
