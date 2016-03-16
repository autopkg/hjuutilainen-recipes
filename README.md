# What's this?

These are my recipes for [AutoPkg](https://github.com/autopkg/autopkg).

# Installation

Just run:

    $ autopkg repo-add hjuutilainen-recipes

Which of course requires that you have [AutoPkg installed](https://github.com/autopkg/autopkg/wiki/Getting-Started).

# Updating your configuration

These recipes were previously in [https://github.com/hjuutilainen/autopkg-recipes](https://github.com/hjuutilainen/autopkg-recipes). These commands will delete the old repo from your configuration and add a new repo with the updated URL:

    $ autopkg repo-delete https://github.com/hjuutilainen/autopkg-recipes.git
    $ autopkg repo-add https://github.com/autopkg/hjuutilainen-recipes.git
