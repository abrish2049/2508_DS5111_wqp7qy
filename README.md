# 2508_DS5111_wqp7qy

   ## Prerequisites

   - A fresh Ubuntu VM
   - GitHub SSH key configured and added to your GitHub account

   ## Setup

   ### 1. Clone the repository

   ```bash
   git clone git@github.com:abrish2049/2508_DS5111_wqp7qy.git
   cd 2508_DS5111_wqp7qy

   2. Initialize the VM

   bash init.sh

   This updates system packages and installs make, python-venv, and tree.

   Verify:

   - make --version — returns version info
   - tree --version — returns version info

   3. Configure git credentials

   bash init_git_creds.sh

   This sets your git user email and name globally.

   Verify: git config --global --list shows your name and email.

   4. Run the project

   make

   Verify: Runs without errors.
