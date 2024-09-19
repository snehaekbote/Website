#/bin/bash

# Pull the latest code
git pull origin main

# Activate your virtual environment (if applicable)
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart your server (e.g., Flask or any service)
systemctl restart your-app.service
