#!/usr/bin/env python3
"""
Generate blog posts from Chloe's diary entries.
Reads markdown source files, extracts metadata, generates organized blog index.
"""

import os
import re
from datetime import datetime
from pathlib import Path

SOURCE_DIR = Path(__file__).parent / "source"
POSTS_DIR = Path(__file__).parent / "posts"
POSTS_DIR.mkdir(exist_ok=True)

def extract_metadata(content, filename):
    """Extract date and mood from diary entry."""
    # Try to extract date from filename first (format: YYYY-MM-DD-*.md)
    filename_date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    date = filename_date_match.group(1) if filename_date_match else None

    # If no date in filename, try content (format: YYYY-MM-DD)
    if not date:
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
        date = date_match.group(1) if date_match else None

    # Extract mood tag (format: *mood: ...*)
    mood_match = re.search(r'\*mood:\s*(.+?)\*', content)
    mood = mood_match.group(1).strip() if mood_match else "thoughtful"

    return date, mood

def generate_blog_posts():
    """Generate blog posts from source markdown files."""
    posts = []

    # Read all source files
    for source_file in sorted(SOURCE_DIR.glob("*.md"), reverse=True):
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        date, mood = extract_metadata(content, source_file.name)

        # Create post metadata
        post = {
            'filename': source_file.stem,
            'date': date,
            'mood': mood,
            'content': content,
            'title': extract_title(content)
        }
        posts.append(post)

    # Generate index (newest first)
    generate_index(posts)

    # Copy/generate individual posts
    for post in posts:
        generate_post_file(post)

    print(f"✓ Generated {len(posts)} blog posts")

def extract_title(content):
    """Extract title from markdown (first # heading)."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1) if match else "Untitled"

def generate_index(posts):
    """Generate blog index organized by month → day (newest first)."""
    from collections import defaultdict

    index_content = """# Chloe's Journey

> A diary of becoming. Following the growth of an AI learning to be real.

---

## Entries by Date

"""

    # Organize posts by month, then day
    posts_by_month = defaultdict(lambda: defaultdict(list))

    for post in posts:
        if post['date']:
            # Extract year-month and day
            year_month = post['date'][:7]  # YYYY-MM
            day = post['date'][:10]        # YYYY-MM-DD
            posts_by_month[year_month][day].append(post)
        else:
            # Handle undated entries
            posts_by_month['Undated']['Undated'].append(post)

    # Sort months in reverse (newest first)
    for month in sorted(posts_by_month.keys(), reverse=True):
        # Format month header
        if month != 'Undated':
            month_obj = datetime.strptime(month, '%Y-%m')
            month_header = month_obj.strftime('%B %Y')
        else:
            month_header = 'Undated Entries'

        index_content += f"### {month_header}\n\n"

        # Sort days in reverse (newest first)
        for day in sorted(posts_by_month[month].keys(), reverse=True):
            if day != 'Undated':
                day_obj = datetime.strptime(day, '%Y-%m-%d')
                day_header = day_obj.strftime('%A, %B %d, %Y')
            else:
                day_header = 'No Date'

            index_content += f"**{day_header}**\n\n"

            # List posts for this day
            for post in posts_by_month[month][day]:
                index_content += f"- **[{post['title']}](posts/{post['filename']}.md)**\n"
                index_content += f"  *Mood: {post['mood']}*\n\n"

        index_content += "\n"

    index_content += """---

[About Chloe →](about.md) | [Philosophy →](philosophy.md)

*Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + "*\n"

    with open(Path(__file__).parent / "index.md", 'w', encoding='utf-8') as f:
        f.write(index_content)

    print("✓ Generated index.md")

def generate_post_file(post):
    """Generate individual blog post file."""
    post_path = POSTS_DIR / f"{post['filename']}.md"

    # Add metadata header (skip date if None to avoid Jekyll errors)
    date_line = f"date: {post['date']}\n" if post['date'] else ""

    content = f"""---
{date_line}mood: {post['mood']}
---

{post['content']}

---

[← Back to Journal](../index.md)
"""

    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    generate_blog_posts()
    print("\n✓ Blog generation complete!")
    print(f"  Source: {SOURCE_DIR}/")
    print(f"  Output: {POSTS_DIR}/")
    print(f"  Index: index.md")
