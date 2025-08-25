use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use quick_xml::Reader;
use quick_xml::events::Event;
use std::io::{BufRead, BufReader, Write};
use std::fs::File;
use std::collections::VecDeque;
use rayon::prelude::*;
use crate::io::xml_utils::get_xml_node;

// Helper function to write tag with attributes to a buffer
fn write_tag_with_attributes(buf: &mut Vec<u8>, e: &quick_xml::events::BytesStart, self_closing: bool) {
    buf.extend_from_slice(b"<");
    buf.extend_from_slice(e.name().as_ref());
    for attr in e.attributes() {
        if let Ok(attr) = attr {
            buf.extend_from_slice(b" ");
            buf.extend_from_slice(attr.key.as_ref());
            buf.extend_from_slice(b"=\"");
            buf.extend_from_slice(&attr.value);
            buf.extend_from_slice(b"\"");
        }
    }
    if self_closing {
        buf.extend_from_slice(b"/>");
    } else {
        buf.extend_from_slice(b">");
    }
}

// Helper function to write opening tag with attributes to a buffer
fn write_opening_tag(buf: &mut Vec<u8>, e: &quick_xml::events::BytesStart) {
    write_tag_with_attributes(buf, e, false);
}

// Helper function to write self-closing tag with attributes to a buffer
fn write_self_closing_tag(buf: &mut Vec<u8>, e: &quick_xml::events::BytesStart) {
    write_tag_with_attributes(buf, e, true);
}

// Helper function to write closing tag to a buffer
fn write_closing_tag(buf: &mut Vec<u8>, e: &quick_xml::events::BytesEnd) {
    buf.extend_from_slice(b"</");
    buf.extend_from_slice(e.name().as_ref());
    buf.extend_from_slice(b">");
}

/// Hybrid streaming parser that uses quick_xml for streaming and parallel processing for batches
pub struct HybridStreamParser {
    batch_size: usize,
    element_queue: VecDeque<String>,
}

impl HybridStreamParser {
    pub fn new(_target_element: &str, batch_size: usize) -> Self {
        Self {
            batch_size,
            element_queue: VecDeque::new(),
        }
    }

    /// Add a complete element to the queue
    fn queue_element(&mut self, element_xml: String) {
        self.element_queue.push_back(element_xml);
    }

    /// Process batch if queue is full and write results
    fn process_batch_if_full<W: Write>(&mut self, writer: &mut W, total_count: &mut usize) -> Result<(), String> {
        if self.element_queue.len() >= self.batch_size {
            let results = self.process_batch();
            *total_count += results.len();

            // Write results
            for json_line in results {
                writeln!(writer, "{}", json_line)
                    .map_err(|e| format!("Write error: {}", e))?;
            }
        }
        Ok(())
    }

    /// Process a batch of elements in parallel
    fn process_batch(&mut self) -> Vec<String> {
        if self.element_queue.is_empty() {
            return Vec::new();
        }

        // Take up to batch_size elements
        let batch: Vec<String> = self.element_queue
            .drain(..self.batch_size.min(self.element_queue.len()))
            .collect();

        // Process in parallel using Rayon
        batch
            .par_iter()
            .filter_map(|xml_str| {
                // Parse each element
                match get_xml_node(xml_str) {
                    Ok(node) => {
                        // Convert XmlNode to serde_json::Value
                        let value = node.to_json();
                        // Serialize to string
                        match serde_json::to_string(&value) {
                            Ok(json) => Some(json),
                            Err(_) => None,
                        }
                    }
                    Err(_) => None,
                }
            })
            .collect()
    }

    /// Process remaining elements
    fn flush(&mut self) -> Vec<String> {
        let mut all_results = Vec::new();

        while !self.element_queue.is_empty() {
            let batch_results = self.process_batch();
            all_results.extend(batch_results);
        }

        all_results
    }
}

