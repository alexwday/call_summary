#!/usr/bin/env python3
"""
XML Structure Explorer
Analyzes an XML file and outputs its complete structure, including:
- Element hierarchy
- Attributes
- Sample text content
- Element counts
- Namespace information
"""

import xml.etree.ElementTree as ET
from collections import defaultdict
import json
import sys
import os
from typing import Dict, List, Any, Optional


class XMLStructureExplorer:
    """Explores and documents XML file structure."""

    def __init__(self):
        self.element_counts = defaultdict(int)
        self.element_attributes = defaultdict(set)
        self.element_texts = defaultdict(list)
        self.element_children = defaultdict(set)
        self.element_parents = defaultdict(set)
        self.namespaces = {}
        self.root_element = None

    def explore_xml(self, file_path: str) -> Dict[str, Any]:
        """
        Main method to explore XML structure.

        Args:
            file_path: Path to XML file

        Returns:
            Dictionary containing complete structure analysis
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            self.root_element = root.tag

            # Extract namespaces
            self._extract_namespaces(root)

            # Recursively explore structure
            self._explore_element(root, parent=None)

            # Build structure report
            return self._build_report()

        except Exception as e:
            return {"error": f"Failed to parse XML: {str(e)}"}

    def _extract_namespaces(self, element):
        """Extract all namespaces from the document."""
        # Get namespaces from root element
        for key, value in element.attrib.items():
            if key.startswith("xmlns"):
                prefix = key.split(":")[-1] if ":" in key else "default"
                self.namespaces[prefix] = value

    def _explore_element(self, element, parent: Optional[str] = None, path: str = ""):
        """Recursively explore XML element structure."""
        # Clean tag name (remove namespace)
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag
        current_path = f"{path}/{tag}" if path else tag

        # Count element occurrences
        self.element_counts[current_path] += 1

        # Track parent-child relationships
        if parent:
            self.element_children[parent].add(tag)
            self.element_parents[tag].add(parent)

        # Collect attributes
        for attr_name, attr_value in element.attrib.items():
            # Store attribute with sample value
            self.element_attributes[current_path].add(f"{attr_name}={attr_value[:50]}")

        # Collect text content (first 100 chars as sample)
        if element.text and element.text.strip():
            text_sample = element.text.strip()[:100]
            if text_sample not in self.element_texts[current_path]:
                self.element_texts[current_path].append(text_sample)
                # Limit to 3 samples per element
                if len(self.element_texts[current_path]) > 3:
                    self.element_texts[current_path] = self.element_texts[current_path][:3]

        # Recursively explore children
        for child in element:
            self._explore_element(child, parent=tag, path=current_path)

    def _build_report(self) -> Dict[str, Any]:
        """Build comprehensive structure report."""
        report = {
            "file_info": {
                "root_element": self.root_element,
                "total_unique_paths": len(self.element_counts),
                "total_elements": sum(self.element_counts.values()),
            },
            "namespaces": self.namespaces if self.namespaces else "No namespaces found",
            "element_hierarchy": self._build_hierarchy(),
            "element_details": self._build_element_details(),
            "statistics": self._build_statistics(),
        }
        return report

    def _build_hierarchy(self) -> Dict[str, Any]:
        """Build hierarchical structure representation."""
        hierarchy = {}

        # Sort paths by depth and name
        sorted_paths = sorted(self.element_counts.keys(), key=lambda x: (x.count("/"), x))

        for path in sorted_paths[:50]:  # Limit to first 50 for readability
            parts = path.split("/")
            current = hierarchy

            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {
                        "_count": self.element_counts["/".join(parts[: i + 1])],
                        "_children": {},
                    }
                current = current[part]["_children"]

        return hierarchy

    def _build_element_details(self) -> List[Dict[str, Any]]:
        """Build detailed information for each unique element."""
        details = []

        # Get top 30 most common elements
        sorted_elements = sorted(self.element_counts.items(), key=lambda x: x[1], reverse=True)[:30]

        for path, count in sorted_elements:
            element_name = path.split("/")[-1]
            detail = {
                "path": path,
                "element": element_name,
                "count": count,
                "attributes": list(self.element_attributes.get(path, [])),
                "sample_text": self.element_texts.get(path, []),
                "children": list(self.element_children.get(element_name, [])),
            }
            details.append(detail)

        return details

    def _build_statistics(self) -> Dict[str, Any]:
        """Build statistical summary."""
        depths = [path.count("/") + 1 for path in self.element_counts.keys()]

        stats = {
            "max_depth": max(depths) if depths else 0,
            "avg_depth": sum(depths) / len(depths) if depths else 0,
            "elements_with_text": len(self.element_texts),
            "elements_with_attributes": len(self.element_attributes),
            "unique_element_names": len(
                set(path.split("/")[-1] for path in self.element_counts.keys())
            ),
        }

        # Most common elements
        top_elements = sorted(self.element_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        stats["most_common_elements"] = [
            {"element": path.split("/")[-1], "path": path, "count": count}
            for path, count in top_elements
        ]

        return stats


def print_structure(structure: Dict[str, Any], indent: int = 0):
    """Pretty print the structure dictionary."""
    for key, value in structure.items():
        if isinstance(value, dict):
            print("  " * indent + f"{key}:")
            print_structure(value, indent + 1)
        elif isinstance(value, list):
            print("  " * indent + f"{key}:")
            for item in value[:5]:  # Limit list output
                if isinstance(item, dict):
                    print_structure(item, indent + 1)
                    print("  " * (indent + 1) + "---")
                else:
                    print("  " * (indent + 1) + f"- {item}")
        else:
            print("  " * indent + f"{key}: {value}")


def save_json_report(structure: Dict[str, Any], output_path: str):
    """Save structure report as JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2, default=str)
    print(f"\nJSON report saved to: {output_path}")


