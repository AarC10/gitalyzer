import sys
import git
import matplotlib.pyplot as plt
from collections import defaultdict
import re
import os

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


def graph_data(years: list[int], total_commits: list[int], total_contributors: int):
    # Total contributions over time (commits per year)
    total_contributions_graph = plt.figure(figsize=(10, 6))
    plt.plot(years, total_commits, marker='o', color='blue')
    plt.title("Total Contributions Over Time")
    plt.xlabel("Year")
    plt.ylabel("Total Commits")
    plt.grid(True)
    plt.xticks(range(years[0], years[-1] + 1))
    plt.tight_layout()

    # Total number of contributors over time
    total_contributors_graph = plt.figure(figsize=(10, 6))
    plt.plot(years, total_contributors, marker='o', color='green')
    plt.title("Total Contributors Over Time")
    plt.xlabel("Year")
    plt.ylabel("Number of Contributors")
    plt.grid(True)
    plt.xticks(range(years[0], years[-1] + 1))
    plt.tight_layout()

    return total_contributions_graph, total_contributors_graph


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
    contributors_graph = plt.figure(figsize=(10, 6))
    for contributor in top_contributor_names:
        yearly_counts = [contributor_yearly_commits[contributor].get(year, 0) for year in all_years]
        plt.plot(all_years, yearly_counts, marker='o', label=contributor)
    plt.title("Contributions per Year for Top Contributors")
    plt.xlabel("Year")
    plt.ylabel("Commits")
    plt.legend()
    plt.grid(True)
    plt.xticks(range(all_years[0], all_years[-1] + 1))
    plt.tight_layout()

    return contributors_graph


def graph_contributor_add_drop():
    sorted_years = sorted(contributors_by_year.keys())
    additions = {}
    dropoffs = {}
    cumulative_contributors = set()
    for i, year in enumerate(sorted_years):
        current = contributors_by_year[year]
        new_additions = current - cumulative_contributors
        additions[year] = len(new_additions)
        if i == 0:
            dropoffs[year] = 0
        else:
            prev_year = sorted_years[i - 1]
            drop = contributors_by_year[prev_year] - current
            dropoffs[year] = len(drop)
        cumulative_contributors.update(current)
    add_drop_graph = plt.figure(figsize=(10, 6))
    x_years = list(range(sorted_years[0], sorted_years[-1] + 1))
    y_additions = [additions.get(year, 0) for year in x_years]
    y_dropoffs = [dropoffs.get(year, 0) for year in x_years]
    plt.plot(x_years, y_additions, marker='o', color='green', label='New Additions')
    plt.plot(x_years, y_dropoffs, marker='o', color='red', label='Dropoffs')
    plt.title("Contributor Additions and Dropoffs per Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Contributors")
    plt.xticks(x_years)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    return add_drop_graph

def handle_figures(repo_path, contributors_graph, contributions_graph, total_contributions_graph, add_drop_graph):
    repo_name = os.path.basename(repo_path)
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    output_folder = os.path.join(os.getcwd(), repo_name)
    os.makedirs(output_folder, exist_ok=True)

    contributors_graph.savefig(os.path.join(output_folder, "top_contributors.png"))
    contributions_graph.savefig(os.path.join(output_folder, "contributions_per_year.png"))
    total_contributions_graph.savefig(os.path.join(output_folder, "total_contributions.png"))
    add_drop_graph.savefig(os.path.join(output_folder, "total_contributors.png"))

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

    total_contributions_graph, total_contributors_graph = graph_data(years, total_commits, total_contributors)
    top_contributors_graph = graph_contributors(top_contrib_re_filter)
    add_drop_graph = graph_contributor_add_drop()

    handle_figures(repo_path, total_contributions_graph, total_contributors_graph, top_contributors_graph, add_drop_graph)

    plt.show()


if __name__ == "__main__":
    main()
