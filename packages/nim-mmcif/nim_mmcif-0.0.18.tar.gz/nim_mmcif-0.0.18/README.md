# nim-mmcif

Fast mmCIF (Macromolecular Crystallographic Information File) parser written in Nim with Python bindings

The goal of this repository is to experiment with vibe coding while building something useful for bioinformatics community, to see how much of a cross platform library can be driven to completion by transformers

## Features

- 🚀 High-performance parsing of mmCIF files using Nim
- 🌍 Cross-platform support (Linux, macOS, Windows)
- 📦 Easy installation via pip

## Installation

### Prerequisites

- Python 3.8 or higher
- Nim compiler (see [platform-specific instructions](CROSS_PLATFORM.md))

### From PyPI

```bash
pip install nim-mmcif
```

### From Source

```bash
# Install Nim (platform-specific, see below)
# macOS: brew install nim
# Linux: curl https://nim-lang.org/choosenim/init.sh -sSf | sh
# Windows: scoop install nim

# Install the package
git clone https://github.com/lucidrains/nim-mmcif
cd nim-mmcif
pip install -e .
```

For detailed platform-specific instructions, see [CROSS_PLATFORM.md](CROSS_PLATFORM.md).

## Quick Start

### Python Usage

#### Dictionary Access

```python
import nim_mmcif

# Parse an mmCIF file (returns dict by default)
data = nim_mmcif.parse_mmcif("path/to/file.mmcif")
print(f"Found {len(data['atoms'])} atoms")

# Access atom properties using dictionary notation
first_atom = data['atoms'][0]
print(f"Atom {first_atom['id']}: {first_atom['label_atom_id']}")
print(f"Position: ({first_atom['x']}, {first_atom['y']}, {first_atom['z']})")

# Parse multiple files using glob patterns
results = nim_mmcif.parse_mmcif("path/to/*.mmcif")
for filepath, data in results.items():
    print(f"{filepath}: {len(data['atoms'])} atoms")
```

#### Dataclass Access

```python
import nim_mmcif

# Parse with dataclass support for cleaner dot notation access
data = nim_mmcif.parse_mmcif("path/to/file.mmcif", as_dataclass=True)
print(f"Found {data.atom_count} atoms")

# Access atom properties using dot notation
first_atom = data.atoms[0]
print(f"Atom {first_atom.id}: {first_atom.label_atom_id}")
print(f"Position: ({first_atom.x}, {first_atom.y}, {first_atom.z})")
print(f"Chain: {first_atom.label_asym_id}, Residue: {first_atom.label_comp_id}")

# Use convenience properties and methods
print(f"Unique chains: {data.chains}")
print(f"Number of residues: {len(data.residues)}")

# Get all atoms from a specific chain
chain_a_atoms = data.get_chain('A')

# Get all atoms from a specific residue
residue_atoms = data.get_residue('A', 1)

# Get all positions as tuples
positions = data.positions  # List of (x, y, z) tuples

# Batch processing with dataclasses
results = nim_mmcif.parse_mmcif_batch(["file1.mmcif", "file2.mmcif"], as_dataclass=True)
for result in results:
    print(f"Structure has {result.atom_count} atoms in {len(result.chains)} chain(s)")
```

#### Other Functions

```python
# Get atom count directly
count = nim_mmcif.get_atom_count("path/to/file.mmcif")
print(f"File contains {count} atoms")

# Get all atoms with their properties (returns list of dicts)
atoms = nim_mmcif.get_atoms("path/to/file.mmcif")
for atom in atoms[:5]:  # Print first 5 atoms
    print(f"Atom {atom['id']}: {atom['label_atom_id']} at ({atom['x']}, {atom['y']}, {atom['z']})")

# Get just the 3D coordinates
positions = nim_mmcif.get_atom_positions("path/to/file.mmcif")
for i, (x, y, z) in enumerate(positions[:5]):
    print(f"Position {i}: ({x:.3f}, {y:.3f}, {z:.3f})")
```

### Nim Usage

```nim
import nim_mmcif/mmcif

# Parse an mmCIF file
let data = mmcif_parse("path/to/file.mmcif")
echo "Found ", data.atoms.len, " atoms"

# Iterate through atoms
for atom in data.atoms[0..<min(5, data.atoms.len)]:
  echo "Atom ", atom.id, ": ", atom.label_atom_id, 
       " at (", atom.Cartn_x, ", ", atom.Cartn_y, ", ", atom.Cartn_z, ")"

# Access specific atom properties
if data.atoms.len > 0:
  let firstAtom = data.atoms[0]
  echo "Chain: ", firstAtom.label_asym_id
  echo "Residue: ", firstAtom.label_comp_id
  echo "B-factor: ", firstAtom.B_iso_or_equiv
```

### Batch Processing

Process multiple mmCIF files efficiently in a single operation:

```python
import nim_mmcif

# List of mmCIF files to process
files = [
    "path/to/structure1.mmcif",
    "path/to/structure2.mmcif",
    "path/to/structure3.mmcif"
]

# Parse all files in batch (returns list when no globs used)
results = nim_mmcif.parse_mmcif_batch(files)

# Process results
for i, data in enumerate(results):
    print(f"Structure {i+1}: {len(data['atoms'])} atoms")
    
    # Analyze each structure
    atoms = data['atoms']
    if atoms:
        # Get unique chain IDs
        chains = set(atom['label_asym_id'] for atom in atoms)
        print(f"  Chains: {', '.join(sorted(chains))}")
        
        # Count residues
        residues = set((atom['label_asym_id'], atom['label_seq_id']) 
                      for atom in atoms)
        print(f"  Residues: {len(residues)}")

# Batch processing with glob patterns (returns dict)
results = nim_mmcif.parse_mmcif_batch("path/to/*.mmcif")
for filepath, data in results.items():
    print(f"{filepath}: {len(data['atoms'])} atoms")

# Mix of glob patterns and regular paths (returns dict)
results = nim_mmcif.parse_mmcif_batch([
    "specific_file.mmcif",
    "structures/*.mmcif",
    "models/model_?.mmcif"
])
for filepath, data in results.items():
    print(f"{filepath}: {len(data['atoms'])} atoms")
```

