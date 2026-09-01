import glob

# Ensure .ps1 have BOM + CRLF
for pattern in ["*.ps1", "watcher/*.ps1"]:
    for path in glob.glob(pattern):
        with open(path, "rb") as f:
            c = f.read()
        if c.startswith(b"\xef\xbb\xbf"):
            c = c[3:]
        c = c.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        c = b"\xef\xbb\xbf" + c
        with open(path, "wb") as f:
            f.write(c)

# Ensure .sh, .plist, .path, .service have LF (no BOM)
for pattern in ["*.sh", "watcher/*.sh", "watcher/*.plist", "watcher/*.path", "watcher/*.service"]:
    for path in glob.glob(pattern):
        with open(path, "rb") as f:
            c = f.read()
        if c.startswith(b"\xef\xbb\xbf"):
            c = c[3:]
        c = c.replace(b"\r\n", b"\n")
        with open(path, "wb") as f:
            f.write(c)

print("All line endings and BOMs synchronized perfectly.")
