# apisql

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/apisql.svg)

apisql is a flask blueprint providing an API for read-only access for a DBMS using direct SQL Queries

## endpoints

### `/query`

Returns query results in json format.

Query parameters that can be send:
- **query**: The SQL query to execute on the DB. The query can be provided in plain text or base64 encoded.
- **num_rows**: The maximum number of rows to return. If not specified, will return the aount defined in the configuration, the amount defined in the environment variable `APISQL__MAX_ROWS` or 100.
- **page_size**: The size of the 'page', when doing paging. By default will use `num_rows` and in any way the page size it won't exceed `num_rows`.
- **page**: Which page to fetch, starting from page 0

### `/download`

Downloads query results in either csv, xls or xlsx format.

Query parameters that can be send:
- **query**: The SQL query to execute on the DB. The query can be provided in plain text or base64 encoded.
- **format**: Either `csv` or `xlsx`. Defaults to `csv`.
- **filename**: The filename for the file to be downloaded, *without the extension*. Defaults to `query-results`.
- **headers**: A semicolon separated list of the headers for the output file. Headers should match the field names that appear in the query.
  Headers may contain one or more modifiers, which appear after a colon. The currently supported modifiers are:
  - `number`, to convert numeric values to strings
  - `yesno`, which converts boolean values to "Yes" / "No"
  - `comma-separated`, which converts arrays of strings to a comma separated list of these strings.
  Finally, the content for a column may be fetched from a different field in the query output, by specifying the field name after a `<` character.

  Example:
  `Fiscal Year:number<fiscal_year;Leap Year:yesno<0;`



**Example:**
For the following SQL:
```
select employee_name as "Employee Name", employee_salary as "Salary", is_manager as "Managerial role?" from employees
```

`headers` could be specified as `Employee Name;Managerial role?:yesno;Salary:number`.

## configuration

Flask configuration for this blueprint:


```python

    from apisql import apisql_blueprint

    app.register_blueprint(
        apisql_blueprint(connection_string='psql://host/database', max_rows=1000, debug=False),
        url_prefix='/api/db/'
    )
```
