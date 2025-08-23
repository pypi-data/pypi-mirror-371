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
            # asciimol doesn't support command-line options for width/height, 
            # so we'll use it directly through its API instead
            try:
                # Import needed modules
                from asciimol.app.io import read_xyz_block
                from asciimol.app.renderer import Renderer
                
                # Read the XYZ file content
                with open(xyz_path, 'r') as f:
                    xyz_lines = f.readlines()
                
                # Parse the XYZ content
                counts, positions, symbols = read_xyz_block(xyz_lines)
                
                # Create a renderer with the specified dimensions
                config = {"width": width, "height": height, "color": True}
                renderer = Renderer(height, width, config)
                
                # Set up the scene
                renderer.coordinates = positions
                renderer.symbols = symbols
                renderer.counts = counts
                renderer.refresh_coordinates()
                
                # Render a frame
                renderer.clear()
                renderer.buffer_scene()
                
                # Get the rendered text
                result_text = "\n".join("".join(row) for row in renderer.buffer)
                
                # Create a mock result object
                class MockResult:
                    def __init__(self, stdout):
                        self.stdout = stdout
                
                result = MockResult(result_text)
            except Exception as e:
                # Fall back to basic command-line approach
                result = subprocess.run(
                    ['python', '-m', 'asciimol', xyz_path],
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

    # --- FlatProt Integration (optional 2D SVG rendering) ---
    def render_flatprot_svg(self, structure_content: str, filename_hint: str = "protein.cif", output_format: str = "svg", auto_open: bool = False, viewer_command: str = "") -> Tuple[bool, str, Optional[str]]:
        """Attempt to render a 2D SVG using FlatProt CLI.
        
        Returns (ok, message, output_path). If ok is True, output_path is the SVG file path.
        
        Notes:
        - Expects AlphaFold mmCIF content (preferred) or DSSP-annotated mmCIF/PDB.
        - Requires FlatProt available via 'uvx flatprot' or 'flatprot' on PATH.
        - DSSP (mkdssp) is needed for non-AlphaFold inputs.
        """
        import shutil
        import tempfile
        # Detect runner: prefer uvx if present, else flatprot
        runner = None
        if shutil.which("uvx"):
            runner = ["uvx", "flatprot"]
        elif shutil.which("flatprot"):
            runner = ["flatprot"]
        else:
            return (False, "FlatProt not found. Install with 'uv tool add FlatProt' or install flatprot globally.", None)

        # Write temp input file with appropriate extension
        suffix = ".cif" if filename_hint.lower().endswith(".cif") else ".pdb"
        tmp_in = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp_in.write(structure_content.encode("utf-8", errors="ignore"))
        tmp_in.flush()
        tmp_in.close()
        # Determine output format
        fmt = (output_format or "svg").lower()
        if fmt not in ("svg", "png"):
            fmt = "svg"
        out_path = tmp_in.name + f".{fmt}"
        # Track for cleanup
        try:
            self._temp_files.append(tmp_in.name)
            self._temp_files.append(out_path)
        except Exception:
            pass

        # Fast-fail if PDB input but DSSP missing (prevents long hangs)
        try:
            if suffix == ".pdb":
                import shutil as _sh
                if not _sh.which("mkdssp"):
                    return (False, "DSSP (mkdssp) is required for PDB inputs. Install with 'brew install brewsci/bio/dssp' or use AlphaFold mmCIF.", None)
        except Exception:
            pass

        # Invoke FlatProt with timeout
        try:
            try:
                proc = subprocess.run(
                    runner + ["project", tmp_in.name, "--output", out_path],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=20.0,
                )
            except subprocess.TimeoutExpired:
                return (False, "FlatProt timed out (20s). Try again later, ensure dependencies are installed, or use ASCII view.", None)
            if proc.returncode != 0:
                # Provide helpful hints for DSSP requirement
                hint = ""
                if suffix == ".pdb" and "DSSP" in (proc.stderr or "") + (proc.stdout or ""):
                    hint = "\nDSSP is required for PDB inputs. Install with 'brew install brewsci/bio/dssp' and preprocess."
                msg = f"FlatProt failed (exit {proc.returncode}). {proc.stderr.strip() or proc.stdout.strip()}{hint}"
                return (False, msg, None)
            if not os.path.exists(out_path):
                return (False, f"FlatProt did not produce output {fmt.upper()}.", None)
            # Optionally open
            try:
                if auto_open:
                    if viewer_command:
                        subprocess.Popen([viewer_command, out_path])
                    else:
                        if sys.platform == "darwin":
                            subprocess.Popen(["open", out_path])
                        elif os.name == "nt":
                            os.startfile(out_path)  # type: ignore[attr-defined]
                        else:
                            subprocess.Popen(["xdg-open", out_path])
            except Exception:
                pass
            return (True, f"FlatProt {fmt.upper()} created: {out_path}", out_path)
        except Exception as e:
            return (False, f"FlatProt invocation error: {e}", None)


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
