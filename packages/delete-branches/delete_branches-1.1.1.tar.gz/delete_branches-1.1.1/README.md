# delete-branches

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/11071/badge)](https://www.bestpractices.dev/projects/11071)
[![CI](https://github.com/tagdots/delete-branches/actions/workflows/ci.yaml/badge.svg)](https://github.com/tagdots/delete-branches/actions/workflows/ci.yaml)
[![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/delete-branches/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/delete-github-branches)
[![coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots/delete-branches/refs/heads/badges/badges/coverage.json)](https://github.com/tagdots/delete-branches/actions/workflows/cron-tasks.yaml)

<br>

## ✅ What does delete-branches do?
**delete-branches** removes GitHub branches that have been inactive (without new commits) for longer than the idle period.

_**exemptions**_: `default branch`, `protected branches`, `head branches in PR`, and `user-specified exclude branches`

<br>

## ⭐ Why switch to delete-branches?
- we reduce your supply chain risks with [openssf best practices](https://best.openssf.org) in our SDLC and operations.
- we share evidence of code coverage results in action (click _Code Coverage » cron-tasks » badge-coverage_).

<br>

## 🏃 Running _delete-branches_ in GitHub action
Use the workflow examples below to create your own workflow inside `.github/workflows/`.

<br>

### Example 1 - MOCK Delete Summary

* run on a scheduled interval - every day at 5:30 pm UTC  (`- cron: '30 17 * * *'`)
* use GitHub Token with permissions: `contents: read`
* exclude branch from delete: `badges` (`exclude-branches: 'badges'`)
* perform a **MOCK delete** (`dry-run: true`)
* display inactive branches without new commits longer than 10 days (`max-idle-days: 10`)

### Example 1 - MOCK Delete Workflow
```
name: delete-github-branches

on:
  schedule:
    - cron: '30 17 * * *'

permissions:
  contents: read

jobs:
  delete-branches:
    runs-on: ubuntu-latest

    permissions:
      contents: read
      pull-requests: read

    - name: Run delete-branches
      id: delete-branches
      uses: tagdots/delete-branches@ff424d3a4af5b29492bd8b778887583259b3e573 # 1.0.0
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        repo-url: ${{ github.repository }}
        max-idle-days: 10
        exclude-branches: 'badges'
        dry-run: true
```

<br>

### Example 2 - Irreversible Delete Summary

* run on a scheduled interval - every day at 5:30 pm UTC  (`- cron: '30 17 * * *'`)
* use GitHub Token with permissions: `contents: write`
* exclude branch from delete: `badges` (`exclude-branches: 'badges'`)
* perform a **delete** (`dry-run: false`)
* delete inactive branches without new commits longer than 10 days (`max-idle-days: 10`)

### Example 2 - Irreversible Delete Workflow
```
name: delete-github-branches

on:
  schedule:
    - cron: '30 17 * * *'

permissions:
  contents: read

jobs:
  delete-branches:
    runs-on: ubuntu-latest

    permissions:
      contents: write
      pull-requests: read

    - name: Run delete-branches
      id: delete-branches
      uses: tagdots/delete-branches@ff424d3a4af5b29492bd8b778887583259b3e573 # 1.0.0
      env:
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        repo-url: ${{ github.repository }}
        max-idle-days: 10
        exclude-branches: 'badges'
        dry-run: false
```

<br>

## 🖥 Running _delete-branches_ locally

### Prerequisites
```
* Python (3.12+)
* GitHub fine-grained token (contents: write)
```

<br>

### Setup _delete-branches_
```
~/work/hello-world $ workon hello-world
(hello-world) ~/work/hello-world $ export GH_TOKEN=github_pat_xxxxxxxxxxxxx
(hello-world) ~/work/hello-world $ pip install -U delete-branches
```

<br>

### 🔍 Example 1 - Run for help
```
(hello-world) ~/work/hello-world $ delete-branches --help
Usage: delete-branches [OPTIONS]

Options:
  --dry-run BOOLEAN        default: true
  --repo-url TEXT          e.g. https://github.com/{owner}/{repo}  [required]
  --exclude-branches TEXT  Branches excluded from deletion
  --max-idle-days TEXT     Delete branches older than max. idle days [required]
  --version                Show the version and exit.
  --help                   Show this message and exit.
```

<br>

### 🔍 Example 2 - MOCK delete branches with no commits longer than 10 days
**Summary**
1. exclude 3 branches: `test-1`, `test-2`, `badges`
1. remove branches without commits longer than 10 days

**Results**
1. refine excluded branches to `badges` because branches (`test-1` and `test-2`) do not exist
1. 3 branches are exempted from delete: `main`, `badges`, `pr-branch-01`
1. 6 branches are not exempted from delete and 2 out of 6 had no commits in the last 10 days
1. mock delete 2 branches
```
(hello-world) ~/work/hello-world $ delete-branches --dry-run true --max-idle-days 10 --repo-url https://github.com/tagdots/hello-world --exclude-branches "test-1, test-2, badges"

🚀 Starting to Delete GitHub Branches (dry-run: True, exclude-branches: {'test-1', 'test-2', 'badges'}, max-idle-days: 10)

Current Time (UTC): 2025-08-20 17:08:32

Refined User Exclude Branch(es): {'badges'}
Default Branch                 : main
Protected Branch               : main
Pull Request Head Branch       : pr-branch-01

Total Number of Branches                         : 9
Total Number of Branches (Exempt-From-Delete)    : 3
Total Number of Branches (Not-Exempt-From-Delete): 6

From 6 Not-Exempt-From-Delete Branch(es),  2 had no commits in the last 10 day(s)
-------------------------------------------------------------------------------------------------
(MOCK) Delete branch - last update UTC 2025-08-09 13:49:34: branch-test-001
(MOCK) Delete branch - last update UTC 2025-08-08 03:29:34: branch-test-005
```

<br>

### 🔍 Example 3 - Delete branches with no commits longer than 10 days
**Summary**
1. exclude 1 branch: `badges`
1. remove branches without commits longer than 10 days

**Results**
1. refine excluded branches to `badges`
1. 3 branches are exempted from delete: `main`, `badges`, `pr-branch-01`
1. 6 branches are not exempted from delete and 2 out of 6 had no commits in the last 10 days
1. delete 2 branches
```
(hello-world) ~/work/hello-world $ delete-branches --dry-run false --max-days 10 --repo-url https://github.com/tagdots/hello-world --exclude-branches "badges"

🚀 Starting to Delete GitHub Branches (dry-run: True, exclude-branches: {'badges'}, max-idle-days: 10)

Current Time (UTC): 2025-08-20 17:26:55

Refined User Exclude Branch(es): {'badges'}
Default Branch                 : main
Protected Branch               : main
Pull Request Head Branch       : pr-branch-01

Total Number of Branches                         : 9
Total Number of Branches (Exempt-From-Delete)    : 3
Total Number of Branches (Not-Exempt-From-Delete): 6

From 6 Not-Exempt-From-Delete Branch(es),  2 had no commits in the last 10 day(s)
-------------------------------------------------------------------------------------------------
✅ Delete branch - last update UTC 2025-08-09 13:49:34: branch-test-001
✅ Delete branch - last update UTC 2025-08-08 03:29:34: branch-test-005
```

<br>

## 🔧 delete-branches command line options

| Input | Description | Default | Required | Notes |
|-------|-------------|----------|----------|----------|
| `repo-url` | Repository URL | `None` | Yes | e.g. https://github.com/{owner}/{repo} |
| `dry-run` | Dry-Run | `True` | No | - |
| `max-idle-days` | Maximum number of days without commits | `None` | No | enter number of days |
| `exclude-branches` | Branches excluded from deletion | `None` | No | comma seperated branches e.g. "branch1, branch2" |

<br>

## 😕  Troubleshooting

Open an [issue][issues]

<br>

## 🙏  Contributing

For pull requests to be accepted on this project, you should follow [PEP8][pep8] when creating/updating Python codes.

See [Contributing][contributing]

<br>

## 🙌 Appreciation
If you find this project helpful, please ⭐ star it.  **Thank you**.

<br>

## 📚 References

[How to fork a repo](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

<br>

[contributing]: https://github.com/tagdots/delete-branches/blob/main/CONTRIBUTING.md
[issues]: https://github.com/tagdots/delete-branches/issues
[pep8]: https://google.github.io/styleguide/pyguide.html
