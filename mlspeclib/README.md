The purpose of MLSpec Lib is to provide a library that can easily read and write schema-tized metadata related to the steps in an ML Pipeline.

The original set of schema was drawn from here - - as a set of illustrative data for initial specs.

If you had a sample pipeline that did the following:
- Read data
- Transformed the data in some way and saved it to a new directory
- Trained a model based on the data
- Wrote the results of the training to a new directory
- Converted the model to a training format
- Created a serving endpoint for the model

At each step, you would want to use first class python objects to drive the workflow, and, ideally, you would want to read/write
metadata about what you were doing to have a permenant record.

This is what MLSpecLib is designed to do:
- Read the metadata in
- Provide a first class Python object for use
- Allow validation of the Python object according to a schema
- Write the object to disk in a readable YAML format

To see it in action, go to the Sample Notebook.

*** NOTE: The Sample Notebook is illustrative only! It does not actually execute any actual training and the schema are just for examples. ***