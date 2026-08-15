import os
import json
import requests
from datetime import datetime

class SocialMediaAutoPoster:
    def __init__(self):
        self.tokens = self.load_tokens()
        self.content = self.load_content()
    
    def load_tokens(self):
        """Environment variables se tokens load karein"""
        return {
            'facebook': {
                'token': os.environ.get('FACEBOOK_TOKEN'),
                'page_id': os.environ.get('FACEBOOK_PAGE_ID')
            },
            'instagram': {
                'token': os.environ.get('INSTAGRAM_TOKEN'),
                'user_id': os.environ.get('INSTAGRAM_USER_ID')
            },
            'linkedin': {
                'token': os.environ.get('LINKEDIN_TOKEN'),
                'person_id': os.environ.get('LINKEDIN_PERSON_ID')
            },
            'twitter': {
                'api_key': os.environ.get('TWITTER_API_KEY'),
                'api_secret': os.environ.get('TWITTER_API_SECRET'),
                'access_token': os.environ.get('TWITTER_ACCESS_TOKEN'),
                'access_secret': os.environ.get('TWITTER_ACCESS_SECRET')
            }
        }
    
    def load_content(self):
        """content.json se post content load karein"""
        try:
            with open('content.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default content
            return {
                "text": "🚀 Digital Marketing Tips!\n\nAaj ka tip: Consistent posting se growth hoti hai!\n\n#DigitalMarketing #SocialMedia #Growth",
                "image_url": "https://picsum.photos/800/600",
                "hashtags": "#automation #socialmedia #free"
            }
    
    def post_to_facebook(self):
        """Facebook Page par post karein"""
        if not self.tokens['facebook']['token']:
            return "No Facebook token"
        
        url = f"https://graph.facebook.com/v18.0/{self.tokens['facebook']['page_id']}/feed"
        params = {
            'message': f"{self.content['text']}\n\n{self.content['hashtags']}",
            'access_token': self.tokens['facebook']['token']
        }
        
        # Image ke saath post
        if self.content.get('image_url'):
            params['link'] = self.content['image_url']
        
        try:
            response = requests.post(url, params=params)
            return response.json()
        except Exception as e:
            return f"Facebook Error: {str(e)}"
    
    def post_to_instagram(self):
        """Instagram par post karein"""
        if not self.tokens['instagram']['token']:
            return "No Instagram token"
        
        ig_user_id = self.tokens['instagram']['user_id']
        
        # Step 1: Media upload karein
        media_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
        media_params = {
            'image_url': self.content['image_url'],
            'caption': f"{self.content['text']}\n\n{self.content['hashtags']}",
            'access_token': self.tokens['instagram']['token']
        }
        
        try:
            media_response = requests.post(media_url, params=media_params)
            media_data = media_response.json()
            
            if 'id' not in media_data:
                return f"Instagram Upload Error: {media_data}"
            
            # Step 2: Media publish karein
            creation_id = media_data['id']
            publish_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
            publish_params = {
                'creation_id': creation_id,
                'access_token': self.tokens['instagram']['token']
            }
            
            publish_response = requests.post(publish_url, params=publish_params)
            return publish_response.json()
            
        except Exception as e:
            return f"Instagram Error: {str(e)}"
    
    def post_to_linkedin(self):
        """LinkedIn par post karein"""
        if not self.tokens['linkedin']['token']:
            return "No LinkedIn token"
        
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            'Authorization': f"Bearer {self.tokens['linkedin']['token']}",
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        payload = {
            'author': f"urn:li:person:{self.tokens['linkedin']['person_id']}",
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': f"{self.content['text']}\n\n{self.content['hashtags']}"
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            return f"LinkedIn Error: {str(e)}"
    
    def post_to_twitter(self):
        """Twitter/X par post karein"""
        if not self.tokens['twitter']['api_key']:
            return "No Twitter tokens"
        
        # Twitter API v2
        url = "https://api.twitter.com/2/tweets"
        headers = {
            'Authorization': f"Bearer {self.tokens['twitter']['access_token']}",
            'Content-Type': 'application/json'
        }
        
        payload = {
            'text': f"{self.content['text'][:280]}"  # Twitter limit 280 chars
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            return f"Twitter Error: {str(e)}"
    
    def run_all(self):
        """Sab platforms par post karein"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'content': self.content['text'][:100],
            'platforms': {}
        }
        
        # Facebook
        print("📘 Facebook par post ho raha hai...")
        results['platforms']['facebook'] = self.post_to_facebook()
        
        # Instagram
        print("📸 Instagram par post ho raha hai...")
        results['platforms']['instagram'] = self.post_to_instagram()
        
        # LinkedIn
        print("💼 LinkedIn par post ho raha hai...")
        results['platforms']['linkedin'] = self.post_to_linkedin()
        
        # Twitter
        print("🐦 Twitter par post ho raha hai...")
        results['platforms']['twitter'] = self.post_to_twitter()
        
        # Results save karein
        with open('post_logs.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(results, indent=2) + '\n')
        
        print("\n✅ Posting Complete!")
        print(json.dumps(results, indent=2))
        
        return results

if __name__ == "__main__":
    poster = SocialMediaAutoPoster()
    poster.run_all()
