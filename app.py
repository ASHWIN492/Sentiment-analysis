import streamlit as st
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import pandas as pd
import plotly.express as px

# Download the NLTK vader lexicon for sentiment analysis
nltk.download('vader_lexicon', quiet=True)

# YouTube API setup
API_KEY = "AIzaSyA24yKEydJlTXRKvGesG-Pr5LpfW20vuAa"  # Replace with your actual API key
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Basic spam detection keywords
spam_keywords = ["subscribe", "check out", "follow me", "click", "link", "giveaway", "win", "visit my channel", "free"]

def is_spam(comment):
    """Simple function to detect spam based on keywords."""
    comment_lower = comment.lower()
    return any(keyword in comment_lower for keyword in spam_keywords)

def get_channel_videos(channel_id, max_results=10):
    try:
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        videos = []
        next_page_token = None
        while len(videos) < max_results:
            playlist_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            ).execute()
            
            videos.extend(playlist_response['items'])
            next_page_token = playlist_response.get('nextPageToken')
            
            if not next_page_token:
                break
        
        return videos
    except HttpError as e:
        st.error(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return []

def get_video_comments(video_id, max_comments=100):
    comments = []
    try:
        results = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText",
            maxResults=min(100, max_comments)
        ).execute()

        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

    except HttpError as e:
        if e.resp.status == 403:
            pass
        else:
            st.error(f"An HTTP error {e.resp.status} occurred: {e.content}")

    return comments

def analyze_sentiment(comments):
    sia = SentimentIntensityAnalyzer()
    sentiments = [sia.polarity_scores(comment)['compound'] for comment in comments]
    return sentiments

