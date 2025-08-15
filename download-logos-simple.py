#!/usr/bin/env python3
import json
import urllib.request
import urllib.error
import os
from pathlib import Path
import time
from urllib.parse import urlparse
import re

# Read token list
with open('token-list.json', 'r') as f:
    token_list = json.load(f)

# Create directory
logo_dir = Path('./token-logo')
logo_dir.mkdir(exist_ok=True)

def sanitize_filename(filename):
    """Sanitize filename to be safe for filesystem"""
    return re.sub(r'[^a-zA-Z0-9\-_.]', '_', filename)

def get_extension_from_url(url):
    """Extract file extension from URL"""
    parsed = urlparse(url)
    path = parsed.path
    ext = os.path.splitext(path)[1]
    
    # Default extensions based on common image types
    if not ext:
        ext = '.png'  # Default to PNG
    elif ext.lower() not in ['.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif']:
        ext = '.png'  # Fallback to PNG for unknown extensions
    
    return ext

def download_file(url, filename):
    """Download file with different user agents and retry logic"""
    if not url:
        print(f"⚠️  Skipping {filename} - no logo URL")
        return False
    
    extension = get_extension_from_url(url)
    safe_filename = sanitize_filename(filename) + extension
    filepath = logo_dir / safe_filename
    
    # Skip if already exists
    if filepath.exists():
        print(f"✅ {safe_filename} already exists, skipping")
        return True
    
    print(f"⬇️  Downloading {url} -> {safe_filename}")
    
    # Try different user agents
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'curl/7.68.0',
        'wget/1.21.3'
    ]
    
    for i, user_agent in enumerate(user_agents):
        try:
            # Create request with headers
            req = urllib.request.Request(url)
            req.add_header('User-Agent', user_agent)
            req.add_header('Accept', 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8')
            req.add_header('Accept-Language', 'en-US,en;q=0.9')
            req.add_header('DNT', '1')
            req.add_header('Connection', 'keep-alive')
            
            # Download the file
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        f.write(response.read())
                    print(f"✅ Successfully downloaded {safe_filename}")
                    return True
                else:
                    if i == 0:  # Only print on first attempt
                        print(f"❌ Failed to download {url}: HTTP {response.status}")
                        
        except urllib.error.HTTPError as e:
            if i == 0:  # Only print on first attempt
                if e.code == 403:
                    print(f"❌ Access forbidden for {url}: {e.code}")
                elif e.code == 404:
                    print(f"❌ File not found for {url}: {e.code}")
                else:
                    print(f"❌ HTTP error for {url}: {e.code}")
        except urllib.error.URLError as e:
            if i == 0:  # Only print on first attempt
                print(f"❌ URL error for {url}: {str(e)}")
        except Exception as e:
            if i == 0:  # Only print on first attempt
                print(f"❌ Unexpected error for {url}: {str(e)}")
        
        # Small delay between retries
        if i < len(user_agents) - 1:
            time.sleep(0.5)
    
    return False

def main():
    print(f"🚀 Starting download of {len(token_list)} token logos...\n")
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    for i, token in enumerate(token_list):
        if token.get('logoUrl'):
            filename = token['symbol']
            
            if download_file(token['logoUrl'], filename):
                downloaded += 1
            else:
                failed += 1
        else:
            print(f"⚠️  No logo URL for {token['symbol']}")
            skipped += 1
        
        # Small delay to be respectful
        time.sleep(0.3)
        
        # Progress indicator
        if (i + 1) % 20 == 0:
            print(f"\n📊 Progress: {i + 1}/{len(token_list)} processed\n")
    
    print(f"\n📊 Final Summary:")
    print(f"✅ Downloaded: {downloaded}")
    print(f"⚠️  Skipped (no URL): {skipped}")
    print(f"❌ Failed: {failed}")
    
    # Count actual files in directory
    actual_files = len([f for f in logo_dir.iterdir() if f.is_file()])
    print(f"📁 Total files in {logo_dir}: {actual_files}")

if __name__ == "__main__":
    main()
