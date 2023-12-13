# Welcome to Pokie


[![Tests](https://github.com/oddbit-project/pokie/workflows/Tests/badge.svg?branch=master)](https://github.com/oddbit-project/pokie/actions)
[![pypi](https://img.shields.io/pypi/v/pokie.svg)](https://pypi.org/project/pokie/)
[![license](https://img.shields.io/pypi/l/pokie.svg)](https://git.oddbit.org/OddBit/pokie/src/branch/master/LICENSE)

Pokie is an API-oriented modular web framework built on top of [Flask](https://github.com/pallets/flask/),
[Rick](https://git.oddbit.org/OddBit/rick) and [Rick-db](https://git.oddbit.org/OddBit/rick_db) libraries, following three-layer and clean architecture
design principles.

It features an object-oriented design, borrowing from common patterns found in other languages, such as
dependency injection, service location, factories and object composition. It also offers the following functionality:

- Modular design;
- Dependency registry; 
- CLI command support;
- Jobs (objects invoked periodically to perform a task);
- Fixtures;
- Unit testing support with pytest;
- Code generation;
- REST-oriented service design; 
- Compatibility with Flask;



Contents:

* [Pokie Tutorial](tutorial/tutorial.md)
* [Pokie Views](http/views.md)
* [Pokie REST Views](http/rest.md)
* [Grid Requests](http/dbgridrequest.md)
* [JSON Responses](http/json_response.md)
* [Global Error Handling](http/error_handler.md)
* [Unit Tests with pytest](test/pytest.md)