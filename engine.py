import os
import json
import urllib.request
import datetime
import json
import urllib.request
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Skipping .env loading.")

def get_youtube_titles(query="Italian food", order="viewCount", timeframe="All Time"):
    # Try YouTube API first
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if api_key:
        try:
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            
            published_after_param = ""
            if timeframe == "Last 30 Days":
                date_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
                published_after_param = f"&publishedAfter={date_ago.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            elif timeframe == "This Year":
                date_ago = datetime.datetime.utcnow() - datetime.timedelta(days=365)
                published_after_param = f"&publishedAfter={date_ago.strftime('%Y-%m-%dT%H:%M:%SZ')}"

            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=10&q={encoded_query}&type=video&order={order}{published_after_param}&key={api_key}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                video_ids = []
                video_details = []
                for item in data.get('items', []):
                    vid = item['id'].get('videoId', '')
                    if vid:
                        video_ids.append(vid)
                        video_details.append({
                            "id": vid,
                            "title": item['snippet']['title'],
                            "channel": item['snippet']['channelTitle'],
                            "url": f"https://www.youtube.com/watch?v={vid}",
                            "views": "N/A"
                        })
                
                # Fetch view counts
                if video_ids:
                    stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={','.join(video_ids)}&key={api_key}"
                    stats_req = urllib.request.Request(stats_url)
                    with urllib.request.urlopen(stats_req) as stats_response:
                        stats_data = json.loads(stats_response.read().decode())
                        for item in stats_data.get('items', []):
                            vid = item['id']
                            views = item['statistics'].get('viewCount', '0')
                            try:
                                formatted_views = f"{int(views):,}"
                            except ValueError:
                                formatted_views = views
                            for detail in video_details:
                                if detail['id'] == vid:
                                    detail['views'] = formatted_views
                
                if video_details:
                    print(f"Successfully fetched titles from YouTube API for query: {query}")
                    return video_details
        except Exception as e:
            print(f"YouTube API failed: {e}. Falling back...")
    
    # Fallback: public RSS/Atom feed or mocked payload
    print("Using fallback payload for YouTube titles...")
    # Mocked recent viral titles for "Italian food"
    return [
        {"title": "I put KETCHUP on pasta in Italy and this happened...", "channel": "@ViralFoodHacks", "url": "https://youtube.com/watch?v=mock1", "views": "4,200,000"},
        {"title": "AUTHENTIC Carbonara with Heavy Cream & Bacon?!", "channel": "@ChefReacts", "url": "https://youtube.com/watch?v=mock2", "views": "3,100,000"},
        {"title": "Gordon Ramsay's 10 Minute Ultimate Italian Meatballs", "channel": "@GordonRamsay", "url": "https://youtube.com/watch?v=mock3", "views": "2,800,000"},
        {"title": "Trying the viral one-pan feta pasta bake!", "channel": "@TrendyEats", "url": "https://youtube.com/watch?v=mock4", "views": "1,500,000"},
        {"title": "Real Italian Grandma reacts to American Pizza", "channel": "@NonnaReacts", "url": "https://youtube.com/watch?v=mock5", "views": "1,200,000"},
        {"title": "I broke spaghetti in front of an Italian chef", "channel": "@PrankChef", "url": "https://youtube.com/watch?v=mock6", "views": "950,000"},
        {"title": "Creamy Garlic Parmesan Fettuccine Alfredo", "channel": "@EasyRecipes", "url": "https://youtube.com/watch?v=mock7", "views": "850,000"},
        {"title": "How to make the BEST Chicken Parm", "channel": "@CookingWithBob", "url": "https://youtube.com/watch?v=mock8", "views": "720,000"},
        {"title": "Secret ingredient for perfect Bolognese (It's milk?)", "channel": "@FoodScience", "url": "https://youtube.com/watch?v=mock9", "views": "600,000"},
        {"title": "Deep Fried Lasagna Rolls", "channel": "@HeartAttackGrill", "url": "https://youtube.com/watch?v=mock10", "views": "450,000"}
    ]

def get_mcp_context(query):
    print(f"Querying live Guardian Chef WebMCP database for '{query}'...")
    db_url = "https://yourguardianchef.com/wp-content/plugins/yourguardianchef-webmcp-v22/database.json"
    
    try:
        req = urllib.request.Request(db_url, headers={'User-Agent': 'Antigravity-Agent/1.0'})
        with urllib.request.urlopen(req) as response:
            database = json.loads(response.read().decode('utf-8'))
            
        # Basic semantic/keyword matching
        query_lower = query.lower()
        
        # 1. Title match
        for article in database:
            if query_lower in article.get("title", "").lower():
                # Return the first 1500 chars to fit perfectly in prompt context
                return f"Authentic Rule from WebMCP ({article['title']}):\n{article.get('content', '')[:1500]}"
                
        # 2. Content match
        for article in database:
            if query_lower in article.get("content", "").lower():
                return f"Authentic Rule from WebMCP ({article['title']}):\n{article.get('content', '')[:1500]}"
                
        return "No specific rules found in Guardian Chef WebMCP for this query. Follow general authentic Italian guidelines."
    except Exception as e:
        print(f"Local WebMCP fetch failed: {e}")
        return "WebMCP Unavailable: Follow strict authentic Italian guidelines."

