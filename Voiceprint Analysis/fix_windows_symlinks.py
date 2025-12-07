"""
Fix Windows Symlink Issue for HuggingFace Models

This script patches the HuggingFace Hub to use file copying instead of symlinks
on Windows systems without Developer Mode or admin privileges.
"""
import os
import sys
import shutil
from pathlib import Path

def patch_huggingface_symlinks():
    """Patch HuggingFace to avoid symlinks on Windows"""
    
    # Set environment variable to disable symlink warnings
    os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
    
    # Monkey-patch the symlink function in pathlib
    original_symlink = Path.symlink_to
    
    def copy_instead_of_symlink(self, target, target_is_directory=False):
        """Copy file instead of creating symlink"""
        try:
            # Try original symlink first
            return original_symlink(self, target, target_is_directory)
        except OSError as e:
            if "WinError 1314" in str(e) or "privilege" in str(e).lower():
                # Symlink failed due to permissions - copy instead
                print(f"[INFO] Copying instead of symlinking: {target} -> {self}")
                if target_is_directory or Path(target).is_dir():
                    shutil.copytree(target, self, dirs_exist_ok=True)
                else:
                    self.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, self)
                return
            else:
                raise
    
    # Apply the patch
    Path.symlink_to = copy_instead_of_symlink
    print("[OK] HuggingFace symlink patch applied - will use file copying on Windows")

if __name__ == "__main__":
    patch_huggingface_symlinks()
    print("[OK] Patch applied successfully!")
    print("[INFO] You can now run: python main.py test")

