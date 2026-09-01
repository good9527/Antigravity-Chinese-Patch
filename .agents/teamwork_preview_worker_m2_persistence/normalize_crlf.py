import glob

for pattern in ["*.ps1", "watcher/*.ps1"]:
    for path in glob.glob(pattern):
        with open(path, "rb") as f:
            content = f.read()
        # normalize to CRLF
        content_crlf = content.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        with open(path, "wb") as f:
            f.write(content_crlf)
        print(f"Normalized {path} to CRLF")