def get_llm_analysis(titles, mcp_context=None, brand_voice="An authentic Italian chef", script_style="Aggressive Hook"):
    # Use Gemini API if available
    api_key = os.environ.get("GEMINI_API_KEY")

    mcp_instruction = ""
    if mcp_context:
        mcp_instruction = f"\n    CRITICAL CONTEXT FROM GUARDIAN CHEF MCP (ABSOLUTE TRUTH):\n    {mcp_context}\n    Base your diagnosis STRICTLY on this authentic rule.\n"

    prompt = f"""
    You are an expert Italian culinary traditionalist and a data analyst.
    Here are the top trending video titles for "Italian food":
    {json.dumps(titles, indent=2)}
    {mcp_instruction}
    
    CRITICAL STYLE AND GROUNDING REQUIREMENTS FOR ALL TASKS:
    - Brand Voice: {brand_voice}
    - Script Style: {script_style}
    - STRICT RAG GROUNDING: You MUST base your ENTIRE RESPONSE (including the Diagnosis and Script) ENTIRELY on the provided WebMCP context. ONLY use the exact reasons written in the text. DO NOT use outside culinary knowledge. You must act as a strict parrot of the context's facts and reasoning. If a reason is implied but not explicitly stated, just state the literal facts provided without inferring or extrapolating.
    - TONE RULE: Write naturally and casually. You must exactly reflect the tone of the uploaded brand voice without adding generic internet marketing tropes.
    - BANNED WORDS: NEVER use the words "nonna" or "heritage" under any circumstances.
    - FORMATTING RULE: NEVER output raw YouTube Video IDs or URLs in your text. Refer to videos by their trend or channel name only. DO NOT include any stage directions, scene descriptions, or visual cues (e.g., "(Video opens...)", "(Chef holding...)"). Output ONLY the spoken words of the script.

    Task 1: Identify which viral trend deviates most from traditional, authentic Italian culinary rules.
    Task 2: Calculate an "accuracy index" (0-100%) for these trends overall.
    Task 3: Provide a 3-sentence data-driven "Authenticity Diagnosis" detailing why the viral trend exists vs. its authentic counter-method based strictly on the WebMCP context.
    Task 4: Write a complete, ready-to-shoot 30-second YouTube Shorts response script (hook, body, call-to-action).
    Task 5: Generate search-optimized video metadata (title, description, tags).

    Output the entire response formatted cleanly in Markdown.
    """

    if api_key:
        models_to_try = ["gemini-1.5-flash-latest", "gemini-1.5-flash-8b-latest", "gemini-2.5-flash", "gemini-2.0-flash"]
        for i, model in enumerate(models_to_try):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode())
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"Successfully generated analysis using {model}.")
                    return text
            except urllib.error.HTTPError as e:
                error_body = e.read().decode()
                if e.code in [503, 429] and i < len(models_to_try) - 1:
                    print(f"Model {model} returned {e.code} (High Demand or Rate Limit). Trying next model...")
                    continue
                raise Exception(f"Gemini API HTTP Error {e.code} on {model}: {error_body}")
            except Exception as e:
                if i < len(models_to_try) - 1:
                    continue
                raise Exception(f"Gemini API failed: {str(e)}")
    else:
        print("GEMINI_API_KEY not found. Using fallback mock analysis.")

    # Fallback response
    return """# Authenticity Diagnosis

**Viral Trend Identified**: The use of heavy cream and bacon in Carbonara, as well as breaking spaghetti.
**Accuracy Index**: 30% Authentic

**Diagnosis**: The data shows a persistent virality in Americanized Italian dishes relying on excess dairy and shortcut ingredients for visual shock value rather than traditional technique. These trends prioritize immediate rich flavors and convenience, starkly contrasting with the authentic method which relies on the emulsion of starchy pasta water, Pecorino Romano, and guanciale to achieve creaminess. By reacting to these deviations, creators manufacture outrage and engagement, moving further away from genuine Italian culinary heritage.

## YouTube Shorts Production Brief

### Script (30 seconds)
**Hook (0-5s)**: (Chef holding a carton of heavy cream, looking disgusted) "If you put this in your Carbonara, we can't be friends."
**Body (5-20s)**: "The internet is obsessed with cream and bacon. But real Roman Carbonara only needs four things: Guanciale, Pecorino, egg yolks, and black pepper. The magic is in the technique—emulsifying the fat with pasta water away from the heat."
**Call-to-Action (20-30s)**: "Stop the culinary crimes! Hit subscribe to learn how to cook like a real Italian nonna."

### Video Metadata
**Title**: Stop Putting CREAM in Carbonara! 🛑🍝 #AuthenticItalian #Cooking #Shorts
**Description**: Heavy cream in carbonara is a crime! Learn the authentic Roman way to make the creamiest pasta using only 4 ingredients. Guanciale, eggs, pecorino, and pepper. No cream allowed!
**Tags**: #Carbonara #ItalianFood #AuthenticItalian #Pasta #CookingHacks #ItalianChef
"""

def main(query="Italian food", order="viewCount", timeframe="All Time", brand_voice="An authentic Italian chef", script_style="Aggressive Hook"):
    print("Starting Intelligence to Action pipeline...")
    
    # 1. SIGNAL IN
    print(f"Fetching signals for '{query}'...")
    titles = get_youtube_titles(query, order, timeframe)
    
    # 1.5. ENRICH SIGNAL
    print("Enriching signal via MCP...")
    mcp_context = get_mcp_context(query)
    
    # 2. INTELLIGENCE OUT
    print("Analyzing intelligence...")
    analysis = get_llm_analysis(titles, mcp_context=mcp_context, brand_voice=brand_voice, script_style=script_style)
    
    # 3. ACTION TAKEN
    output_file = "youtube_production_brief.md"
    print(f"Writing action plan to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(analysis)
    
    print("Pipeline complete. Brief generated successfully.")
    return titles

if __name__ == "__main__":
    main()
