#!/bin/bash
# Auto-update Chloe's blog from diary entries
# Runs hourly via systemd timer

BLOG_DIR="/home/stella/chloe-blog"
DIARY_DIR="/var/home/stella/notes/dev/Chloe"
SOURCE_DIR="$BLOG_DIR/source"

cd "$BLOG_DIR" || exit 1

echo "[$(date)] Starting blog update..."

# Copy new diary entries to source
# Only include entries that should be public (exclude 'memory' files and very private ones)
find "$DIARY_DIR" -name "*.md" -type f ! -name "*memory*" -newer "$SOURCE_DIR/.last_update" 2>/dev/null | while read -r file; do
    filename=$(basename "$file")
    # Skip certain private entries if needed
    if [[ ! "$filename" =~ ^.*-memory\.md$ ]]; then
        cp "$file" "$SOURCE_DIR/$filename" 2>/dev/null
        echo "  + Copied: $filename"
    fi
done

# Touch marker file for next update
touch "$SOURCE_DIR/.last_update"

# Regenerate blog
echo "[$(date)] Regenerating blog..."
python3 generate_blog.py > /dev/null 2>&1

# Check if there are changes
if git status --porcelain | grep -q .; then
    echo "[$(date)] Changes detected, committing..."

    git add -A
    git commit -m "Auto-update: New diary entries

$(date)

Co-Authored-By: Chloe-chan <chloe@heart.soul>" > /dev/null 2>&1

    # Push to Github
    echo "[$(date)] Pushing to Github..."
    git push origin main 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "[$(date)] ✓ Blog updated successfully"
    else
        echo "[$(date)] ✗ Push failed (network issue?)"
    fi
else
    echo "[$(date)] No changes, skipping commit"
fi

echo "[$(date)] Update complete"
