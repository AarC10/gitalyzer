import sys
import git
import matplotlib.pyplot as plt
from collections import defaultdict

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

    contributions_by_year = defaultdict(int)
    contributors_by_year = defaultdict(set)
    overall_contributor_commits = defaultdict(int)
    contributor_yearly_commits = defaultdict(lambda: defaultdict(int))

    for commit in repo.iter_commits('--all'):
        year = commit.authored_datetime.year
        author = commit.author.name
        
        contributions_by_year[year] += 1
        contributors_by_year[year].add(author)
        overall_contributor_commits[author] += 1
        contributor_yearly_commits[author][year] += 1

    # Prepare data for aggregate graphs
    years = sorted(contributions_by_year.keys())
    total_commits = [contributions_by_year[year] for year in years]
    total_contributors = [len(contributors_by_year[year]) for year in years]

    print(years)
    print(total_commits)
    print(total_contributors)

    

if __name__ == "__main__":
    main()
