#/bin/bash

# Reset any local changes
git reset --hard origin/main

# Pull the latest code (this won't fail since there are no local changes)
git pull origin main

# Activate your virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart your application service
echo "Restarting my_flask_app.service..."
sudo systemctl restart my_flask_app.service
