from flask import Flask, render_template, request, jsonify
import googleapiclient.discovery

app = Flask(__name__)

YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"  # Replace with your actual API key

def scrape_yt_data(url, data_type):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    video_id = None
    channel_id = None

    # Extract Video ID
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[-1].split("&")[0]
    elif "/channel/" in url:
        channel_id = url.split("/channel/")[-1].split("/")[0]
    else:
        return {"error": "Invalid URL format"}

    # Get Channel ID from Video (if needed)
    if video_id and data_type == 'subscribers':
        try:
            video_request = youtube.videos().list(part="snippet", id=video_id)
            video_response = video_request.execute()

            if "items" not in video_response or not video_response["items"]:
                return {"error": "Video not found"}
            
            channel_id = video_response["items"][0]["snippet"]["channelId"]

        except Exception as e:
            return {"error": f"Error fetching channel ID: {str(e)}"}

    # Get Subscribers
    if channel_id and data_type == 'subscribers':
        try:
            channel_request = youtube.channels().list(part="statistics", id=channel_id)
            channel_response = channel_request.execute()

            if "items" in channel_response and channel_response["items"]:
                return {"subscribers": channel_response["items"][0]["statistics"].get("subscriberCount", "Data not available")}
            else:
                return {"error": "Channel not found"}

        except Exception as e:
            return {"error": f"Error retrieving subscriber count: {str(e)}"}

    # Get Comments, Likes, or Views
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

        elif data_type in ['likes', 'views']:
            try:
                request = youtube.videos().list(part="statistics", id=video_id)
                response = request.execute()
                stats = response.get("items", [])[0]["statistics"]
                return {data_type: stats.get("likeCount" if data_type == 'likes' else "viewCount", "Data not available")}
            except Exception as e:
                return {"error": f"Error retrieving {data_type}: {str(e)}"}

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
