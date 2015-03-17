# Source Code Policy #

DTA Anyway should be useful and reusable to others who want to develop DTA.  To that end, the following policies will be applied to source code that gets added to this repository:

  * Style should adhere to the [PEP 8 -- Style Guide for Python Code](http://www.python.org/dev/peps/pep-0008/)
  * In particular, take note of the docstring requirement; these will be used to generate [Sphinx](http://sphinx.pocoo.org/)-based HTML documentation pages.
> > Write docstrings for all public modules, functions, classes, and
> > methods.  Docstrings are not necessary for non-public methods, but you
> > should have a comment that describes what the method does.  This
> > comment should appear after the "def" line.
  * The code should be standalone; that is, the only imports should be released, versioned python modules.

# Workflow #

For each subtask, the workflow will be:
  * Definition: Define and document subtask functional specifications as wiki document (inputs, outputs, behavior) - Task Leader
  * Design: Technical specification, including class and/or object diagrams, stub API for major tasks or changes, but discussion will suffice for smaller changes.  This will likely be shared between different tasks because of the common code-base and so it really serves as the technical documentation - Task Leader or can be designated to primary implementer
  * Signoff - All task contributors
  * Implementation: code checkins at least weekly on the dev branch.  Functional and technical specs should be updated as required. - All task contributors
  * Code Review - Task Leader
  * Code Review Followup if necessary - All relevant task contributors
  * Branch merge of feature branch into master -  Task Leader

# Tests #

Test all code before committing to main repository.  Please read our documentation about [How to Write Tests](http://code.google.com/p/dta/wiki/TestingSuite) .