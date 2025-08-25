# Oxidize

High-performance XML to JSON streaming parser built with Rust and PyO3. Specialized for extracting repeated elements from large XML files like API responses, log files, and data exports.

## Key Features

- **High Performance**: 2-3x faster than lxml, built with Rust's quick-xml parser with batch processing in Rayon
- **Low Memory Usage**: Streaming architecture processes files larger than available RAM
- **Specialized Design**: Opinionated API and schema design for common data engineering and data analysis workflows

## Use Cases

Perfect for extracting structured data from XML files containing repeated elements into newline JSON
- **API responses**: Extract `<record>`, `<item>`, or `<entry>` elements from REST API responses
- **Log files**: Parse `<event>` or `<log>` entries from XML-formatted logs
- **Data exports**: Process `<row>`, `<product>`, or `<transaction>` elements from database exports
- **Configuration files**: Extract `<server>`, `<user>`, or similar repeated configuration blocks

## Installation

```bash
./build_rust_utils.sh
```

## Usage

Extract specific elements from XML and convert to JSON-Lines:

```python
import oxidize

# File to file
count = oxidize.parse_xml_file_to_json_file("data.xml", "book", "books.json")

# File to string  
json_lines = oxidize.parse_xml_file_to_json_string("data.xml", "book")

# String to string
result = oxidize.parse_xml_string_to_json_string(xml_content, "book")

# Control batch size (default 1000)
oxidize.parse_xml_file_to_json_file("huge.xml", "record", "out.json", batch_size=500)
```

## Conversion Rules

**Uniform arrays**: All elements become arrays for consistent schema inference:

```xml
<book id="bk101">
    <author>J.K. Rowling</author>
    <title>Harry Potter</title>
</book>
```

```json
{
  "@id": "bk101",
  "author": ["J.K. Rowling"], 
  "title": ["Harry Potter"]
}
```

**Key behaviors:**
- **Attributes**: Prefixed with `@` to avoid conflicts with element names
- **Mixed content**: Text in elements with children stored as `#text` entries
- **Empty elements**: Self-closing/empty tags become `null` values
- **Structure preservation**: Element order maintained via IndexMap
- **Namespace handling**: Prefixes kept in element names, declarations treated as attributes

**Ignored features:**
- Processing instructions, DTDs, comments (not relevant for data extraction)
- Custom entity definitions (entity references passed through as text)
- Character references automatically unescaped by quick_xml

## Data Processing

### Pandas  
```python
json_lines = oxidize.parse_xml_file_to_json_string("data.xml", "record")
records = [json.loads(line) for line in json_lines.strip().split('\n')]
df = pd.json_normalize(records)
```

### Polars
```python
oxidize.parse_xml_file_to_json_file("data.xml", "record", "temp.json")
# Use infer_schema_length=None and eager loading for unknown schemas
df = pl.read_json("temp.json", infer_schema_length=None)
# Use lazy loading for known schemas
lf = pl.scan_ndjson("temp.json")
```

### DuckDB
```python
oxidize.parse_xml_file_to_json_file("data.xml", "record", "data.json") 
df = duckdb.sql("SELECT * FROM read_json_auto('data.json')").df()
```

## API

```python
parse_xml_file_to_json_file(input_path, target_element, output_path, batch_size=1000) -> int
parse_xml_file_to_json_string(input_path, target_element, batch_size=1000) -> str  
parse_xml_string_to_json_file(xml_content, target_element, output_path, batch_size=1000) -> int
parse_xml_string_to_json_string(xml_content, target_element, batch_size=1000) -> str
```
