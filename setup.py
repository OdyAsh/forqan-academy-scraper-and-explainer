# setup.py - minimal stub since we're using pyproject.toml and setup.cfg for configuration
# EXPLANATION NOTE: more details here: 
# https://medium.com/@joshuale/a-practical-guide-to-python-project-structure-and-packaging-90c7f7a04f95#:~:text=Use%20Case%201%3A%20When%20you%20want%20to%20install%20the%20whole%20src-equivalent%20folder%20as%20a%20package
# Now we should run `pip install -e .` in the terminal 
# to install the packages found in forqan_academy_scraper_and_explainer/
# in order to be easily imported by python scripts found in scripts/

# EXPLANATION NOTE: check this link to understand more about the pip command above:
# https://www.reddit.com/r/learnpython/comments/ayx7za/comment/ei407ao/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

# DEBUGGING NOTE: check these links (in order) ONLY IF you face the PyLance issue in the first link below:
# PyLance issue: https://stackoverflow.com/questions/76532312/pylance-does-not-recognize-local-packages-installed-with-pip-install-e#:~:text=could%20not%20be%20resolved%20and%20Intellisense%20fails
# its solution: https://github.com/microsoft/pylance-release/issues/3473#issuecomment-1278116834
# official documentation of the solution: https://setuptools.pypa.io/en/latest/userguide/development_mode.html#strict-editable-installs
# tricky note: remember not to delete the `build/` direectory: https://setuptools.pypa.io/en/latest/userguide/development_mode.html#strict-editable-installs:~:text=Please%20be%20careful%20to%20not%20remove%20this%20directory%20while%20testing%20your%20project%2C%20otherwise%20your%20editable%20installation%20may%20be%20compromised

from setuptools import setup
if __name__ == '__main__':
    setup()