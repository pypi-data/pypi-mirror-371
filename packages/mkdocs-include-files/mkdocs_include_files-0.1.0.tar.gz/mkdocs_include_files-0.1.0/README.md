# Mkdocs Include Files

The purpose of Mkdocs Include Files is to allow markdown files that don't naturally fit well living in the `docs` folder to be stored in the best spot. When its time to build the docs with `mkdocs build`, the specific files that need to be included will be copied into the `docs` folder.

## Usage

- `temp_location` is where the files will get moved to.  You would likely include this location in your .gitignore so they aren't committed.
- `search_syntax` would be a common file syntax that you would want for files to be copied to the `temp_location`.  Refer to [fnmatch](https://docs.python.org/3/library/fnmatch.html) for syntax details.
- `search_paths` is the paths to search that is relative to where the mkdocs.yml file is.

For example:
```
|_docs
|
|_src
    |_APP
mkdocs.yml
```

<h5 a><strong><code>mkdocs.yml</code></strong></h5>

```mkdocs.yml
plugins:
  - include-files:
      temp_location: include
      search_syntax: doc*.md
      search_paths: src/APP/
```

## Work to be done
- add ability to search multiple paths
- add ability to have multiple search syntaxes