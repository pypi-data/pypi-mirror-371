import sys, re
from .core import download_github_dir
from .help import show_help
# from .version import get_version  # helper to fetch version from pyproject.toml

def validate_github_url(url: str) -> bool:
    """
    Validate GitHub repository or subdirectory URL using regex.
    Examples of valid:
      - https://github.com/user/repo
      - https://github.com/user/repo/tree/branch/path/to/dir
    """
    pattern = re.compile(
        r"^https:\/\/github\.com\/[^\/]+\/[^\/]+(?:\/tree\/[^\/]+(?:\/.*)?)?$"
    )
    return bool(pattern.match(url))


def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    flat = False
    save_dir = "."
    force = False
    rename = False

    args = sys.argv[1:]

    # -------------------------------
    # Handle flags with no URL needed
    # -------------------------------
    if args[0] in ("--help", "-h"):
        show_help()
        sys.exit(0)

    if args[0] in ("--version", "-v", "-V"):
        print(f"giget 0.3.1 built by Ronit Naik")
        sys.exit(0)

    # -------------------------------
    # Handle flags + URL
    # -------------------------------
    url = None
    i = 0
    while i < len(args):
        arg = args[i]

        if arg == "-nf":
            flat = True
        elif arg == "--force":
            force = True
        elif arg == "--rename":
            rename = True
        elif arg == "-o":
            if i + 1 >= len(args):
                print("❌ Missing output directory after -o")
                sys.exit(1)
            save_dir = args[i + 1]
            i += 1  # skip next since we consumed it
        elif arg.startswith("-"):
            print("❌ Unknown flag:", arg)
            sys.exit(1)
        else:
            # This should be the GitHub URL
            if url is not None:
                print("❌ Multiple URLs detected. Only one is allowed.")
                sys.exit(1)
            url = arg.rstrip("/")

        i += 1

    # -------------------------------
    # Validate URL
    # -------------------------------
    if url is None:
        print("❌ Missing GitHub URL.\n\nUsage: giget [flags] <github_url>")
        sys.exit(1)

    if not validate_github_url(url):
        print("❌ Invalid GitHub URL format:", url)
        print("   Example: https://github.com/user/repo")
        print("   Example: https://github.com/user/repo/tree/branch/path/to/dir")
        sys.exit(1)

    # -------------------------------
    # Extract GitHub parts
    # -------------------------------
    try:
        # Example: https://github.com/jasmcaus/opencv-course/tree/master/Resources/Photos
        parts = url.split("github.com/")[1].split("/")
        if "tree" in parts:
            owner, repo, _, branch, *path = parts
        else:
            owner, repo, *path = parts
            branch = "master"
        folder_path = "/".join(path)
    except Exception:
        print("❌ Invalid GitHub URL structure.")
        sys.exit(1)

    # -------------------------------
    # Run the downloader
    # -------------------------------
    try:
        download_github_dir(
            owner,
            repo,
            folder_path,
            branch,
            save_dir=save_dir,
            flat=flat,
            force=force,
            rename=rename,
        )
        print("✅ Download complete!")
    except Exception as e:
        print("❌ Error:", e)
        sys.exit(1)
