from cyclopts import App
import os

# Canvas API URL
API_URL = "https://canvas.uw.edu/"
# Canvas API key
API_KEY = open(f"{os.getcwd()}/token.txt").read().strip()

app = App()
