import os
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

# Locate the .env file at the root level of Knowledge_Atlas
base_dir = os.path.dirname(__file__)
load_dotenv(dotenv_path=os.path.join(base_dir, "../../../.env"))
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def load_json(filepath):
    """Helper function to read JSON files."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Helper function to write data into JSON format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def search_unsplash(query, room_type):
    """Fetch image metadata from Unsplash API and parse it according to the contract."""
    if not UNSPLASH_ACCESS_KEY:
        print("❌ Error: UNSPLASH_ACCESS_KEY is not set. Please check your .env file.")
        return []

    url = "https://api.unsplash.com/search/photos"
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "query": query,
        "per_page": 30,  # Number of images per page (Max 30)
        "page": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        # Monitor Demo tier rate limits
        remaining = response.headers.get("X-Ratelimit-Remaining")
        if remaining:
            print(f"    [API Rate Limit: {remaining}/50 requests remaining]")

        if response.status_code != 200:
            print(f"    ❌ API Error (Status Code: {response.status_code})")
            return []

        data = response.json()
        results = data.get("results", [])
        
        parsed_records = []
        for img in results:
            # Enforce contract-compliant field formatting for strict provenance
            record = {
                "url": img.get("urls", {}).get("regular"),
                "thumbnail_url": img.get("urls", {}).get("thumb"),
                "title": img.get("alt_description") or img.get("description") or "Untitled",
                "photographer": img.get("user", {}).get("name") or "Unknown",
                "source_name": "Unsplash",
                "source_page_url": img.get("links", {}).get("html"),
                "license": "Unsplash License (free, attribution appreciated)",
                "space_type": room_type,
                "search_query": query,
                "collected_at": datetime.utcnow().isoformat() + "Z"  # ISO 8601 Format
            }
            parsed_records.append(record)
            
        return parsed_records

    except Exception as e:
        print(f"    ❌ Network or Parsing Exception: {e}")
        return []

def main():
    space_types_path = os.path.join(base_dir, "../data/space_types.json")
    output_path = os.path.join(base_dir, "../data/search_results.json")
    
    if not os.path.exists(space_types_path):
        print(f"❌ Error: Required input file missing at {space_types_path}")
        return
        
    space_types = load_json(space_types_path)
    all_results = []
    
    print("🚀 Starting Image Collection Pipeline...")
    
    # Iterate through the 15 required room categories
    for room_type, details in space_types.items():
        search_terms = details["search_terms"]
        print(f"\n📂 Space Type: {room_type}")
        
        for term in search_terms:
            print(f"  🔍 Executing Query: '{term}'")
            records = search_unsplash(term, room_type)
            
            if not records:
                print(f"    ⚠️ Warning: No results returned or query skipped.")
            else:
                print(f"    ✅ Success: Captured {len(records)} image records")
                all_results.extend(records)
            
            # Rate Limiting: Introduce delay to safeguard against server bans (Contract Requirement)
            time.sleep(2) 
            
    save_json(all_results, output_path)
    print(f"\n✨ Pipeline Execution Completed! Total Records Collected: {len(all_results)}")
    print(f"💾 Saved Output to: {output_path}")

if __name__ == "__main__":
    main()