#/bin/bash

# Pull the latest code
git pull origin main

# Activate your virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart your application service
echo "Restarting my_flask_app.service..."
sudo systemctl restart my_flask_app.service
