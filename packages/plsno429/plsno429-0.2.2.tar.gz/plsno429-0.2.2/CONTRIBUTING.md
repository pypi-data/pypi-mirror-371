# Contributing to plsno429
Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

## Table of Contents

1. [How to Contribute](#how-to-contribute)
2. [Reporting Issues](#reporting-issues)
3. [Creating a Pull Request (PR)](#creating-a-pull-request-pr)
4. [Coding Style Guidelines](#coding-style-guidelines)
5. [Writing Tests](#writing-tests)
6. [Other Contributions](#other-contributions)

## How to Contribute

1. Fork the repository and clone it to your local machine:

    ```bash
    git clone https://REPO_URL/REPO_USERNAME/plsno429.git
    ```

2. Create a new branch for your changes:

    ```bash
    git checkout -b feature/new-feature
    ```

3. Make your changes and commit them with a clear message with conventional commit:

    ```bash
    git add .
    git commit -m "feat: Add a clear and concise commit message"
    ```

4. Push your changes to the remote repository:

    ```bash
    git push origin feature/new-feature
    ```

5. Create a Pull Request (PR) on GitHub.

## Reporting Issues

### Bug Reports

- Use the **issue tracker** to report any bugs you find.
- Provide as much detail as possible and steps to reproduce the issue.
- If applicable, include screenshots or log files.

### Feature Requests

- Use the **issue tracker** to suggest new features.
- Explain what problem the feature would solve or why it would be beneficial.

## Creating a Pull Request (PR)

- Use **Fork** to create a copy of the repository in your GitHub account, then make changes in a new branch.
- Do not push changes directly to the `main` or `master` branch.
- Before submitting a PR, ensure that your changes are adequately tested.
- Provide a clear and detailed description of your changes in the PR title and description.
- During the review process, you may be asked to make additional changes based on feedback.

## Coding Style Guidelines

- Use 4 spaces for indentation.
- Use clear and descriptive names for variables and functions.
- Comment your code to explain the intent behind complex sections.

## Writing Tests

- When adding new features or fixing bugs, please include relevant tests.
- Tests should be written using `pytest`.
- Run tests to ensure they pass:

    ```bash
    uv run pytest
    ```

## Other Contributions

- Documentation is a critical part of the project, and contributions to it are also welcomed.
- Run `mkdocs` for documentation:

    ```bash
    uv run mkdocs build
    ```

- Please adhere to the project's Code of Conduct.

Thank you! Your contributions make this project better for everyone.
