# How To Get Code #
### Get Git ###
[Download Git](http://git-scm.com/download)

### [Using Git in command line](http://google-opensource.blogspot.com/2008/05/develop-with-git-on-google-code-project.html) ###
**Read-only**
In git-bash session, cd to a directory you want to download it to.
```
git clone http://code.google.com/p/dta
cd dta
git checkout <branch name>  \\i.e. git checkout dev, to check out the development branch, since that is where most of the work is
```

**Read/Write**
Note: you must be an approved committer on the project in order to do this! email elizabeth@sfcta.org for more info.
In git-bash session, cd to a directory you want to download it to.
```
git clone https://<googlecodeusername>@code.google.com/p/dta
cd dta
git checkout <branch name>  \\i.e. git checkout dev, to check out the development branch, since that is where most of the work is
```

i.e. for Elizabeth, this is
```
git clone https://elizabeth%40sfcta.org@code.google.com/p/dta/ 
```

### Documenting your changes with commits ###
Once you've made a change that you want to document, add the changed files and then "commit" them with a message about what they are.

i.e.
```
git status            ## shows what you've added
git add __init__.py   ## adds a specific file that you've changed to the queue
git add .             ## adds ALL files to the queue
git status            ## will list changes that are staged to be committed
git commit -m "This commit will do A, B, and C"  ## commits the change
git status
```

### Pushing your changes to the repository ###
After you've committed your changes to the local git repository, you might want others to see them!  Note that you can only do this if you have write-access to the repository.

Also you will need to make sure you have the correct settings for your google code account w.r.t. passwords.  I usually check the box: "Accept xxx@sfcta.org Google Account password" on https://code.google.com/hosting/settings


i.e.
```
git remote              ## shows you what remote repositories you can access, this should always include "origin", which is where you cloned the repository from.  In most cases, you will want to push to origin.
git push origin master  ## this pushes your master branch on the local repository to the master branch on the "origin" repository.
```

### Using Eclipse ###
  1. File-->Import-->Git-->Checkout Projects from Git
  1. Create a new repository location
> > Url: https://dta.googlecode.com/svn/branches/
  1. Checkout as a project in the workspace: dta (note we need to update this stuff)
  1. Fully Recursive (to get history)
  1. It is helpful to have python development tools available, so once it is imported, right click on project-->PyDev-->Set as PyDev project

  * install PyDev by going to help-->add software-->new site, http://pydev.org/updates