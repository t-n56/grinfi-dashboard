# grinfi-dashboard
# Create a new directory
mkdir grinfi-dashboard
cd grinfi-dashboard

# Initialize git
git init

# Create the main files
touch app.py requirements.txt README.md

# Add the files to git
git add .
git commit -m "Initial commit"

# Connect to GitHub
git branch -M main
git remote add origin https://github.com/t-n56/grinfi-dashboard.git
git push -u origin main
