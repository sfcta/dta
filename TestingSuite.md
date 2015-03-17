## Unit Test Package ##

We are using the nose python software package, which extends the built in python unit test package.

To install nose from the command line (must have setup tools installed):
`easy_install nose`

## How to write tests ##
[Nose Documentation](http://nose.readthedocs.org/en/latest/writing_tests.html)

Nose uses a regex that recognizes `test_` and `Test_` to find what it needs to run.

Basically:
  * Put all tests in the `\test` sub-folder
  * Name test python files with something that starts with `test_`
  * `import nose.tools' should be used to make sure nose is included.
  * Write functions that start with `test_` that you want to be run.
  * Each function should have an `assert` line, where the answer the function gets should be compared with the 'known answer'
  * All data needed to run the tests should be included in the `testData` sub-folder