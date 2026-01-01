import os
import requests
import urllib.parse
import zipfile
import io
import sys

def download_and_extract_media_from_koofr(link_url, output_folder='downloads', media_extensions=None, password=None):
    """
    Downloads the ZIP bundle from a Koofr public share link and extracts media files (images/videos).
    
    Args:
    - link_url (str): Full Koofr public share link (e.g., https://app.koofr.net/links/xxxx?path=%2Ffolder).
    - output_folder (str): Local folder to save extracted files.
    - media_extensions (list): File extensions to extract. Defaults to common image/video types.
    - password (str): Password if the share is protected (most are not).
    """
    if media_extensions is None:
        media_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff',
                            '.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv']

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Parse the link
    parsed_url = urllib.parse.urlparse(link_url)
    path_parts = parsed_url.path.split('/links/')
    if len(path_parts) < 2:
        raise ValueError("Invalid Koofr link format. Make sure it's a full public share link.")
    
    link_id = path_parts[1].split('?')[0]
    query = parsed_url.query or 'path=%2F'  # Default to root if no path

    # Password parameter (leave empty if no password)
    password_param = f"&password={urllib.parse.quote(password)}" if password else "&password="

    # Step 1: Get bundle metadata
    api_url = f"https://app.koofr.net/api/v2/public/links/{link_id}/bundle?{query}{password_param}"
    print(f"Fetching metadata... ({api_url})")
    
    try:
        resp = requests.get(api_url, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e} (Status code: {resp.status_code})")
        if resp.status_code == 404:
            print("The share link is invalid, expired, or has been removed.")
        elif resp.status_code == 403:
            print("Access denied – the link might require a password or be restricted.")
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        sys.exit(1)

    data = resp.json()
    bundle_name = data.get('file', {}).get('name')
    if not bundle_name:
        print("No bundle found – the folder might be empty or the link no longer active.")
        sys.exit(1)

    print(f"Found bundle: {bundle_name}")

    # Step 2: Build download URL
    zip_filename = f"{bundle_name}.zip"
    encoded_zip = urllib.parse.quote(zip_filename)
    dl_url = f"https://app.koofr.net/content/links/{link_id}/files/get/{encoded_zip}?{query}{password_param}&pf=1&force"

    print(f"Downloading ZIP... (this may take time for large folders)")
    
    headers = {'Referer': link_url}
    try:
        resp = requests.get(dl_url, headers=headers, stream=True, timeout=60)
        resp.raise_for_status()
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)

    # Step 3: Extract media files from ZIP (streamed to avoid memory issues)
    total_extracted = 0
    try:
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            for file_info in z.infolist():
                if file_info.is_dir():
                    continue
                filename_lower = file_info.filename.lower()
                if any(filename_lower.endswith(ext) for ext in media_extensions):
                    # Preserve folder structure
                    extract_path = os.path.join(output_folder, file_info.filename.lstrip('/'))
                    os.makedirs(os.path.dirname(extract_path), exist_ok=True)
                    
                    with z.open(file_info) as source, open(extract_path, 'wb') as target:
                        target.write(source.read())
                    
                    print(f"Extracted: {file_info.filename}")
                    total_extracted += 1
    except zipfile.BadZipFile:
        print("Downloaded file is not a valid ZIP – the link may be broken.")
        sys.exit(1)

    print(f"\nDone! Extracted {total_extracted} media files to '{output_folder}' folder.")


# ================ HOW TO USE ================
if __name__ == "__main__":
    print("Koofr Media Downloader\n")
    
    # Paste your Koofr link here (replace the entire string below)
    koofr_link = "https://app.koofr.net/links/c1fab741-0e23-4516-8f30-1bc31814aea0?path=%2FBreanna%20Ly"
    
    if "PASTE_YOUR_KOOFR_LINK_HERE" in koofr_link:
        print("Error: You need to replace the placeholder with a real Koofr share link!")
        print("Example: https://app.koofr.net/links/abcd1234-efgh-5678-ijkl-9012mnopqrst?path=%2FMy%20Folder")
        sys.exit(1)
    
    # Optional: change the output folder name
    output_folder = "koofr_downloads"
    
    # If the link requires a password, uncomment and set it:
    # password = "your_password_here"
    
    try:
        download_and_extract_media_from_koofr(
            link_url=koofr_link,
            output_folder=output_folder,
            # password=password  # uncomment if needed
        )
    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")