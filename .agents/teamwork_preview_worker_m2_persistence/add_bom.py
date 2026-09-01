import glob

for pattern in ["*.ps1", "watcher/*.ps1"]:
    for path in glob.glob(pattern):
        with open(path, "rb") as f:
            content = f.read()
        # Remove any existing BOM first
        if content.startswith(b"\xef\xbb\xbf"):
            content = content[3:]
        # Normalize CRLF
        content = content.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        # Add UTF-8 BOM
        content_with_bom = b"\xef\xbb\xbf" + content
        with open(path, "wb") as f:
            f.write(content_with_bom)
        print(f"Added UTF-8 BOM and normalized CRLF to {path}")
