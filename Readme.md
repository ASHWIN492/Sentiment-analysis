# Visualization and Sentiment Analysis of YouTube Data

This is a Streamlit application that performs sentiment analysis on YouTube video comments and provides visual insights into channel and video performance. The app uses the YouTube Data API to fetch data, NLTK for sentiment analysis, and Plotly for data visualizations.

## Features

- **Channel Insights**: Provides an overview of a YouTube channel's statistics including subscriber count, total views, and video count.
- **Sentiment Analysis**: Analyzes the sentiment of video comments (positive, negative, and neutral) using NLTK's Vader lexicon.
- **Spam Detection**: Filters spam comments using a simple keyword-based method.
- **Video Statistics**: Displays video statistics such as view count, like count, comment count, and average sentiment per video.
- **Channel Comparison**: Allows comparison of multiple YouTube channels by their subscriber count, total views, and video count.
- **Interactive Visualizations**: Includes various visualizations such as bar charts for comment distribution, video popularity, and sentiment scores.

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/yourusername/youtube-channel-analysis-app.git
    cd youtube-channel-analysis-app
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Download the NLTK `vader_lexicon` data:

    ```bash
    python -m nltk.downloader vader_lexicon
    ```

4. Set up your YouTube API Key. Create a `.env` file (or update the script directly) with your YouTube Data API key:

    ```plaintext
    API_KEY=your_youtube_data_api_key
    ```

## Usage

1. Run the Streamlit app:

    ```bash
    streamlit run app.py
    ```

2. Open your browser and navigate to `http://localhost:8501`.

3. Enter a YouTube channel ID to start the analysis.

## Pages

### 1. Home

- Enter a YouTube channel ID and analyze the channel's data including videos and comments.
- Select whether to filter spam comments.

### 2. Channel Insights

- Provides an overview of the YouTube channel including subscribers, total views, and videos.
- Displays video statistics like view count, like count, and comment count.
- Includes interactive visualizations for comment distribution, video popularity, and average sentiment per video.

### 3. Sentiment Analysis

- Analyzes and displays sentiment statistics for video comments (positive, neutral, and negative).
- Shows the most positive and most negative comments.
- Interactive sentiment distribution plots for all comments and by video.

### 4. Channel Comparison

- Allows comparison of multiple YouTube channels by subscriber count, view count, and video count.
- Displays bar charts for easy comparison.

## Requirements

- Python 3.x
- YouTube Data API v3
- Libraries: `streamlit`, `google-api-python-client`, `nltk`, `pandas`, `plotly`

## API Key Setup (via RapidAPI)

To use the YouTube Data API through RapidAPI, follow these steps:

1. Go to the [RapidAPI YouTube Data API v3 page](https://rapidapi.com/).
2. Sign up for an account or log in if you already have one.
3. Subscribe to the YouTube Data API on RapidAPI.
4. Copy your API key from the RapidAPI dashboard.
5. Update the script with your RapidAPI key in the `API_KEY` variable or store it in a `.env` file.