def get_channel_statistics(channel_id):
    try:
        channel_response = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        ).execute()
        
        if 'items' in channel_response:
            item = channel_response['items'][0]
            stats = item['statistics']
            stats['channelTitle'] = item['snippet']['title']  # Add channel title
            return stats
        else:
            return None
    except HttpError as e:
        st.error(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None

def get_video_statistics(video_id):
    try:
        stats = youtube.videos().list(
            part='statistics,contentDetails',
            id=video_id
        ).execute()['items'][0]
        
        duration = stats['contentDetails']['duration']
        # Convert duration to a more readable format if needed
        
        return {
            'viewCount': int(stats['statistics'].get('viewCount', 0)),
            'likeCount': int(stats['statistics'].get('likeCount', 0)),
            'commentCount': int(stats['statistics'].get('commentCount', 0)),
            'duration': duration
        }
    except HttpError as e:
        st.error(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return {}

def filter_spam_comments(comments):
    """Return non-spam comments by filtering out spam using the is_spam function."""
    non_spam_comments = [comment for comment in comments if not is_spam(comment)]
    return non_spam_comments

def visualization_page(df_comments, df_videos, channel_stats):
    st.header("Channel Insights and Visualization")
    
    # Channel Overview
    st.subheader("Channel Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Subscribers", f"{int(channel_stats['subscriberCount']):,}")
    col2.metric("Total Views", f"{int(channel_stats['viewCount']):,}")
    col3.metric("Total Videos", f"{int(channel_stats['videoCount']):,}")

    # Video Statistics
    st.subheader("Video Statistics")
    st.write(f"Number of videos analyzed: {len(df_videos)}")
    st.write(f"Total number of comments analyzed: {len(df_comments)}")
    
    # Comments per Video
    comments_per_video = df_comments['Video Title'].value_counts()
    fig_comments_per_video = px.bar(
        x=comments_per_video.index, 
        y=comments_per_video.values,
        labels={'x': 'Video Title', 'y': 'Number of Comments'},
        title="Number of Comments per Video"
    )
    fig_comments_per_video.update_xaxes(tickangle=45)
    st.plotly_chart(fig_comments_per_video)

    # Video Popularity (if view count is available)
    if 'View Count' in df_videos.columns:
        st.subheader("Video Popularity")
        
        # Top-10 videos by views
        st.subheader("Top-10 Videos by Views")
        top_videos = df_videos.nlargest(10, 'View Count')
        st.table(top_videos[['Video Title', 'View Count']])
        
        # Bottom-10 videos by views
        st.subheader("Bottom-10 Videos by Views")
        bottom_videos = df_videos.nsmallest(10, 'View Count')
        st.table(bottom_videos[['Video Title', 'View Count']])
        
        # Plot for views per video
        fig_video_views = px.bar(
            df_videos.sort_values('View Count', ascending=False), 
            x='Video Title', 
            y='View Count',
            title="Views per Video"
        )
        fig_video_views.update_xaxes(tickangle=45)
        st.plotly_chart(fig_video_views)
    else:
        st.warning("View Count data is not available for the videos.")

    # Most and least liked videos (if Like Count is available)
    if 'Like Count' in df_videos.columns:
        st.subheader("Most Liked Video")
        st.table(df_videos.nlargest(1, 'Like Count')[['Video Title', 'Like Count']])

        st.subheader("Least Liked Video")
        st.table(df_videos.nsmallest(1, 'Like Count')[['Video Title', 'Like Count']])
    else:
        st.warning("Like Count data is not available for the videos.")

    # Video with the highest duration (if Duration is available)
    if 'Duration' in df_videos.columns:
        st.subheader("Video with the Highest Duration")
        st.table(df_videos.nlargest(1, 'Duration')[['Video Title', 'Duration']])
    else:
        st.warning("Duration data is not available for the videos.")

    # Average sentiment by video (if available)
    if 'Average Sentiment' in df_videos.columns:
        st.subheader("Average Sentiment by Video")
        fig_video_sentiment = px.bar(
            df_videos.sort_values('Average Sentiment'), 
            x='Video Title', 
            y='Average Sentiment',
            title="Average Sentiment by Video"
        )
        fig_video_sentiment.update_xaxes(tickangle=45)
        st.plotly_chart(fig_video_sentiment)
    else:
        st.warning("Average Sentiment data is not available for the videos.")

def sentiment_analysis_page(df_comments, df_videos):
    st.header("Sentiment Analysis")

    # Overall sentiment statistics
    avg_sentiment = df_comments['Sentiment'].mean()
    positive_comments = (df_comments['Sentiment'] > 0).sum()
    negative_comments = (df_comments['Sentiment'] < 0).sum()
    neutral_comments = (df_comments['Sentiment'] == 0).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average Sentiment", f"{avg_sentiment:.2f}")
    col2.metric("Positive Comments", f"{positive_comments:,}")
    col3.metric("Negative Comments", f"{negative_comments:,}")
    col4.metric("Neutral Comments", f"{neutral_comments:,}")

    # Sentiment distribution
    fig_sentiment_dist = px.histogram(
        df_comments, 
        x='Sentiment', 
        nbins=50, 
        title="Distribution of Comment Sentiment Scores"
    )
    st.plotly_chart(fig_sentiment_dist)

    # Average sentiment by video
    fig_video_sentiment = px.bar(
        df_videos.sort_values('Average Sentiment'), 
        x='Video Title', 
        y='Average Sentiment',
        title="Average Sentiment by Video"
    )
    fig_video_sentiment.update_xaxes(tickangle=45)
    st.plotly_chart(fig_video_sentiment)
    
    # Display comments with highest and lowest sentiment
    st.subheader("Most Positive Comments")
    st.table(df_comments.nlargest(5, 'Sentiment')[['Video Title', 'Comment', 'Sentiment']])
    
    st.subheader("Most Negative Comments")
    st.table(df_comments.nsmallest(5, 'Sentiment')[['Video Title', 'Comment', 'Sentiment']])
    
    # Allow user to explore all comments
    st.subheader("Explore All Comments")
    st.dataframe(df_comments)
    
    # Add a text input for searching comments
    search_term = st.text_input("Search comments containing:")
    if search_term:
        filtered_df = df_comments[df_comments['Comment'].str.contains(search_term, case=False)]
        st.write(f"Found {len(filtered_df)} comments containing '{search_term}':")
        st.dataframe(filtered_df)

def channel_comparison_page():
    st.header("Compare Multiple Channels")
    
    # Input multiple channel IDs
    channel_ids = st.text_area("Enter YouTube Channel IDs (comma-separated):", "").split(',')

    if st.button("Compare Channels"):
        channel_stats_list = []
        for channel_id in channel_ids:
            channel_id = channel_id.strip()
            channel_stats = get_channel_statistics(channel_id)
            if channel_stats:
                channel_stats_list.append(channel_stats)

        if channel_stats_list:
            df_channel_stats = pd.DataFrame(channel_stats_list)
            st.write(df_channel_stats)

            # Visualizations for comparison
            fig_subscribers = px.bar(
                df_channel_stats, 
                x='channelTitle', 
                y='subscriberCount', 
                title='Subscribers Comparison'
            )
            fig_views = px.bar(
                df_channel_stats, 
                x='channelTitle', 
                y='viewCount', 
                title='View Count Comparison'
            )
            fig_videos = px.bar(
                df_channel_stats, 
                x='channelTitle', 
                y='videoCount', 
                title='Video Count Comparison'
            )

            st.plotly_chart(fig_subscribers)
            st.plotly_chart(fig_views)
            st.plotly_chart(fig_videos)
        else:
            st.error("No valid channel statistics to display.")

def main():
    st.title("YouTube Channel Analysis")

    # Sidebar for navigation and spam detection toggle
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Channel Insights", "Sentiment Analysis", "Channel Comparison"])

    # Sidebar spam filter toggle
    filter_spam = st.sidebar.checkbox("Filter spam comments", value=True)

    # Initialize session state to store our data
    if 'df_comments' not in st.session_state:
        st.session_state.df_comments = None
    if 'df_videos' not in st.session_state:
        st.session_state.df_videos = None
    if 'channel_stats' not in st.session_state:
        st.session_state.channel_stats = None

    if page == "Home":
        channel_id = st.text_input("Enter YouTube Channel ID:")
        
        if channel_id:
            if st.button("Analyze Channel"):
                with st.spinner("Fetching channel data and analyzing..."):
                    videos = get_channel_videos(channel_id)
                    channel_stats = get_channel_statistics(channel_id)
                    
                    if videos and channel_stats:
                        all_comments = []
                        video_titles = []
                        video_sentiments = []
                        video_stats = []

                        for video in videos:
                            video_id = video['snippet']['resourceId']['videoId']
                            video_title = video['snippet']['title']
                            comments = get_video_comments(video_id)
                            
                            # Fetch video statistics
                            stats = get_video_statistics(video_id)
                            
                            if comments:
                                # Check whether to filter spam comments
                                if filter_spam:
                                    non_spam_comments = filter_spam_comments(comments)
                                else:
                                    non_spam_comments = comments
                                
                                sentiments = analyze_sentiment(non_spam_comments)
                                all_comments.extend(non_spam_comments)
                                video_titles.extend([video_title] * len(non_spam_comments))
                                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
                            else:
                                avg_sentiment = 0

                            video_stats.append({
                                'Video Title': video_title,
                                'View Count': stats.get('viewCount', 0),
                                'Like Count': stats.get('likeCount', 0),
                                'Comment Count': stats.get('commentCount', 0),
                                'Average Sentiment': avg_sentiment
                            })
                        
                        # Create dataframes for comments and video statistics
                        df_comments = pd.DataFrame({
                            'Comment': all_comments,
                            'Video Title': video_titles,
                            'Sentiment': analyze_sentiment(all_comments)
                        })

                        df_videos = pd.DataFrame(video_stats)

                        # Store the data in session state
                        st.session_state.df_comments = df_comments
                        st.session_state.df_videos = df_videos
                        st.session_state.channel_stats = channel_stats

                        st.success("Analysis complete! Navigate to other pages to view insights.")

    

    elif page == "Channel Insights" and st.session_state.df_videos is not None:
        visualization_page(st.session_state.df_comments, st.session_state.df_videos, st.session_state.channel_stats)

    elif page == "Sentiment Analysis" and st.session_state.df_comments is not None:
        sentiment_analysis_page(st.session_state.df_comments, st.session_state.df_videos)
    
    elif page == "Channel Comparison":
        channel_comparison_page()

    else:
        st.write("Please enter a valid YouTube channel ID and analyze the channel.")

if __name__ == "__main__":
    main()
