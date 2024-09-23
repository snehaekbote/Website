#/bin/bash

# Stash any local changes
git stash --include-untracked

# Pull the latest code with rebase
git pull --rebase origin main

# Apply stashed changes, if any
git stash pop || true

# Activate your virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart your application service
echo "Restarting my_flask_app.service..."
sudo systemctl restart my_flask_app.service