Batch processing is particularly useful when:
- Analyzing multiple protein structures for comparative studies
- Processing entire datasets of crystallographic structures
- Building machine learning datasets from PDB files
- Performing high-throughput structural analysis

The batch function provides better performance than individual parsing when processing multiple files, as it reduces the overhead of repeated function calls.

## API Reference

### Functions

#### `parse_mmcif(filepath: str, as_dataclass: bool = False) -> dict | MmcifData | dict[str, dict] | dict[str, MmcifData]`
Parse an mmCIF file or files matching a glob pattern.
- **filepath**: Path to mmCIF file or glob pattern
- **as_dataclass**: If True, returns MmcifData dataclass(es) with dot notation access
- **Returns**:
  - Single file + dict: Dictionary with 'atoms' key
  - Single file + dataclass: MmcifData instance
  - Glob pattern + dict: Dictionary mapping file paths to parsed data
  - Glob pattern + dataclass: Dictionary mapping file paths to MmcifData instances
- Supports wildcards: `*` (any characters), `?` (single character), `**` (recursive)

#### `parse_mmcif_batch(filepaths: list[str] | str, as_dataclass: bool = False) -> list[dict] | list[MmcifData] | dict[str, dict] | dict[str, MmcifData]`
Parse multiple mmCIF files in a single operation.
- **filepaths**: List of paths, single path, or glob pattern
- **as_dataclass**: If True, returns MmcifData dataclass(es) with dot notation access
- **Returns**:
  - No glob + dict: List of dictionaries with parsed data
  - No glob + dataclass: List of MmcifData instances
  - With glob + dict: Dictionary mapping file paths to parsed data
  - With glob + dataclass: Dictionary mapping file paths to MmcifData instances
- More efficient than parsing files individually when processing multiple structures

#### `get_atom_count(filepath: str) -> int`
Get the number of atoms in an mmCIF file.

#### `get_atoms(filepath: str) -> list[dict]`
Get all atoms from an mmCIF file as a list of dictionaries.

#### `get_atom_positions(filepath: str) -> list[tuple[float, float, float]]`
Get 3D coordinates of all atoms as a list of (x, y, z) tuples.

### Dataclasses

#### `MmcifData`
Container for parsed mmCIF data with typed atom access.

**Properties:**
- `atoms`: List of Atom objects
- `atom_count`: Total number of atoms
- `positions`: List of (x, y, z) tuples for all atoms
- `chains`: Set of unique chain identifiers
- `residues`: Set of unique (chain_id, seq_id) tuples

**Methods:**
- `get_chain(chain_id: str)`: Get all atoms from a specific chain
- `get_residue(chain_id: str, seq_id: int)`: Get all atoms from a specific residue
- `to_dict()`: Convert back to dictionary format

#### `Atom`
Represents a single atom with typed properties accessible via dot notation.

**Properties:**
- `type`: Record type (ATOM or HETATM)
- `id`: Atom serial number
- `type_symbol`: Element symbol
- `label_atom_id`: Atom name
- `label_comp_id`: Residue name
- `label_asym_id`: Chain identifier
- `label_entity_id`: Entity ID
- `label_seq_id`: Residue sequence number
- `Cartn_x`, `Cartn_y`, `Cartn_z`: 3D coordinates
- `x`, `y`, `z`: Convenient aliases for coordinates
- `occupancy`: Occupancy factor
- `B_iso_or_equiv`: B-factor (temperature factor)
- `position`: Tuple of (x, y, z) coordinates

**Methods:**
- `to_dict()`: Convert back to dictionary format

### Dictionary Format

When using the default dictionary format (as_dataclass=False), each atom dictionary contains:
- `type`: Record type (ATOM or HETATM)
- `id`: Atom serial number
- `label_atom_id`: Atom name
- `label_comp_id`: Residue name
- `label_asym_id`: Chain identifier
- `label_seq_id`: Residue sequence number
- `x`, `y`, `z`: 3D coordinates (aliases for Cartn_x, Cartn_y, Cartn_z)
- `occupancy`: Occupancy factor
- `B_iso_or_equiv`: B-factor
- And more...

## Platform Support

| Platform | Architecture | Python | Status |
|----------|-------------|--------|--------|
| Linux    | x64, ARM64  | 3.8-3.12 | ✅ |
| macOS    | x64, ARM64  | 3.8-3.12 | ✅ |
| Windows  | x64         | 3.8-3.12 | ✅ |

## Building from Source

### Automatic Build

```bash
python build_nim.py
```

### Manual Build

```bash
# Build using nimble tasks
nimble build         # Build debug version
nimble buildRelease  # Build optimized release version
```

## Development

### Running Tests

```bash
pip install pytest
pytest tests/ -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Documentation

- [Cross-Platform Guide](CROSS_PLATFORM.md) - Platform-specific build instructions

## Performance

The Nim implementation provides significant performance improvements over pure Python parsers, especially for large mmCIF files commonly used in structural biology.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Nim](https://nim-lang.org/) for high performance
- Python integration via [nimporter](https://github.com/Pebaz/nimporter) and [nimpy](https://github.com/yglukhov/nimpy)
- mmCIF format specification from [wwPDB](https://www.wwpdb.org/)
