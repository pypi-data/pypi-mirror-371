"""Dataclass representations for mmCIF data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Atom:
    """
    Represents a single atom from an mmCIF file.
    
    Provides typed access to all atom properties with dot notation:
        atom.x, atom.y, atom.z, atom.label_atom_id, etc.
    """
    
    # Record type
    type: str
    
    # Atom identifiers
    id: int
    type_symbol: str
    label_atom_id: str
    label_comp_id: str
    label_asym_id: str
    label_entity_id: int
    label_seq_id: int
    
    # 3D coordinates
    Cartn_x: float
    Cartn_y: float
    Cartn_z: float
    
    # Convenience aliases for coordinates
    x: float = field(init=False)
    y: float = field(init=False)
    z: float = field(init=False)
    
    # Crystallographic properties
    occupancy: float
    B_iso_or_equiv: float
    
    # Optional fields that may be present
    pdbx_PDB_ins_code: str | None = None
    pdbx_formal_charge: int | None = None
    auth_seq_id: int | None = None
    auth_comp_id: str | None = None
    auth_asym_id: str | None = None
    auth_atom_id: str | None = None
    pdbx_PDB_model_num: int | None = None
    
    def __post_init__(self):
        """Set coordinate aliases after initialization."""
        self.x = self.Cartn_x
        self.y = self.Cartn_y
        self.z = self.Cartn_z
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Atom:
        """
        Create an Atom instance from a dictionary.
        
        Args:
            data: Dictionary containing atom data
            
        Returns:
            Atom instance with populated fields
        """
        # Filter to only known fields that are present
        known_fields = {f.name for f in cls.__dataclass_fields__.values() if f.init}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Atom back to a dictionary.
        
        Returns:
            Dictionary representation of the atom
        """
        # Start with required fields
        result = {
            'type': self.type,
            'id': self.id,
            'type_symbol': self.type_symbol,
            'label_atom_id': self.label_atom_id,
            'label_comp_id': self.label_comp_id,
            'label_asym_id': self.label_asym_id,
            'label_entity_id': self.label_entity_id,
            'label_seq_id': self.label_seq_id,
            'Cartn_x': self.Cartn_x,
            'Cartn_y': self.Cartn_y,
            'Cartn_z': self.Cartn_z,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'occupancy': self.occupancy,
            'B_iso_or_equiv': self.B_iso_or_equiv,
        }
        
        # Add optional fields if present and not None
        optional_fields = [
            'pdbx_PDB_ins_code', 'pdbx_formal_charge', 'auth_seq_id',
            'auth_comp_id', 'auth_asym_id', 'auth_atom_id', 'pdbx_PDB_model_num'
        ]
        
        for field_name in optional_fields:
            value = getattr(self, field_name, None)
            if value is not None:
                result[field_name] = value
        
        return result
    
    @property
    def position(self) -> tuple[float, float, float]:
        """Get the 3D position as a tuple."""
        return (self.x, self.y, self.z)


@dataclass
class MmcifData:
    """
    Represents parsed mmCIF data with typed atom access.
    
    Provides convenient access patterns:
        data.atoms[0].x
        data.atoms[0].label_atom_id
        data.atom_count
    """
    
    atoms: list[Atom]
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MmcifData:
        """
        Create an MmcifData instance from a dictionary.
        
        Args:
            data: Dictionary containing 'atoms' key with list of atom dicts
            
        Returns:
            MmcifData instance with Atom objects
        """
        atoms = [Atom.from_dict(atom_dict) for atom_dict in data.get('atoms', [])]
        return cls(atoms=atoms)
    
    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """
        Convert back to dictionary format.
        
        Returns:
            Dictionary with 'atoms' key containing list of atom dicts
        """
        return {'atoms': [atom.to_dict() for atom in self.atoms]}
    
    @property
    def atom_count(self) -> int:
        """Get the total number of atoms."""
        return len(self.atoms)
    
    @property
    def positions(self) -> list[tuple[float, float, float]]:
        """Get all atom positions as a list of tuples."""
        return [atom.position for atom in self.atoms]
    
    @property
    def chains(self) -> set[str]:
        """Get unique chain identifiers."""
        return {atom.label_asym_id for atom in self.atoms}
    
    @property
    def residues(self) -> set[tuple[str, int]]:
        """Get unique residues as (chain_id, seq_id) tuples."""
        return {(atom.label_asym_id, atom.label_seq_id) for atom in self.atoms}
    
    def get_chain(self, chain_id: str) -> list[Atom]:
        """Get all atoms from a specific chain."""
        return [atom for atom in self.atoms if atom.label_asym_id == chain_id]
    
    def get_residue(self, chain_id: str, seq_id: int) -> list[Atom]:
        """Get all atoms from a specific residue."""
        return [
            atom for atom in self.atoms 
            if atom.label_asym_id == chain_id and atom.label_seq_id == seq_id
        ]


def dict_to_dataclass(data: dict | list) -> MmcifData | list[MmcifData] | dict[str, MmcifData]:
    """
    Convert dictionary results to dataclass format.
    
    Args:
        data: Single dict, list of dicts, or dict of dicts from parse functions
        
    Returns:
        Corresponding dataclass structure
    """
    if isinstance(data, dict):
        # Check if it's a single result or a mapping of file paths to results
        if 'atoms' in data:
            # Single result
            return MmcifData.from_dict(data)
        else:
            # Dictionary mapping paths to results
            return {path: MmcifData.from_dict(result) for path, result in data.items()}
    elif isinstance(data, list):
        # List of results from batch processing
        return [MmcifData.from_dict(result) for result in data]
    else:
        raise TypeError(f"Unexpected data type: {type(data)}")


def dataclass_to_dict(data: MmcifData | list[MmcifData] | dict[str, MmcifData]) -> dict | list | dict[str, dict]:
    """
    Convert dataclass results back to dictionary format.
    
    Args:
        data: Single MmcifData, list of MmcifData, or dict of MmcifData
        
    Returns:
        Corresponding dictionary structure
    """
    if isinstance(data, MmcifData):
        return data.to_dict()
    elif isinstance(data, list):
        return [item.to_dict() for item in data]
    elif isinstance(data, dict):
        return {path: result.to_dict() for path, result in data.items()}
    else:
        raise TypeError(f"Unexpected data type: {type(data)}")