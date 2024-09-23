#/bin/bash
# Log current git status
echo "Git status before reset:"
git status

# Reset any local changes (including uncommitted ones)
git reset --hard

# Remove any untracked files and directories
git clean -fd

# Pull the latest code with rebase
git pull --rebase origin main

# Activate your virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart your application service
echo "Restarting my_flask_app.service..."
sudo systemctl restart my_flask_app.service
