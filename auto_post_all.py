import os
import json
import requests
from datetime import datetime
import time

class AllSocialMediaPoster:
    def __init__(self):
        self.tokens = self.load_tokens()
        self.content = self.load_content()
    
    def load_tokens(self):
        """Sabhi platforms ke tokens"""
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
            'youtube': {
                'token': os.environ.get('YOUTUBE_TOKEN'),
                'channel_id': os.environ.get('YOUTUBE_CHANNEL_ID')
            },
            'pinterest': {
                'token': os.environ.get('PINTEREST_TOKEN'),
                'board_id': os.environ.get('PINTEREST_BOARD_ID')
            },
            'tiktok': {
                'token': os.environ.get('TIKTOK_TOKEN'),
                'user_id': os.environ.get('TIKTOK_USER_ID')
            }
        }
    
    def load_content(self):
        """content.json se content load karein"""
        with open('content.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # ============ FACEBOOK ============
    def post_to_facebook(self):
        """Facebook Page par post"""
        try:
            if not self.tokens['facebook']['token']:
                return "❌ Facebook token missing"
            
            url = f"https://graph.facebook.com/v18.0/{self.tokens['facebook']['page_id']}/feed"
            
            params = {
                'message': f"{self.content['text']}\n\n{self.content['hashtags']}",
                'access_token': self.tokens['facebook']['token']
            }
            
            # Image post
            if self.content.get('image_url'):
                params['link'] = self.content['image_url']
            
            response = requests.post(url, params=params)
            data = response.json()
            
            if 'id' in data:
                return f"✅ Facebook Success: {data['id']}"
            else:
                return f"❌ Facebook Error: {data}"
                
        except Exception as e:
            return f"❌ Facebook Exception: {str(e)}"
    
    # ============ INSTAGRAM ============
    def post_to_instagram(self):
        """Instagram par post"""
        try:
            if not self.tokens['instagram']['token']:
                return "❌ Instagram token missing"
            
            ig_user_id = self.tokens['instagram']['user_id']
            
            # Step 1: Media container create karein
            media_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
            media_params = {
                'image_url': self.content['image_url'],
                'caption': f"{self.content['text']}\n\n{self.content['hashtags']}",
                'access_token': self.tokens['instagram']['token']
            }
            
            media_response = requests.post(media_url, params=media_params)
            media_data = media_response.json()
            
            if 'id' not in media_data:
                return f"❌ Instagram Upload Error: {media_data}"
            
            # Step 2: Publish karein
            creation_id = media_data['id']
            publish_url = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
            publish_params = {
                'creation_id': creation_id,
                'access_token': self.tokens['instagram']['token']
            }
            
            publish_response = requests.post(publish_url, params=publish_params)
            publish_data = publish_response.json()
            
            if 'id' in publish_data:
                return f"✅ Instagram Success: {publish_data['id']}"
            else:
                return f"❌ Instagram Publish Error: {publish_data}"
                
        except Exception as e:
            return f"❌ Instagram Exception: {str(e)}"
    
    # ============ LINKEDIN ============
    def post_to_linkedin(self):
        """LinkedIn par post"""
        try:
            if not self.tokens['linkedin']['token']:
                return "❌ LinkedIn token missing"
            
            url = "https://api.linkedin.com/v2/ugcPosts"
            headers = {
                'Authorization': f"Bearer {self.tokens['linkedin']['token']}",
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            # Image ke saath post
            if self.content.get('image_url'):
                # Pehle image register karein
                register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
                register_payload = {
                    "registerUploadRequest": {
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                        "owner": f"urn:li:person:{self.tokens['linkedin']['person_id']}",
                        "serviceRelationships": [{
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }]
                    }
                }
                
                register_response = requests.post(register_url, headers=headers, json=register_payload)
                register_data = register_response.json()
                
                if 'value' in register_data:
                    upload_url = register_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
                    asset = register_data['value']['asset']
                    
                    # Image upload karein
                    image_response = requests.get(self.content['image_url'])
                    upload_response = requests.post(upload_url, headers={
                        'Authorization': f"Bearer {self.tokens['linkedin']['token']}",
                        'Content-Type': 'image/jpeg'
                    }, data=image_response.content)
                    
                    # Post with image
                    payload = {
                        'author': f"urn:li:person:{self.tokens['linkedin']['person_id']}",
                        'lifecycleState': 'PUBLISHED',
                        'specificContent': {
                            'com.linkedin.ugc.ShareContent': {
                                'shareCommentary': {
                                    'text': f"{self.content['text']}\n\n{self.content['hashtags']}"
                                },
                                'shareMediaCategory': 'IMAGE',
                                'media': [{
                                    'status': 'READY',
                                    'description': {
                                        'text': self.content['text'][:100]
                                    },
                                    'media': asset,
                                    'title': {
                                        'text': self.content['text'][:50]
                                    }
                                }]
                            }
                        },
                        'visibility': {
                            'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                        }
                    }
                else:
                    return f"❌ LinkedIn Image Register Error: {register_data}"
            else:
                # Text only post
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
            
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            if 'id' in data:
                return f"✅ LinkedIn Success: {data['id']}"
            else:
                return f"❌ LinkedIn Error: {data}"
                
        except Exception as e:
            return f"❌ LinkedIn Exception: {str(e)}"
    
    # ============ YOUTUBE ============
    def post_to_youtube(self):
        """YouTube par video post (agar video hai)"""
        try:
            if not self.tokens['youtube']['token']:
                return "❌ YouTube token missing"
            
            # Agar video file nahi hai to community post karein
            if not self.content.get('video_path'):
                # Community tab post (agar enabled hai)
                url = "https://www.googleapis.com/youtube/v3/commentThreads"
                # Ya simple video upload agar file hai
                return "⚠️ YouTube: Video file required for upload"
            
            url = "https://www.googleapis.com/upload/youtube/v3/videos"
            headers = {
                'Authorization': f"Bearer {self.tokens['youtube']['token']}",
                'Content-Type': 'application/json'
            }
            
            params = {
                'uploadType': 'multipart',
                'part': 'snippet,status'
            }
            
            snippet = {
                'title': self.content.get('title', 'My Video'),
                'description': f"{self.content['text']}\n\n{self.content['hashtags']}",
                'tags': self.content.get('tags', ['social', 'media']),
                'categoryId': '22'
            }
            
            status = {
                'privacyStatus': 'public'
            }
            
            files = {
                'media': open(self.content['video_path'], 'rb')
            }
            
            data = {
                'snippet': json.dumps(snippet),
                'status': json.dumps(status)
            }
            
            response = requests.post(url, headers=headers, params=params, files=files, data=data)
            data = response.json()
            
            if 'id' in data:
                return f"✅ YouTube Success: https://youtube.com/watch?v={data['id']}"
            else:
                return f"❌ YouTube Error: {data}"
                
        except Exception as e:
            return f"❌ YouTube Exception: {str(e)}"
    
    # ============ PINTEREST ============
    def post_to_pinterest(self):
        """Pinterest par pin post"""
        try:
            if not self.tokens['pinterest']['token']:
                return "❌ Pinterest token missing"
            
            url = "https://api.pinterest.com/v5/pins"
            headers = {
                'Authorization': f"Bearer {self.tokens['pinterest']['token']}",
                'Content-Type': 'application/json'
            }
            
            payload = {
                'board_id': self.tokens['pinterest']['board_id'],
                'title': self.content.get('title', self.content['text'][:50]),
                'description': f"{self.content['text']}\n\n{self.content['hashtags']}",
                'media_source': {
                    'source_type': 'image_url',
                    'url': self.content['image_url']
                },
                'link': self.content.get('link', '')
            }
            
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            if 'id' in data:
                return f"✅ Pinterest Success: {data['id']}"
            else:
                return f"❌ Pinterest Error: {data}"
                
        except Exception as e:
            return f"❌ Pinterest Exception: {str(e)}"
    
    # ============ TIKTOK ============
    def post_to_tiktok(self):
        """TikTok par video post"""
        try:
            if not self.tokens['tiktok']['token']:
                return "❌ TikTok token missing"
            
            if not self.content.get('video_path'):
                return "⚠️ TikTok: Video file required"
            
            # Step 1: Video upload initialize karein
            init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
            headers = {
                'Authorization': f"Bearer {self.tokens['tiktok']['token']}",
                'Content-Type': 'application/json'
            }
            
            init_payload = {
                "post_info": {
                    "title": self.content.get('title', 'My Video'),
                    "privacy_level": "PUBLIC",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": os.path.getsize(self.content['video_path']),
                    "chunk_size": 10000000,
                    "total_chunk_count": 1
                }
            }
            
            init_response = requests.post(init_url, headers=headers, json=init_payload)
            init_data = init_response.json()
            
            if 'data' not in init_data:
                return f"❌ TikTok Init Error: {init_data}"
            
            upload_url = init_data['data']['upload_url']
            publish_id = init_data['data']['publish_id']
            
            # Step 2: Video upload karein
            with open(self.content['video_path'], 'rb') as video_file:
                upload_response = requests.put(
                    upload_url,
                    headers={'Content-Type': 'video/mp4'},
                    data=video_file
                )
            
            # Step 3: Publish karein
            publish_url = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
            publish_payload = {
                "publish_id": publish_id
            }
            
            publish_response = requests.post(publish_url, headers=headers, json=publish_payload)
            
            return f"✅ TikTok Upload Complete: {publish_id}"
            
        except Exception as e:
            return f"❌ TikTok Exception: {str(e)}"
    
    # ============ RUN ALL ============
    def run_all(self):
        """Sabhi platforms par post karein"""
        print("=" * 50)
        print("🚀 SOCIAL MEDIA AUTO POST START")
        print("=" * 50)
        print(f"📅 Time: {datetime.now().isoformat()}")
        print(f"📝 Content: {self.content['text'][:100]}...")
        print("=" * 50)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'platforms': {}
        }
        
        # Facebook
        print("\n📘 Facebook...")
        fb_result = self.post_to_facebook()
        results['platforms']['facebook'] = fb_result
        print(fb_result)
        time.sleep(2)
        
        # Instagram
        print("\n📸 Instagram...")
        ig_result = self.post_to_instagram()
        results['platforms']['instagram'] = ig_result
        print(ig_result)
        time.sleep(2)
        
        # LinkedIn
        print("\n💼 LinkedIn...")
        li_result = self.post_to_linkedin()
        results['platforms']['linkedin'] = li_result
        print(li_result)
        time.sleep(2)
        
        # Pinterest
        print("\n📌 Pinterest...")
        pin_result = self.post_to_pinterest()
        results['platforms']['pinterest'] = pin_result
        print(pin_result)
        time.sleep(2)
        
        # YouTube (only if video)
        print("\n🎥 YouTube...")
        yt_result = self.post_to_youtube()
        results['platforms']['youtube'] = yt_result
        print(yt_result)
        time.sleep(2)
        
        # TikTok (only if video)
        print("\n🎵 TikTok...")
        tt_result = self.post_to_tiktok()
        results['platforms']['tiktok'] = tt_result
        print(tt_result)
        
        # Results save karein
        with open('post_logs.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(results, indent=2) + '\n')
        
        print("\n" + "=" * 50)
        print("✅ POSTING COMPLETE!")
        print("=" * 50)
        
        return results

if __name__ == "__main__":
    poster = AllSocialMediaPoster()
    poster.run_all()
