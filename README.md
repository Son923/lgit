# lgit
Lightweight version of git

lgit
Core project
Notions: git basics
Introduction
Version control is a powerful tool for collaborative teams. It might seem overly complicated for the purpose of just saving some code, and you might have already been traumatised by some wild git conflict on your own projects... every aspiring developer gets scared by git at some point! But imagine working in a team of a dozen developers on a project that has several features being developed in parallel: you need a smart process to ensure the tracking & integrity of the main project and a way to incorporate smoothly the new features.

Therefore, over the next two weeks, you will understand what version control is by looking under the hood and coding your own version of git. Understand how git works, and you will never waver in front of a conflict again!

Your mission
Your task is to code a lightweight version of git. The goal is to understand how git works so that you can make sense of the magic that happens when you "git add / git commit / git push" - and save yourself of any git trouble you might encounter in the future as you work on large teams.

As the actual implementation of git is a bit complex, we'll work on a simplified version together, step by step. While simplified a little, this version still gives an accurate representation of how git works.

Your program will be called lgit.py and will implement versioning locally, but you don't have to handle remotes (so no pull, fetch or push).

First: what is Git?
Git is a type of database: it records the state of the files in your working directory, which allows you to have a clear picture of what your directory contains at a given moment.

Git stores all its data in a hidden directory named .git. That directory is created when you type the command git init in a new directory, as tracking is initialised in that directory.

From there, any time you use a git command (git add, git commit, git status...), git will read and update the information stored in the .git directory. Destroy the .git directory, and you lose absolutely all tracking information! 🔥


  
The key concepts
The main thing to understand is that, contrary to other version control systems, git records a full picture (a "snapshot") of your working directory every time you do a git commit. Every commit is a file listing that represents the exact state of your tracked files at one point.

What happens when you update a file? Git doesn't bother recording the difference between the new version and the old version, it actually just stores the new version of the file. This makes retrieving a version of a file extremely easy, as you just have to fetch it from the git database. Let's repeat it: git stores full files, and not just "updates" to a file. (This is actually not an absolute rule, but it's enough for our project today.)

Now the last thing to understand is what is the index. The index is a "temporary snapshot" that contains what will effectively be stored if you do a git commit. The index is a listing of all the files you have git add'ed previously, and when you type in git commit what you effectively do is make a permanent copy of that snapshot. That index is also called the staging area, because it's the area where you make changes, add files, remove files (you "stage" your files... like a theater director!); and when you are perfectly content with what it looks like, you commit that snapshot permanently in your git history. Basically, a git commit says "I want to remember my directory in exactly that state, please archive a picture of my staging area, kthkbay."

Your .lgit directory structure
For the purpose of simplification, we will use the following directory structure:

a directory objects will store the files you lgit add
a directory commits will store the commit objects: those are not the actual file listings but some information about the commit (author, date & commit message)
a directory snapshots will store the actual file listings
a file index will host the staging area & other information
a file config will store the name of the author, initialised from the environment variable LOGNAME
The command lgit init will create the directory structure.

If a lgit command is typed in a directory which doesn't have (nor its parent directories) a .lgit directory, lgit will exit with a fatal error.


  
Structure of the "objects" directory
When you lgit add a file, what you do is store a copy of the file content in the lgit database.

File contents will be stored in the lgit database with their SHA1 hash value. It means that you have to calculate the SHA1 value of the file content, and you will use the SHA1 value to retrieve the file content at any time.

Each file will be stocked in the following way:

the first two characters of the SHA1 will be the directory name
the last 38 characters will be the file name
Let's look at an example!


  
Structure of the "index" file
If you remember, the "index" file is our staging area: it's where we keep all current file information before we commit anything to the permanent "commits"/"snapshots" directories.

Each line in the index file will correspond to a tracked file and will contain 5 fields.

1: the timestamp of the file in the working directory
2: the SHA1 of the content in the working directory
3: the SHA1 of the file content after you lgit add'ed it
4: the SHA1 of the file content after you lgit commit'ed it
5: the file pathname
So basically the index has information about the content of a given file (as identified by its name) at different stages.

Let's go back to our example. I just added a file called test, let's look at the index. Since I just added the file, the content is the same in the staging as in the working directory. We have never done a commit so there's no hash in the fourth field.


  
lgit status
Let's modify again the test file. We then run lgit status to update the index and... surprise, the file appears both as "to be committed" and "not staged for commit"! How is it possible?

Well, look at the index file. We had already once lgit add'ed the file, so lgit already has a version ready to be committed. You can check, the SHA1 in the middle didn't change.

But we also modified that file in the current directory, so the index has been updated with the new file timestamp and the SHA1 representing the new file content in the working directory.

And you can check that the first SHA1 *isn't* present in the objects directory. That's because it's just the state of the file in the current directory, but we have never lgit add'ed it!


  
lgit status: untracked files
lgit status not only updates the index but also reports on the files that are "untracked" by lgit. Those are the files that are present in the working directory, but have never been lgit add'ed.


  
lgit commit, the commit object & the snapshot
Okay, let's actually commit the changes (that is, tell lgit to store the snapshot permanently).

The commit object and the snapshot are simplified here compared to what git actually does, but the principle is the same.

Both objects have the same name (here it's the timestamp with milliseconds, you can use another way to name your files if you want) and are in their respective folders.

Your commit object will contain the following information:

author name
time of the commit
an empty line
the commit message
The snapshot is a simplified version of the index with just the SHA1 of the staged content and the filename.

Let's walk through an example!


  
lgit log
Now that you have worked hard, you might want to see all those commits you did! The lgit log command should display all commits, sorted in descending order, with the following information:

your commit identifier (for lgit we will use the commit filename, the real git uses the SHA1 of the commit)
a field with the author of the commit
a field with a human-readable date
and the commit message

  
Directions
Now hopefully after that slow walk-through, you have a good idea of how your lgit program works and interacts with the .lgit directory.

It's time for you to code your own!

Here are the commands that must be present in your project:

lgit init: initialises version control in the current directory (until this has been done, any lgit command should return a fatal error)
lgit add: stages changes, should work with files and recursively with directories
lgit rm: removes a file from the working directory and the index
lgit config --author: sets a user for authoring the commits
lgit commit -m: creates a commit with the changes currently staged (if the config file is empty, this should not be possible!)
lgit status: updates the index with the content of the working directory and displays the status of tracked/untracked files
lgit ls-files: lists all the files currently tracked in the index, relative to the current directory
lgit log: shows the commit history
You must respect the directory structure & files indicated in the subject.
