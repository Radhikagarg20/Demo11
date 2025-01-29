from flask import Flask, render_template, request, jsonify
import googleapiclient.discovery

app = Flask(__name__)

# Replace with your actual YouTube API key
YOUTUBE_API_KEY = "AIzaSyCf4r6vIlVsNcmaEaPS-mm8KARh9KS77sg"

def scrape_yt_data(url, data_type):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    video_id, channel_id = None, None

    # Extract video ID or channel ID from URL
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[-1].split("&")[0]
    elif "/channel/" in url:
        channel_id = url.split("/channel/")[-1].split("/")[0]
    else:
        return {"error": "Invalid URL"}

    # If user asks for subscribers from a video URL, first get the channel ID
    if video_id and data_type == "subscribers":
        try:
            video_request = youtube.videos().list(part="snippet", id=video_id)
            video_response = video_request.execute()

            if "items" in video_response and len(video_response["items"]) > 0:
                channel_id = video_response["items"][0]["snippet"]["channelId"]
            else:
                return {"error": "Could not retrieve channel ID from video"}

        except Exception as e:
            return {"error": f"Error retrieving channel ID: {str(e)}"}

    # Fetch subscriber count if channel ID is available
    if channel_id and data_type == "subscribers":
        try:
            request = youtube.channels().list(part="statistics", id=channel_id)
            response = request.execute()

            if "items" in response and len(response["items"]) > 0:
                return {"subscribers": response["items"][0]["statistics"].get("subscriberCount", "Data not available")}
            else:
                return {"error": "Channel not found or data unavailable"}

        except Exception as e:
            return {"error": f"Error retrieving subscriber count: {str(e)}"}

    # Fetch video-related data (likes, views, comments)
    if video_id:
        if data_type == 'comments':
            try:
                request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=100)
                response = request.execute()
                return [{
                    "author": item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                    "text": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                } for item in response.get("items", [])]
            except Exception as e:
                return {"error": f"Error retrieving comments: {str(e)}"}

        elif data_type == 'likes':
            try:
                request = youtube.videos().list(part="statistics", id=video_id)
                response = request.execute()
                return {"likes": response.get("items", [])[0]["statistics"]["likeCount"]}
            except Exception as e:
                return {"error": f"Error retrieving likes: {str(e)}"}

        elif data_type == 'views': 
            try:
                request = youtube.videos().list(part="statistics", id=video_id)
                response = request.execute()
                return {"views": response.get("items", [])[0]["statistics"]["viewCount"]}
            except Exception as e:
                return {"error": f"Error retrieving views: {str(e)}"}

    return {"error": "Invalid request"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    data_type = request.form['data_type']
    result = scrape_yt_data(url, data_type)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