def main():
    """Main function to run XML explorer."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python explore_xml_structure.py <xml_file_path> [output_json_path]")
        print("\nExample:")
        print("  python explore_xml_structure.py transcript.xml")
        print("  python explore_xml_structure.py transcript.xml structure_report.json")
        sys.exit(1)

    xml_file = sys.argv[1]

    # Check if file exists
    if not os.path.exists(xml_file):
        print(f"Error: File '{xml_file}' not found")
        sys.exit(1)

    # Optional JSON output path
    json_output = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Analyzing XML structure of: {xml_file}")
    print("=" * 80)

    # Create explorer and analyze
    explorer = XMLStructureExplorer()
    structure = explorer.explore_xml(xml_file)

    # Check for errors
    if "error" in structure:
        print(f"Error: {structure['error']}")
        sys.exit(1)

    # Print file info
    print("\nFILE INFORMATION:")
    print("-" * 40)
    for key, value in structure["file_info"].items():
        print(f"{key}: {value}")

    # Print namespaces
    print("\nNAMESPACES:")
    print("-" * 40)
    if isinstance(structure["namespaces"], dict):
        for prefix, uri in structure["namespaces"].items():
            print(f"{prefix}: {uri}")
    else:
        print(structure["namespaces"])

    # Print hierarchy (simplified)
    print("\nELEMENT HIERARCHY (Top Level):")
    print("-" * 40)
    if structure["element_hierarchy"]:
        for element, info in list(structure["element_hierarchy"].items())[:10]:
            if isinstance(info, dict):
                count = info.get("_count", 0)
                children = list(info.get("_children", {}).keys())
                print(f"<{element}> (count: {count})")
                if children:
                    print(f"  └─ children: {', '.join(children[:5])}")

    # Print detailed elements
    print("\nTOP ELEMENTS BY FREQUENCY:")
    print("-" * 40)
    for detail in structure["element_details"][:15]:
        print(f"\n{detail['path']} (count: {detail['count']})")

        if detail["attributes"]:
            print(f"  Attributes: {', '.join(detail['attributes'][:3])}")

        if detail["sample_text"]:
            print(f"  Sample text: \"{detail['sample_text'][0][:60]}...\"")

        if detail["children"]:
            print(f"  Children: {', '.join(detail['children'][:5])}")

    # Print statistics
    print("\nSTATISTICS:")
    print("-" * 40)
    stats = structure["statistics"]
    print(f"Maximum depth: {stats['max_depth']}")
    print(f"Average depth: {stats['avg_depth']:.2f}")
    print(f"Elements with text content: {stats['elements_with_text']}")
    print(f"Elements with attributes: {stats['elements_with_attributes']}")
    print(f"Unique element names: {stats['unique_element_names']}")

    print("\nMost common elements:")
    for item in stats["most_common_elements"][:10]:
        print(f"  {item['element']:<20} {item['count']:>5} occurrences")

    # Save JSON if requested
    if json_output:
        save_json_report(structure, json_output)

    print("\n" + "=" * 80)
    print("Analysis complete!")


if __name__ == "__main__":
    main()