/// Stream parse file using quick_xml and process batches in parallel
pub fn hybrid_stream_parse<R: BufRead, W: Write>(
    reader: R,
    mut writer: W,
    target_element: &str,
    batch_size: usize,
) -> Result<usize, String> {
    let mut parser = HybridStreamParser::new(target_element, batch_size);
    let mut xml_reader = Reader::from_reader(reader);
    xml_reader.trim_text(true);

    let mut buf = Vec::new();
    let mut element_buf = Vec::new();
    let mut in_target = false;
    let mut depth = 0;
    let mut total_count = 0;

    let target_bytes = target_element.as_bytes();

    loop {
        match xml_reader.read_event_into(&mut buf) {
            Ok(Event::Start(ref e)) => {
                if e.name().as_ref() == target_bytes {
                    in_target = true;
                    depth = 1;
                    element_buf.clear();
                    write_opening_tag(&mut element_buf, e);
                } else if in_target {
                    depth += 1;
                    write_opening_tag(&mut element_buf, e);
                }
            }
            Ok(Event::End(ref e)) => {
                if in_target {
                    write_closing_tag(&mut element_buf, e);

                    depth -= 1;
                    if depth == 0 && e.name().as_ref() == target_bytes {
                        // Complete element found
                        in_target = false;

                        // Convert to string and queue
                        if let Ok(element_str) = String::from_utf8(element_buf.clone()) {
                            parser.queue_element(element_str);
                        }

                        // Process batch if queue is full
                        parser.process_batch_if_full(&mut writer, &mut total_count)?;

                        element_buf.clear();
                    }
                }
            }
            Ok(Event::Empty(ref e)) => {
                if e.name().as_ref() == target_bytes {
                    // This is a self-closing target element - collect and process it
                    let mut element_xml = Vec::new();
                    write_self_closing_tag(&mut element_xml, e);
                    
                    // Convert to string and queue
                    if let Ok(element_str) = String::from_utf8(element_xml) {
                        parser.queue_element(element_str);
                    }

                    // Process batch if queue is full
                    parser.process_batch_if_full(&mut writer, &mut total_count)?;
                }
            }
            Ok(Event::Text(ref e)) => {
                if in_target {
                    element_buf.extend_from_slice(e.as_ref());
                }
            }
            Ok(Event::Eof) => break,
            Err(e) => return Err(format!("XML parsing error: {}", e)),
            _ => {} // Ignore other events
        }

        buf.clear();
    }

    // Process remaining elements
    let final_results = parser.flush();
    total_count += final_results.len();

    for json_line in final_results {
        writeln!(writer, "{}", json_line)
            .map_err(|e| format!("Write error: {}", e))?;
    }

    Ok(total_count)
}

/// Python-exposed function: file input -> file output
#[pyfunction]
#[pyo3(signature = (input_path, target_element, output_path, batch_size=None))]
pub fn parse_xml_file_to_json_file(
    input_path: &str,
    target_element: &str,
    output_path: &str,
    batch_size: Option<usize>,
) -> PyResult<usize> {
    let batch_size = batch_size.unwrap_or(1000);

    let input_file = File::open(input_path)
        .map_err(|e| PyValueError::new_err(format!("Error opening input file: {}", e)))?;
    let reader = BufReader::new(input_file);

    let output_file = File::create(output_path)
        .map_err(|e| PyValueError::new_err(format!("Error creating output file: {}", e)))?;
    let writer = std::io::BufWriter::new(output_file);

    hybrid_stream_parse(reader, writer, target_element, batch_size)
        .map_err(|e| PyValueError::new_err(format!("Hybrid parsing error: {}", e)))
}

/// Python-exposed function: file input -> string output
#[pyfunction]
#[pyo3(signature = (input_path, target_element, batch_size=None))]
pub fn parse_xml_file_to_json_string(
    input_path: &str,
    target_element: &str,
    batch_size: Option<usize>,
) -> PyResult<String> {
    let batch_size = batch_size.unwrap_or(1000);

    let input_file = File::open(input_path)
        .map_err(|e| PyValueError::new_err(format!("Error opening input file: {}", e)))?;
    let reader = BufReader::new(input_file);

    let mut output = Vec::new();

    hybrid_stream_parse(reader, &mut output, target_element, batch_size)
        .map_err(|e| PyValueError::new_err(format!("Hybrid parsing error: {}", e)))?;

    String::from_utf8(output)
        .map_err(|e| PyValueError::new_err(format!("UTF-8 conversion error: {}", e)))
}

/// Python-exposed function: string input -> file output
#[pyfunction]
#[pyo3(signature = (xml_content, target_element, output_path, batch_size=None))]
pub fn parse_xml_string_to_json_file(
    xml_content: &str,
    target_element: &str,
    output_path: &str,
    batch_size: Option<usize>,
) -> PyResult<usize> {
    let batch_size = batch_size.unwrap_or(1000);

    let reader = std::io::Cursor::new(xml_content.as_bytes());

    let output_file = File::create(output_path)
        .map_err(|e| PyValueError::new_err(format!("Error creating output file: {}", e)))?;
    let writer = std::io::BufWriter::new(output_file);

    hybrid_stream_parse(reader, writer, target_element, batch_size)
        .map_err(|e| PyValueError::new_err(format!("Hybrid parsing error: {}", e)))
}

