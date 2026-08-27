"""
Fetch authentic transparent weapon PNG renders from the web for all 18 MW4 weapons.
"""

import os
import re
import json
import urllib.request
import urllib.parse

WEAPONS_TO_FETCH = [
    ("w_xm4", "XM4", "Assault Rifle"),
    ("w_mcw", "MCW", "Assault Rifle"),
    ("w_holger556", "Holger 556", "Assault Rifle"),
    ("w_kastov74m", "Kastov 74-M", "Assault Rifle"),
    ("w_rival9", "Rival-9", "Submachine Gun"),
    ("w_striker45", "Striker 45", "Submachine Gun"),
    ("w_amr9", "AMR-9", "Submachine Gun"),
    ("w_wspswarm", "WSP Swarm", "Submachine Gun"),
    ("w_basb", "BAS-B", "Battle Rifle"),
    ("w_sidewinder", "Sidewinder", "Battle Rifle"),
    ("w_kvdenforcer", "KVD Enforcer", "Marksman Rifle"),
    ("w_bruenmk9", "Bruen Mk9", "Light Machine Gun"),
    ("w_pulemyot762", "Pulemyot 762", "Light Machine Gun"),
    ("w_kattamr", "KATT-AMR", "Sniper Rifle"),
    ("w_longbow", "Longbow", "Sniper Rifle"),
    ("w_lockwood680", "Lockwood 680", "Shotgun"),
    ("w_cor45", "COR-45", "Handgun"),
    ("w_renetti", "Renetti", "Handgun"),
]

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "weapons")
os.makedirs(OUT_DIR, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search_fandom_image(query_str):
    try:
        # 1. Search for page
        search_url = f"https://callofduty.fandom.com/api.php?action=query&list=search&srsearch={urllib.parse.quote(query_str + ' menu icon')}&srnamespace=6&format=json"
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            search_results = res_data.get("query", {}).get("search", [])
            if not search_results:
                return None
            
            first_title = search_results[0].get("title")
            
            # 2. Get direct file URL
            info_url = f"https://callofduty.fandom.com/api.php?action=query&titles={urllib.parse.quote(first_title)}&prop=imageinfo&iiprop=url&format=json"
            req2 = urllib.request.Request(info_url, headers=headers)
            with urllib.request.urlopen(req2, timeout=10) as resp2:
                info_data = json.loads(resp2.read().decode("utf-8"))
                pages = info_data.get("query", {}).get("pages", {})
                for pid, page in pages.items():
                    imginfo = page.get("imageinfo", [])
                    if imginfo:
                        return imginfo[0].get("url")
    except Exception as e:
        print(f"Error searching for {query_str}: {e}")
    return None


def download_image(img_url, out_path):
    try:
        req = urllib.request.Request(img_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp, open(out_path, "wb") as f:
            f.write(resp.read())
        print(f"Successfully downloaded {out_path} ({os.path.getsize(out_path)} bytes)")
        return True
    except Exception as e:
        print(f"Error downloading {img_url}: {e}")
        return False


def main():
    print(f"Targeting download folder: {OUT_DIR}")
    for wid, name, cls in WEAPONS_TO_FETCH:
        out_file = os.path.join(OUT_DIR, f"{wid}.png")
        print(f"Searching for {name} ({cls})...")
        url = search_fandom_image(name)
        if url:
            print(f"  Found URL: {url[:80]}...")
            download_image(url, out_file)
        else:
            print(f"  No image found for {name}")

if __name__ == "__main__":
    main()
