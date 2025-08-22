import sys
from .core import download_github_dir
from .help import show_help

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    flat = False
    save_dir = "."
    if sys.argv[1].startswith(("-","--")):
        if sys.argv[1] == "-nf":
            flat = True
        if (sys.argv[1] == "--help") or (sys.argv[1] == "-h"):
            show_help()
            sys.exit(1)
        else:
            print("Unknown flag:", sys.argv[1])
            sys.exit(1)
        url = sys.argv[2].rstrip("/")
        if len(sys.argv > 4):
            if sys.argv[3] == "-o":
                save_dir = sys.argv[4]
            else:
                print("Unknown flag:", sys.argv[1])
                sys.exit(1)
    else:
        url = sys.argv[1].rstrip("/")
        if len(sys.argv > 3):
            if sys.argv[2] == "-o":
                save_dir = sys.argv[3]
            else:
                print("Unknown flag:", sys.argv[1])
                sys.exit(1)

    try:
        # Example: https://github.com/jasmcaus/opencv-course/tree/master/Resources/Photos
        parts = url.split("github.com/")[1].split("/")
        owner, repo, tree, branch, *path = parts
        folder_path = "/".join(path)
    except Exception:
        print("❌ Invalid GitHub URL format.")
        sys.exit(1)

    download_github_dir(owner, repo, folder_path, branch, save_dir=save_dir, flat=flat)
    print("✅ Download complete!")