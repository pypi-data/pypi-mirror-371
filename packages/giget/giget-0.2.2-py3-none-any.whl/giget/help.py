# help.py

def show_help():
    help_text = """
giget - A simple CLI tool to download GitHub directories | sub-directories | files.

Usage:
    giget [flags] <github_repo_url> [options]

Options:
    -h, --help       Show this help message and exit.
    -o <path>        Specify output directory (default: current directory).
    -nf <path>       Downloads all files into current dir (no folders)

Examples:
    giget https://github.com/user/repo
    giget https://github.com/user/repo -o ./downloads
    giget -nf https://github.com/user/repo

Description:
    giget is a Python package and CLI tool that makes it easy to download
    any directories or all the files inside directories 
    from GitHub repositories.

    Steps:
      1. Provide a GitHub repository URL.
      2. giget will fetch and download the files.
      3. You can specify an output folder using -o.
      4. If you want to download all the files and dont want the 
         structure of the folder then use -nf.
"""
    print(help_text)
