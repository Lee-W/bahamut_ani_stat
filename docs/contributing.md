### Step 1. Fork this repository to your GitHub

### Step 2. Clone the repository from your GitHub

```sh
git clone https://github.com/[YOUR GITHUB ACCOUNT]/bahamut_ani_stat.git
```

### Step 3. Add this repository to the remote in your local repository

```sh
git remote add upstream "https://github.com/Lee-W/bahamut_ani_stat"
```

You can pull the latest code in main branch through `git pull upstream main` afterward.

### Step 4. Check out a branch for your new feature

```sh
git checkout -b [YOUR FEATURE]
```

### Step 5. Install prerequisite

```sh
python -m pip install pipx
python -m pipx install poetry invoke
python -m pipx ensurepath
```

* [pipx](https://github.com/pipxproject/pipx): for python tool management
* [poetry](https://python-poetry.org/): for dependency management
* [invoke](https://github.com/pyinvoke/invoke): for task management

### Step 6. Create your local Python virtual environment and install dependencies

```sh
inv env.init-dev
```

### Step 7. Work on your new feature

Note that this project follows [conventional-commit](https://www.conventionalcommits.org/en/v1.0.0/) and bumps version based on it. Use the following command to commit your changes.

```sh
inv git.commit
```

### Step 8. Run test cases

Make sure all test cases pass.

```sh
inv test
```

### Step 9. Run test coverage

Check the test coverage and see where you can add test cases.

```sh
inv test.cov
```

### Step 10. Reformat source code

Format your code through `ruff`.

```sh
inv style.format
```

### Step 11. Run style check

Make sure your coding style passes all enforced linters.

```sh
inv style
```

[Optional] Check your coding style through `pylint`. Note that you do not have to fix all the issues warned by `pylint`.

```sh
inv style.pylint
```

### Step 12. Run security check

Ensure the packages installed are secure, and no server vulnerability is introduced

```sh
inv secure
```

### Step 13. Create a Pull Request and celebrate 🎉
