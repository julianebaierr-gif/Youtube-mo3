# -*- coding: utf-8 -*-
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.build_article_database import ARTICLE_OBJECT

out_path = os.path.join(BASE_DIR, "app", "articles_data.py")

with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    f.write('"""\nYT4MP3 Blog Articles Content Repository\n"""\n\n')
    f.write('from typing import List, Dict, Any\n\n')
    f.write(f'BLOG_ARTICLES: List[Dict[str, Any]] = [{repr(ARTICLE_OBJECT)}]\n')

print(f"Successfully wrote articles to {out_path}")
