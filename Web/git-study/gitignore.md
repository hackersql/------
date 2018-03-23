Ignoring files

From time to time there are files you don't want git to track. There are a few methods of telling git what files to ignore.

.gitignore

If you create a file in your repository named .gitignore git will use its rules when looking at files to commit.
Note that git will not ignore a file that was already tracked before a rule was added to this file to ignore it. 
In such a case the file must be un-tracked, usually with git rm --cached filename
if you want to ignore a dir, you may be want to use git rm --cached -r dirName.

Global .gitignore

A global .gitignore file can also be very useful for ignoring files in every git repositories on your computer. 
For example, you might create the file at ~/.gitignoreglobal and add some rules to it. 
To add this file to your cross-repository configuration, run git config --global core.excludesfile ~/.gitignoreglobal

Here are some good rules to add to this file:

# Compiled source #
###################
*.com
*.class
*.dll
*.exe
*.o
*.so

# Packages #
############
# it's better to unpack these files and commit the raw source
# git has its own built in compression methods
*.7z
*.dmg
*.gz
*.iso
*.jar
*.rar
*.tar
*.zip

# Logs and databases #
######################
*.log
*.sql
*.sqlite

# OS generated files #
######################
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

You may also want to check out GitHub's gitignore repository, which contains a list of .gitignore files for many popular operating systems, environments, and languages.


same as the file .git/info/exclude


