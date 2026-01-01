# koofr_downloader
Open koofr_downloader.py in Notepad (or any text editor like Notepad++, VS Code).
Scroll down near the bottom (after the big function ends, in the "# ================ HOW TO USE ================" section).
Find line 111 (most editors show line numbers on the left — enable it in View > Status Bar if needed).
Replace the entire line with your actual link, like this example:
koofr_link = "PASTE_YOUR_KOOFR_LINK_HERE"
with your actual Koofr link (e.g., https://app.koofr.net/links/...).
(Optional) Change output_folder = "koofr_downloads" to whatever folder name you want.
Save the file.
Run it in PowerShell/Command Prompt with:textpython koofr_downloader.py (or py koofr_downloader.py)
