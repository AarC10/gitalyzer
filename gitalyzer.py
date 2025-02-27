import sys
import git
import matplotlib.pyplot as plt
from collections import defaultdict
import re

contributions_by_year = defaultdict(int)
contributors_by_year = defaultdict(set)
overall_contributor_commits = defaultdict(int)
contributor_yearly_commits = defaultdict(lambda: defaultdict(int))


def gather_data(repo: git.Repo):
    for commit in repo.iter_commits('--all'):
        year = commit.authored_datetime.year
        author = commit.author.name

        contributions_by_year[year] += 1
        contributors_by_year[year].add(author)
        overall_contributor_commits[author] += 1
        contributor_yearly_commits[author][year] += 1

    years = sorted(contributions_by_year.keys())
    total_commits = [contributions_by_year[year] for year in years]
    total_contributors = [len(contributors_by_year[year]) for year in years]

    return years, total_commits, total_contributors


def graph_data(years: list[int], total_commits: list[int], total_contributors: list[int]):
    # Total contributions over time (commits per year)
    plt.figure(figsize=(10, 6))
    plt.plot(years, total_commits, marker='o', color='blue')
    plt.title("Total Contributions Over Time")
    plt.xlabel("Year")
    plt.ylabel("Total Commits")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Total number of contributors over time
    plt.figure(figsize=(10, 6))
    plt.plot(years, total_contributors, marker='o', color='green')
    plt.title("Total Contributors Over Time")
    plt.xlabel("Year")
    plt.ylabel("Number of Contributors")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def graph_contributors(top_contrib_re_filter=None):
    overall_contributors = sorted(overall_contributor_commits.items(), key=lambda x: x[1], reverse=True)

    # Get top 10 contributors
    if top_contrib_re_filter:
        pattern = re.compile(top_contrib_re_filter)
        top_contributors = [
            (contributor, count) for contributor, count in overall_contributors if not pattern.search(contributor)
        ][:10]
    else:
        top_contributors = overall_contributors[:10]

    top_contributor_names = [contributor for contributor, count in top_contributors]
    all_years = sorted({year for counts in contributor_yearly_commits.values() for year in counts})

    # Contributions per year for top contributors
    plt.figure(figsize=(10, 6))
    for contributor in top_contributor_names:
        yearly_counts = [contributor_yearly_commits[contributor].get(year, 0) for year in all_years]
        plt.plot(all_years, yearly_counts, marker='o', label=contributor)
    plt.title("Contributions per Year for Top Contributors")
    plt.xlabel("Year")
    plt.ylabel("Commits")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_repo.py <path_to_git_folder> [filter_regex]")
        sys.exit(1)

    repo_path = sys.argv[1]
    try:
        repo = git.Repo(repo_path)
    except Exception as e:
        print(f"Error opening repository at {repo_path}: {e}")
        sys.exit(1)

    top_contrib_re_filter = sys.argv[2] if len(sys.argv) >= 3 else None

    years, total_commits, total_contributors = gather_data(repo)

    graph_data(years, total_commits, total_contributors)
    graph_contributors(top_contrib_re_filter)


if __name__ == "__main__":
    main()
