import sys
from .core import download_github_dir
from .help import show_help

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    flat = False
    save_dir = "."

    # size of argv in 3 or more -- command has flags
    if sys.argv[1].startswith(("-","--")):
        # size of argv is 3 or 2 if -h or --help 
        if sys.argv[1] == "-nf":
            flat = True
        elif (sys.argv[1] == "--help") or (sys.argv[1] == "-h"):
            show_help()
            sys.exit(1)
        else:
            print("Unknown flag:", sys.argv[1])
            sys.exit(1)
        if len(sys.argv) == 2:
            print("No GitHub url found\n\ngiget -nf <github-url>")
        url = sys.argv[2].rstrip("/")

        # checking if -o flag is present -- if yes then size of argv should be 5
        if len(sys.argv) >= 4:
            
            if sys.argv[3] == "-o":
                if len(sys.argv == 4):
                    print("Missing output directory after -o")
                    sys.exit(1)
                save_dir = sys.argv[4]
            else:
                print("Unknown flag:", sys.argv[3])
                sys.exit(1)
    
    # size of argv is 2 -- a normal CLI command
    else:
        url = sys.argv[1].rstrip("/")
        # checking if -o is present
        if len(sys.argv) > 3:
            if sys.argv[2] == "-o":
                if len(sys.argv == 3):
                    print("Missing output directory after -o")
                    sys.exit(1)
                save_dir = sys.argv[3]
            else:
                print("Unknown flag:", sys.argv[3])
                sys.exit(1)

    try:
        # Example: https://github.com/jasmcaus/opencv-course/tree/master/Resources/Photos
        parts = url.split("github.com/")[1].split("/")
        owner, repo, tree, branch, *path = parts
        folder_path = "/".join(path)
    except Exception:
        print("****| Invalid GitHub URL format. |****")
        sys.exit(1)

    download_github_dir(owner, repo, folder_path, branch, save_dir=save_dir, flat=flat)
    print("✅ Download complete!")