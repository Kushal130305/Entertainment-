import time
import feedparser
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from keep_alive import keep_alive
from datetime import datetime
import pytz
import os

# Set up your Blogger API credentials and scopes
SCOPES = ['https://www.googleapis.com/auth/blogger']
creds = Credentials.from_authorized_user_file(os.environ.get('token.json'), SCOPES)
service = build('blogger', 'v3', credentials=creds, static_discovery=False)

# RSS feed URL
rss_feed_url = 'https://www.indiatv.in/rssnews/topstory.xml'
blog_id = os.environ.get('blog_id')

keep_alive()

# Initialize the latest post's title and ID to track
latest_post_title = ""
posted_entry_ids = set()  # Set to store posted entry IDs

# Function to create a new post on Blogger with an iframe and image
def create_blogger_post_with_iframe_and_image(title, iframe_code, image_url):
    post_body = {
        "kind": "blogger#post",
        "title": title,
        "content": f'{iframe_code}<div><img src="{image_url}" width="1" height="1"/></div>',
        "labels": ["Top News"]
    }

    request = service.posts().insert(blogId=blog_id, body=post_body)
    request.execute()

# Main loop to trigger new posts from RSS feed every 20 minutes
while True:
    feed = feedparser.parse(rss_feed_url)
    if feed.entries:
        entry = feed.entries[0]  # Get the latest entry
        title = entry.title
        entry_id = entry.id  # Extract a unique identifier for the entry
        content_url = entry.link
        description = entry.description
        image_start = description.find('<img src="') + len('<img src="')
        image_end = description.find('"', image_start)
        image_url = description[image_start:image_end]

        if entry_id not in posted_entry_ids:  # Check if the entry ID has been posted
            iframe_code = f'<iframe src="{content_url}" width="800" height="600" frameborder="0"></iframe>'
            create_blogger_post_with_iframe_and_image(title, iframe_code, image_url)
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))  # Replace 'Asia/Kolkata' with your desired timezone
            formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S %Z')
            print(f"Posted: {title} - {formatted_time}")
            latest_post_title = title
            posted_entry_ids.add(entry_id)  # Add the entry ID to the set of posted IDs
    
    time.sleep(20 * 60)  # Sleep for 20 minutes
