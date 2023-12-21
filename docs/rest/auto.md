# Automatic REST generation

Common REST scenarios include CRUD interaction with a database object (a view, a table or a predefined query); these
often involve a *RequestRecord* with request validation rules, a *DTO Record* representing the database object, a
*Service* that implements domain logic, and obviously a *RestView* to implement the different endpoints.

Pokie's *rest.Auto* helpers leverage the existing [Code Generation](../codegen/codegen.md) mechanisms to generate in
runtime the required classes for a barebones operation. These classes can be incrementally overridden later,
making them ideal in PoC and simple use cases. They can also be used to perform rapid prototyping - implementations can be done incrementally, starting with automatic helpers and gradually
implementing the specific business logic.

> **Note:** The *rest.Auto* database funcionality is only available for PostgreSQL databases.

## Automatic REST from DTO


## Automatic REST from Database Table