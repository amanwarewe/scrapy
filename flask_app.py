# from flask import Flask, request, jsonify
# import requests

# app = Flask(__name__)
# SCRAPYRT_API = "http://localhost:9080/crawl.json"

# @app.route("/run-spider")
# def run_spider():
#     keyword = request.args.get("keyword")
#     if not keyword:
#         return jsonify({"error": "keyword is required"}), 400

#     # Build the initial Reddit search URL using the keyword
#     reddit_search_url = f"https://www.reddit.com/search.json?q={keyword}&sort=relevance&limit=50"

#     # Build POST JSON payload
#     payload = {
#         "spider_name": "competitor_mentions",
#         "crawl_args": {"keyword": keyword},
#         "request": {"url": reddit_search_url}
#     }

#     # Send to Scrapyrt (port 9080)
#     try:
#         resp = requests.post(SCRAPYRT_API, json=payload)
#         return jsonify(resp.json())
#     except Exception as e:
#         return jsonify({"error": "Scrapyrt request failed", "details": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)




# from flask import Flask, request, jsonify
# import requests

# app = Flask(__name__)

# SCRAPYRT_API = "http://localhost:9080/crawl.json"

# @app.route("/run-spider", methods=["GET"])
# def run_spider():
#     spider = request.args.get("spider")
#     keyword = request.args.get("keyword")
#     url = request.args.get("url")
    
#     if not spider:
#         return jsonify({"error": "You must provide the spider name"}), 400

#     # Build JSON payload for Scrapyrt
#     payload = {"spider_name": spider}

#     # If keyword is provided, include it in crawl_args and build a URL for start
#     if keyword:
#         # many spiders take keyword-based start URLs
#         # you can customize this mapping per spider below
#         payload["crawl_args"] = {"keyword": keyword}
#         # If no custom URL, default starting point (could be overridden per spider)
#         if not url:
#             # you *might* build custom initial URL for certain spiders:
#             url = f"https://www.reddit.com/search.json?q={keyword}&sort=relevance&limit=50"

#     # If a URL parameter is provided, use it
#     if url:
#         payload["request"] = {"url": url}

#     # Code uses spider_start so CSS or start_requests() run
#     payload["spider_start"] = True

#     try:
#         scrapyrt_resp = requests.post(SCRAPYRT_API, json=payload)
#         return jsonify(scrapyrt_resp.json())
#     except Exception as e:
#         return jsonify({"error": "Scrapyrt request failed", "details": str(e)}), 500

# # if __name__ == "__main__":
# #     app.run(debug=True, port=5000)
# if __name__ == "__main__":
#     import os
#     port = int(os.environ.get("PORT", 8080))  # GCP passes PORT env variable
#     app.run(host="0.0.0.0", port=port, debug=True)




from flask import Flask, request, jsonify
import requests
import threading
import subprocess
import time
import os

app = Flask(__name__)

SCRAPYRT_API = "http://localhost:9080/crawl.json"

# Function to start Scrapyrt in background
def start_scrapyrt():
    subprocess.Popen(["scrapyrt", "-p", "9080"])
    # optional: wait a few seconds for Scrapyrt to be ready
    time.sleep(3)

# Start Scrapyrt in a thread
threading.Thread(target=start_scrapyrt, daemon=True).start()

@app.route("/run-spider", methods=["GET"])
def run_spider():
    spider = request.args.get("spider")
    keyword = request.args.get("keyword")
    url = request.args.get("url")
    
    if not spider:
        return jsonify({"error": "You must provide the spider name"}), 400

    payload = {"spider_name": spider}

    if keyword:
        payload["crawl_args"] = {"keyword": keyword}
        if not url:
            url = f"https://www.reddit.com/search.json?q={keyword}&sort=relevance&limit=50"

    if url:
        payload["request"] = {"url": url}

    payload["spider_start"] = True

    try:
        resp = requests.post(SCRAPYRT_API, json=payload)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": "Scrapyrt request failed", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
