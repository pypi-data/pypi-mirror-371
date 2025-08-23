"""
Binary manager for FootsiesGym - handles automatic binary downloads.
"""

import urllib.request
import urllib.error
import fcntl
from pathlib import Path
from typing import Optional


class BinaryManager:
    """Manages automatic downloading and caching of FootsiesGym binaries."""
    
    # Direct download URLs for binary files
    # Using GitHub raw files as the primary source
    DOWNLOAD_BASE_URL = "https://github.com/chasemcd/FootsiesGym/raw/main/binaries"
    
    # Fallback URLs in case primary fails
    FALLBACK_URLS = [
        "https://raw.githubusercontent.com/chasemcd/FootsiesGym/main/binaries",
    ]
    
    BINARY_FILES = {
        "footsies_linux_server_021725.zip": "footsies_linux_server_021725.zip",
        "footsies_linux_windowed_021725.zip": "footsies_linux_windowed_021725.zip", 
        "footsies_mac_headless_5709b6d.zip": "footsies_mac_headless_5709b6d.zip",
        "footsies_mac_windowed_5709b6d.zip": "footsies_mac_windowed_5709b6d.zip",
    }
    
    def __init__(self):
        self.package_dir = Path(__file__).parent
        self.binaries_dir = self.package_dir / "binaries"
        self.binaries_dir.mkdir(exist_ok=True)
    
    def ensure_binaries_available(self, platform: str = "linux") -> bool:
        """
        Ensure the required binaries are available for the given platform.
        Downloads them automatically if they don't exist locally.
        Uses file locking to prevent race conditions when multiple processes
        try to download simultaneously.
        
        Args:
            platform: Target platform ("linux" or "mac")
            
        Returns:
            bool: True if binaries are available, False otherwise
        """
        required_files = self._get_required_files(platform)
        
        # Check if all required files exist
        missing_files = []
        for filename in required_files:
            file_path = self.binaries_dir / filename
            if not file_path.exists():
                missing_files.append(filename)
        
        if not missing_files:
            print(f"✅ All {platform} binaries are available")
            return True
        
        # Use file locking to prevent multiple processes from downloading simultaneously
        lock_file = self.binaries_dir / ".download_lock"
        
        try:
            # Create lock file and acquire exclusive lock
            with open(lock_file, 'w') as lock_fd:
                print(f"🔒 Acquiring download lock for {platform} binaries...")
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
                
                # Re-check if files exist after acquiring lock (another process might have downloaded them)
                missing_files = []
                for filename in required_files:
                    file_path = self.binaries_dir / filename
                    if not file_path.exists():
                        missing_files.append(filename)
                
                if not missing_files:
                    print(f"✅ All {platform} binaries are now available (downloaded by another process)")
                    return True
                
                print(f"📥 Downloading missing {platform} binaries: {missing_files}")
                
                # Download missing files
                success = True
                for filename in missing_files:
                    if not self._download_binary(filename):
                        success = False
                
                print(f"🔓 Releasing download lock for {platform} binaries")
                return success
                
        except Exception as e:
            print(f"❌ Error during binary download: {e}")
            return False
        finally:
            # Clean up lock file
            try:
                if lock_file.exists():
                    lock_file.unlink()
            except:
                pass  # Ignore cleanup errors
    
    def _get_required_files(self, platform: str) -> list[str]:
        """Get the list of required binary files for a platform."""
        if platform.lower() == "linux":
            return [
                "footsies_linux_server_021725.zip",
                "footsies_linux_windowed_021725.zip"
            ]
        elif platform.lower() == "mac":
            return [
                "footsies_mac_headless_5709b6d.zip", 
                "footsies_mac_windowed_5709b6d.zip"
            ]
        else:
            return []
    
    def _download_binary(self, filename: str) -> bool:
        """
        Get a binary file by copying from local repository or downloading from HTTP.
        
        Args:
            filename: Name of the file to download
            
        Returns:
            bool: True if successful, False otherwise
        """
        local_path = self.binaries_dir / filename
        
        # First, try to find the file in the local repository
        # Look for it in the parent directory structure
        repo_binaries_path = self.package_dir.parent / "footsiesgym" / "binaries" / filename
        
        if repo_binaries_path.exists():
            try:
                print(f"  Copying {filename} from local repository...")
                import shutil
                shutil.copy2(repo_binaries_path, local_path)
                print(f"  ✅ Copied {filename} ({local_path.stat().st_size} bytes)")
                return True
            except Exception as e:
                print(f"  ❌ Failed to copy from local repository: {e}")
        
        # If local copy fails, try HTTP download as fallback
        urls_to_try = [self.DOWNLOAD_BASE_URL] + self.FALLBACK_URLS
        
        for base_url in urls_to_try:
            url = f"{base_url}/{filename}"
            
            try:
                print(f"  Downloading {filename} from {base_url}...")
                
                # Create request with user agent to avoid blocking
                request = urllib.request.Request(url)
                request.add_header('User-Agent', 'FootsiesGym/0.1.0')
                
                with urllib.request.urlopen(request, timeout=30) as response:
                    # Check if we got a valid response
                    if response.status == 200:
                        with open(local_path, 'wb') as f:
                            # Download in chunks to handle large files
                            while True:
                                chunk = response.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                        
                        print(f"  ✅ Downloaded {filename} ({local_path.stat().st_size} bytes)")
                        return True
                    else:
                        print(f"  ❌ HTTP {response.status} from {base_url}")
                        continue
                        
            except urllib.error.HTTPError as e:
                print(f"  ❌ HTTP error {e.code} from {base_url}: {e.reason}")
                continue
            except urllib.error.URLError as e:
                print(f"  ❌ URL error from {base_url}: {e.reason}")
                continue
            except Exception as e:
                print(f"  ❌ Unexpected error from {base_url}: {e}")
                continue
        
        print(f"  ❌ Failed to get {filename} from all sources")
        return False
    

    
    def get_binary_path(self, platform: str = "linux", windowed: bool = False) -> Optional[Path]:
        """
        Get the path to the appropriate binary file.
        
        Args:
            platform: Target platform ("linux" or "mac")
            windowed: Whether to get windowed version (True) or headless (False)
            
        Returns:
            Path to the binary file, or None if not available
        """
        if platform.lower() == "linux":
            filename = "footsies_linux_windowed_021725.zip" if windowed else "footsies_linux_server_021725.zip"
        elif platform.lower() == "mac":
            filename = "footsies_mac_windowed_5709b6d.zip" if windowed else "footsies_mac_headless_5709b6d.zip"
        else:
            return None
        
        binary_path = self.binaries_dir / filename
        return binary_path if binary_path.exists() else None


# Global instance
_binary_manager = None

def get_binary_manager() -> BinaryManager:
    """Get the global binary manager instance."""
    global _binary_manager
    if _binary_manager is None:
        _binary_manager = BinaryManager()
    return _binary_manager
