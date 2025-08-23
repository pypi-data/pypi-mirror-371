"""Protein structure visualization using asciimol and ASE."""

from typing import Any, Dict, List, Optional, Tuple
import io
import tempfile
import os
import subprocess
from pathlib import Path

import numpy as np
from ase.io import read as ase_read
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

import asciimol
from asciimol.app.renderer import Renderer


class ProteinVisualizer:
    """Visualize protein structures using asciimol."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize the protein visualizer.
        
        Args:
            console: Rich console for rendering
        """
        self.console = console or Console()
        self._config = {
            'width': 80,
            'height': 30,
            'color': True,
            'auto_rotate': True,
            'auto_rotate_speed': 0.1,
        }
        self._renderer = None
        self._atoms = None
        self._temp_files = []

    def cleanup(self):
        """Clean up temporary files."""
        for path in self._temp_files:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception:
                pass
        self._temp_files = []

    def _pdb_to_xyz(self, pdb_content: str) -> str:
        """Convert PDB content to XYZ format using ASE.
        
        Args:
            pdb_content: PDB file content as string
            
        Returns:
            XYZ format content
        """
        # Create a temporary file for the PDB content
        with tempfile.NamedTemporaryFile(suffix='.pdb', delete=False) as f:
            f.write(pdb_content.encode('utf-8'))
            pdb_path = f.name
            self._temp_files.append(pdb_path)
        
        # Read the PDB file using ASE
        try:
            atoms = ase_read(pdb_path, format='proteindatabank')
            
            # Create a temporary file for the XYZ content
            xyz_path = pdb_path + '.xyz'
            self._temp_files.append(xyz_path)
            
            # Write the atoms to XYZ format
            atoms.write(xyz_path, format='xyz')
            
            # Read the XYZ file
            with open(xyz_path, 'r') as f:
                xyz_content = f.read()
                
            return xyz_content
        except Exception as e:
            raise ValueError(f"Failed to convert PDB to XYZ: {e}")

    def render_pdb_as_text(self, pdb_content: str, width: int = 80, height: int = 30) -> str:
        """Render a PDB file as text using asciimol.
        
        Args:
            pdb_content: PDB file content as string
            width: Width of the rendering
            height: Height of the rendering
            
        Returns:
            ASCII art representation of the protein
        """
        try:
            # Convert PDB to XYZ
            xyz_content = self._pdb_to_xyz(pdb_content)
            
            # Create a temporary file for the XYZ content
            with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
                f.write(xyz_content.encode('utf-8'))
                xyz_path = f.name
                self._temp_files.append(xyz_path)
            
            # Use asciimol to render the XYZ file
            result = subprocess.run(
                ['python', '-m', 'asciimol', xyz_path, '--no-interactive', '--width', str(width), '--height', str(height)],
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error rendering protein: {e.stderr}"
        except Exception as e:
            return f"Error rendering protein: {e}"
        finally:
            self.cleanup()

    def get_rich_panel(self, pdb_content: str, title: str = "Protein Structure") -> Panel:
        """Get a Rich panel with the protein visualization.
        
        Args:
            pdb_content: PDB file content as string
            title: Title for the panel
            
        Returns:
            Rich Panel with protein visualization
        """
        text = self.render_pdb_as_text(pdb_content)
        return Panel(Text(text), title=title, border_style="green")


def is_available() -> bool:
    """Check if protein visualization is available."""
    # Since asciimol and ASE are now core dependencies, this should always return True
    # This function is kept for backward compatibility
    return True


def render_protein(pdb_content: str, width: int = 80, height: int = 30) -> str:
    """Render a protein structure as text.
    
    Args:
        pdb_content: PDB file content as string
        width: Width of the rendering
        height: Height of the rendering
        
    Returns:
        Text representation of the protein
    """
    visualizer = ProteinVisualizer()
    return visualizer.render_pdb_as_text(pdb_content, width, height)
