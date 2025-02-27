import sys
import git
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_repo.py <path_to_git_folder>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    try:
        repo = git.Repo(repo_path)
    except Exception as e:
        print(f"Error opening repository at {repo_path}: {e}")
        sys.exit(1)
    

if __name__ == "__main__":
    main()