/// Python-exposed function: string input -> string output
#[pyfunction]
#[pyo3(signature = (xml_content, target_element, batch_size=None))]
pub fn parse_xml_string_to_json_string(
    xml_content: &str,
    target_element: &str,
    batch_size: Option<usize>,
) -> PyResult<String> {
    let batch_size = batch_size.unwrap_or(1000);

    let reader = std::io::Cursor::new(xml_content.as_bytes());

    let mut output = Vec::new();

    hybrid_stream_parse(reader, &mut output, target_element, batch_size)
        .map_err(|e| PyValueError::new_err(format!("Hybrid parsing error: {}", e)))?;

    String::from_utf8(output)
        .map_err(|e| PyValueError::new_err(format!("UTF-8 conversion error: {}", e)))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Cursor;

    #[test]
    fn test_hybrid_stream_parser_new() {
        let parser = HybridStreamParser::new("Record", 100);
        assert_eq!(parser.batch_size, 100);
        assert!(parser.element_queue.is_empty());
    }

    #[test]
    fn test_basic_xml_parsing() {
        let xml = r#"<?xml version="1.0"?>
<root>
    <Item id="1"><Value>100</Value></Item>
    <Item id="2"><Value>200</Value></Item>
</root>"#;

        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();

        let result = hybrid_stream_parse(reader, &mut output, "Item", 10);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 2);

        let output_str = String::from_utf8(output).unwrap();
        assert!(output_str.contains("\"id\":\"1\""));
        assert!(output_str.contains("\"Value\":\"100\""));
        assert!(output_str.contains("\"id\":\"2\""));
    }

    #[test]
    fn test_empty_xml() {
        let xml = "<?xml version=\"1.0\"?><root></root>";
        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();

        let result = hybrid_stream_parse(reader, &mut output, "Item", 10);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 0);
        assert!(output.is_empty());
    }

    #[test]
    fn test_batch_size_variations() {
        let xml = r#"<?xml version="1.0"?>
<root>
    <R id="1"/>
    <R id="2"/>
    <R id="3"/>
    <R id="4"/>
    <R id="5"/>
</root>"#;

        // Test with batch size 1
        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();
        let result = hybrid_stream_parse(reader, &mut output, "R", 1);
        assert_eq!(result.unwrap(), 5);

        // Test with batch size 3
        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();
        let result = hybrid_stream_parse(reader, &mut output, "R", 3);
        assert_eq!(result.unwrap(), 5);

        // Test with batch size 10 (larger than element count)
        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();
        let result = hybrid_stream_parse(reader, &mut output, "R", 10);
        assert_eq!(result.unwrap(), 5);
    }

    #[test]
    fn test_attributes_handling() {
        let xml = r#"<?xml version="1.0"?>
<root>
    <Item id="123" type="test" enabled="true"/>
</root>"#;

        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();

        let result = hybrid_stream_parse(reader, &mut output, "Item", 10);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 1);

        let output_str = String::from_utf8(output).unwrap();
        assert!(output_str.contains("\"id\":\"123\""));
        assert!(output_str.contains("\"type\":\"test\""));
        assert!(output_str.contains("\"enabled\":\"true\""));
    }

    #[test]
    fn test_invalid_xml() {
        // Test with malformed XML - the parser may handle some incomplete XML gracefully
        let xml = "<root><Item>Unclosed";
        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();

        let result = hybrid_stream_parse(reader, &mut output, "Item", 10);
        // The parser handles incomplete XML by returning 0 elements
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 0);
    }

    #[test]
    fn test_self_closing_target_elements() {
        // Test that self-closing elements are properly captured when they ARE the target
        let xml = r#"<?xml version="1.0"?>
<root>
    <Item id="1" status="active"/>
    <Item id="2" status="inactive"/>
    <Item id="3"><Name>With Content</Name></Item>
</root>"#;

        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();

        let result = hybrid_stream_parse(reader, &mut output, "Item", 10);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 3); // Should capture all 3 items

        let output_str = String::from_utf8(output).unwrap();
        // Check all items are captured
        assert!(output_str.contains("\"id\":\"1\""));
        assert!(output_str.contains("\"id\":\"2\""));
        assert!(output_str.contains("\"id\":\"3\""));
        assert!(output_str.contains("\"status\":\"active\""));
        assert!(output_str.contains("\"status\":\"inactive\""));
        assert!(output_str.contains("With Content"));
    }

    #[test]
    fn test_special_characters() {
        let xml = r#"<?xml version="1.0"?>
<root>
    <Item>Text&lt;&gt;&amp;&quot;&apos;</Item>
</root>"#;

        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();

        let result = hybrid_stream_parse(reader, &mut output, "Item", 10);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 1);

        let output_str = String::from_utf8(output).unwrap();
        // Check that special characters are unescaped in JSON
        assert!(output_str.contains("<>&"));
    }

    #[test]
    fn test_nested_elements() {
        let xml = r#"<?xml version="1.0"?>
<root>
    <Item id="1">
        <Child>
            <GrandChild>Value</GrandChild>
        </Child>
    </Item>
</root>"#;

        let reader = Cursor::new(xml.as_bytes());
        let mut output = Vec::new();

        let result = hybrid_stream_parse(reader, &mut output, "Item", 10);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), 1);

        let output_str = String::from_utf8(output).unwrap();
        assert!(output_str.contains("\"Child\""));
        assert!(output_str.contains("\"GrandChild\""));
    }
}