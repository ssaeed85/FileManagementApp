"""
Streamlit application for file name management.
"""
import streamlit as st
import os  # Keep for os.startfile (Windows-specific)
from pathlib import Path
from file_cleaner import FileNameCleaner
from duplicate_finder import DuplicateFinder
from help_content import (
    DUPLICATE_FINDER_HOW_TO,
    DUPLICATE_FINDER_HOW_IT_WORKS,
    FILE_CLEANER_HOW_TO,
    FILE_CLEANER_DATE_FORMATS
)


def get_drives():
    """Get available drives on Windows."""
    drives = []
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        drive = f"{letter}:\\"
        if Path(drive).exists():
            drives.append(drive)
    return drives


def get_subdirectories(path):
    """Get list of subdirectories in the given path."""
    try:
        items = []
        path_obj = Path(path)
        for item in sorted(path_obj.iterdir()):
            if item.is_dir():
                items.append(item.name)
        return items
    except (PermissionError, OSError):
        return []


def get_container_drive_mounts():
    """Return mounted drive paths exposed under /mnt inside container."""
    mounts = []
    mount_root = Path('/mnt')
    if not mount_root.exists() or not mount_root.is_dir():
        return mounts

    for mount_dir in sorted(mount_root.iterdir()):
        if mount_dir.is_dir():
            drive_name = mount_dir.name.upper()
            mounts.append((f"{drive_name}:\\", str(mount_dir)))

    return mounts


def directory_explorer():
    """Display a directory explorer interface."""
    st.sidebar.header("📂 Directory Explorer")

    # Use platform-appropriate default root.
    container_mounts = get_container_drive_mounts() if os.name != 'nt' else []
    if os.name == 'nt':
        default_start_path = Path.home()
    elif container_mounts:
        default_start_path = Path(container_mounts[0][1])
    else:
        default_start_path = Path('/')
    
    # Initialize session state
    if 'current_path' not in st.session_state:
        st.session_state.current_path = str(default_start_path)
    if 'nav_history' not in st.session_state:
        st.session_state.nav_history = [st.session_state.current_path]
    if 'nav_position' not in st.session_state:
        st.session_state.nav_position = 0
    
    # Drive selection (Windows only)
    drives = get_drives()
    if drives and os.name == 'nt':
        current_drive = st.session_state.current_path.split("\\")[0] + "\\"
        selected_drive = st.sidebar.selectbox(
            "Drive:",
            drives,
            index=drives.index(current_drive) if current_drive in drives else 0
        )
        
        # If drive changed, update path
        if not st.session_state.current_path.startswith(selected_drive):
            # Add to history
            st.session_state.nav_history = st.session_state.nav_history[:st.session_state.nav_position + 1]
            st.session_state.nav_history.append(selected_drive)
            st.session_state.nav_position += 1
            st.session_state.current_path = selected_drive
    
    # Display current path with navigation
    st.sidebar.text_area(
        "Current Path:",
        value=st.session_state.current_path,
        height=60,
        disabled=True
    )
    
    # Navigation buttons
    col1, col2, col3, col4 = st.sidebar.columns([1, 1, 1, 2])
    with col1:
        if st.button("⬅️", help="Go back", disabled=st.session_state.nav_position == 0):
            st.session_state.nav_position -= 1
            st.session_state.current_path = st.session_state.nav_history[st.session_state.nav_position]
            st.rerun()
    
    with col2:
        if st.button("➡️", help="Go forward", disabled=st.session_state.nav_position >= len(st.session_state.nav_history) - 1):
            st.session_state.nav_position += 1
            st.session_state.current_path = st.session_state.nav_history[st.session_state.nav_position]
            st.rerun()
    
    with col3:
        parent_path = str(Path(st.session_state.current_path).parent)
        if st.button("⬆️", help="Go to parent directory"):
            if parent_path != st.session_state.current_path:
                # Add to history
                st.session_state.nav_history = st.session_state.nav_history[:st.session_state.nav_position + 1]
                st.session_state.nav_history.append(parent_path)
                st.session_state.nav_position += 1
                st.session_state.current_path = parent_path
                st.rerun()
    
    with col4:
        if st.button("🏠 Home", help="Go to home directory"):
            home_path = str(Path.home())
            if home_path != st.session_state.current_path:
                # Add to history
                st.session_state.nav_history = st.session_state.nav_history[:st.session_state.nav_position + 1]
                st.session_state.nav_history.append(home_path)
                st.session_state.nav_position += 1
                st.session_state.current_path = home_path
                st.rerun()

    if container_mounts:
        st.sidebar.markdown("**Mounted Drives:**")
        for drive_label, target_path in container_mounts:
            mount_name = Path(target_path).name
            if st.sidebar.button(f"💽 {drive_label}", key=f"drive_btn_{mount_name}"):
                if st.session_state.current_path != target_path:
                    st.session_state.nav_history = st.session_state.nav_history[:st.session_state.nav_position + 1]
                    st.session_state.nav_history.append(target_path)
                    st.session_state.nav_position += 1
                    st.session_state.current_path = target_path
                    st.rerun()

    # List subdirectories
    subdirs = get_subdirectories(st.session_state.current_path)
    
    if subdirs:
        st.sidebar.markdown("**Folders:**")
        
        # Create a scrollable area with folders
        for subdir in subdirs[:20]:  # Limit to 20 folders to prevent UI overload
            if st.sidebar.button(f"📁 {subdir}", key=f"dir_{subdir}"):
                new_path = str(Path(st.session_state.current_path) / subdir)
                # Add to history
                st.session_state.nav_history = st.session_state.nav_history[:st.session_state.nav_position + 1]
                st.session_state.nav_history.append(new_path)
                st.session_state.nav_position += 1
                st.session_state.current_path = new_path
                st.rerun()
        
        if len(subdirs) > 20:
            st.sidebar.info(f"+ {len(subdirs) - 20} more folders")
    else:
        st.sidebar.info("No accessible subdirectories")
    
    # Manual path entry (optional)
    with st.sidebar.expander("✏️ Enter path manually"):
        manual_path = st.text_input(
            "Path:",
            placeholder="/path/to/folder or C:\\Users\\YourName\\Documents"
        )
        if st.button("Go"):
            if Path(manual_path).exists() and Path(manual_path).is_dir():
                # Add to history
                st.session_state.nav_history = st.session_state.nav_history[:st.session_state.nav_position + 1]
                st.session_state.nav_history.append(manual_path)
                st.session_state.nav_position += 1
                st.session_state.current_path = manual_path
                st.rerun()
            else:
                st.error("Invalid directory path")
    
    return st.session_state.current_path


def duplicate_finder_page():
    """Duplicate file finder interface."""
    st.title("🔍 Duplicate File Finder")
    st.markdown("Find potential duplicate files across two directories using fuzzy matching.")
    
    # How to use walkthrough
    with st.expander("ℹ️ How to Use - Duplicate File Finder", expanded=False):
        st.markdown(DUPLICATE_FINDER_HOW_TO)
    
    # How it works section - collapsed by default
    with st.expander("ℹ️ How It Works", expanded=False):
        st.markdown(DUPLICATE_FINDER_HOW_IT_WORKS)
    
    # Initialize directory paths
    if 'dir1_path' not in st.session_state:
        st.session_state.dir1_path = str(Path.home())
    if 'dir2_path' not in st.session_state:
        st.session_state.dir2_path = str(Path.home())
    if 'dir1_include_subdirs' not in st.session_state:
        st.session_state.dir1_include_subdirs = True
    if 'dir2_include_subdirs' not in st.session_state:
        st.session_state.dir2_include_subdirs = True
    if 'files_explored' not in st.session_state:
        st.session_state.files_explored = False
    
    # Two-column layout for folder selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Folder 1")
        
        # Folder 1 path display
        st.markdown("**Folder 1 Path:**")
        st.code(st.session_state.dir1_path, language=None)
        
        if st.button("📂 Select from Sidebar", key="set_dir1", use_container_width=True):
            # Use the current path from directory explorer
            if 'current_path' in st.session_state:
                st.session_state.dir1_path = st.session_state.current_path
                # Reset explored state when path changes
                st.session_state.files_explored = False
                st.rerun()
        
        include_subdirs1 = st.checkbox(
            "Include Subdirectories",
            value=st.session_state.dir1_include_subdirs,
            key="dir1_subdirs_check"
        )
        if st.session_state.dir1_include_subdirs != include_subdirs1:
            st.session_state.dir1_include_subdirs = include_subdirs1
            # Reset explored state when setting changes
            st.session_state.files_explored = False
        
        # Show file count only after exploration
        if st.session_state.files_explored and 'files1_info' in st.session_state:
            file_count = len(st.session_state.files1_info)
            subdir_text = " (including subdirectories)" if st.session_state.dir1_include_subdirs else ""
            st.success(f"✓ {file_count} files found{subdir_text}")
        elif not Path(st.session_state.dir1_path).exists():
            st.warning("Invalid directory")
        else:
            st.info("Ready to explore")
    
    with col2:
        st.subheader("📁 Folder 2")
        
        # Folder 2 path display
        st.markdown("**Folder 2 Path:**")
        st.code(st.session_state.dir2_path, language=None)
        
        if st.button("📂 Select from Sidebar", key="set_dir2", use_container_width=True):
            # Use the current path from directory explorer
            if 'current_path' in st.session_state:
                st.session_state.dir2_path = st.session_state.current_path
                # Reset explored state when path changes
                st.session_state.files_explored = False
                st.rerun()
        
        include_subdirs2 = st.checkbox(
            "Include Subdirectories",
            value=st.session_state.dir2_include_subdirs,
            key="dir2_subdirs_check"
        )
        if st.session_state.dir2_include_subdirs != include_subdirs2:
            st.session_state.dir2_include_subdirs = include_subdirs2
            # Reset explored state when setting changes
            st.session_state.files_explored = False
        
        # Show file count only after exploration
        if st.session_state.files_explored and 'files2_info' in st.session_state:
            file_count = len(st.session_state.files2_info)
            subdir_text = " (including subdirectories)" if st.session_state.dir2_include_subdirs else ""
            st.success(f"✓ {file_count} files found{subdir_text}")
        elif not Path(st.session_state.dir2_path).exists():
            st.warning("Invalid directory")
        else:
            st.info("Ready to explore")
    
    st.markdown("---")
    
    # Explore Files button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        explore_disabled = not (Path(st.session_state.dir1_path).exists() and Path(st.session_state.dir2_path).exists())
        if st.button("🔍 Explore Files", type="primary", use_container_width=True, disabled=explore_disabled):
            with st.spinner("Scanning directories..."):
                st.session_state.files1_info = DuplicateFinder.get_file_info(
                    st.session_state.dir1_path, 
                    st.session_state.dir1_include_subdirs
                )
                st.session_state.files2_info = DuplicateFinder.get_file_info(
                    st.session_state.dir2_path, 
                    st.session_state.dir2_include_subdirs
                )
                st.session_state.files_explored = True
                st.rerun()
    
    st.markdown("---")
    
    # Matching parameters
    st.subheader("⚙️ Matching Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name_threshold = st.slider(
            "Name Similarity Threshold:",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="Minimum similarity for filenames (0=completely different, 1=identical)"
        )
    
    with col2:
        use_tfidf = st.checkbox(
            "Use Smart Matching (TF-IDF)",
            value=True,
            help="Downweights common words, upweights unique terms for better matching"
        )
    
    st.markdown("---")
    
    # Find duplicates button (only enabled after exploration)
    if st.session_state.files_explored:
        if st.button("🔍 Find Duplicates", type="primary", use_container_width=True):
            with st.spinner("Searching for duplicates..."):
                # Use the already scanned file information
                files1 = st.session_state.files1_info
                files2 = st.session_state.files2_info
                
                # Calculate IDF if using TF-IDF
                idf = None
                if use_tfidf:
                    all_files = files1 + files2
                    idf = DuplicateFinder.calculate_idf(all_files)
                
                # Perform matching
                matches = []
                for file1 in files1:
                    for file2 in files2:
                        # Skip if different file extensions
                        if file1['extension'] != file2['extension']:
                            continue
                        
                        # Use TF-IDF or basic similarity
                        if use_tfidf and idf:
                            name_sim = DuplicateFinder.calculate_tfidf_similarity(
                                file1['name'],
                                file2['name'],
                                idf
                            )
                        else:
                            name_sim = DuplicateFinder.calculate_name_similarity(
                                file1['name'],
                                file2['name']
                            )
                        
                        size_sim = DuplicateFinder.calculate_size_similarity(
                            file1['size'],
                            file2['size']
                        )
                        
                        # Check if name meets minimum threshold (size is for display only)
                        if name_sim >= name_threshold:
                            # Calculate overall confidence based primarily on name
                            confidence = name_sim
                            
                            # Determine match reasons
                            reasons = []
                            if name_sim >= 0.95:
                                reasons.append("Name exact match")
                            elif name_sim >= 0.8:
                                reasons.append("Name very similar")
                            else:
                                reasons.append("Name similar")
                            
                            if size_sim >= 0.99:
                                reasons.append("Size exact match")
                            elif size_sim >= 0.95:
                                reasons.append("Size very close")
                            else:
                                reasons.append("Size similar")
                            
                            matches.append({
                                'file1_name': file1['name'],
                                'file1_path': file1['path'],
                                'file1_relative_path': file1.get('relative_path', file1['name']),
                                'file1_size': file1['size'],
                                'file2_name': file2['name'],
                                'file2_path': file2['path'],
                                'file2_relative_path': file2.get('relative_path', file2['name']),
                                'file2_size': file2['size'],
                                'name_similarity': name_sim,
                                'size_similarity': size_sim,
                                'confidence': confidence,
                                'reasons': ', '.join(reasons)
                            })
                
                # Sort by confidence (highest first)
                matches.sort(key=lambda x: x['confidence'], reverse=True)
                st.session_state.duplicate_matches = matches
    else:
        st.info("👆 Click 'Explore Files' first to scan directories")
    
    # Display results
    if 'duplicate_matches' in st.session_state and st.session_state.duplicate_matches:
        matches = st.session_state.duplicate_matches
        
        st.success(f"✓ Found {len(matches)} potential duplicate(s)")
        
        # Build display table with explicit absolute paths
        display_data = []
        for match in matches:
            # Resolve to a canonical absolute path for consistent display in Docker/Windows.
            file1_display = str(Path(match['file1_path']).resolve(strict=False))
            file2_display = str(Path(match['file2_path']).resolve(strict=False))
            
            display_data.append({
                "Full Path (Folder 1)": file1_display,
                "Size 1": DuplicateFinder.format_size(match['file1_size']),
                "Full Path (Folder 2)": file2_display,
                "Size 2": DuplicateFinder.format_size(match['file2_size']),
                "Name Match": f"{match['name_similarity']:.1%}",
                "Size Match": f"{match['size_similarity']:.1%}",
                "Confidence": f"{match['confidence']:.1%}",
                "Reason": match['reasons']
            })
        
        st.dataframe(display_data, use_container_width=True, hide_index=True)
        
        # Actions on selected match
        st.markdown("---")
        st.subheader("Quick Actions")
        
        selected_idx = st.selectbox(
            "Select a match to open:",
            options=range(len(matches)),
            format_func=lambda i: f"{matches[i]['file1_name']} ↔ {matches[i]['file2_name']}",
            key="match_selector"
        )
        
        if selected_idx is not None:
            # Folder actions row
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📂 Open Folder 1", use_container_width=True):
                    try:
                        os.startfile(st.session_state.dir1_path)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                if st.button("📂 Open Folder 2", use_container_width=True):
                    try:
                        os.startfile(st.session_state.dir2_path)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col3:
                if st.button("📂 Open Both Folders", use_container_width=True):
                    try:
                        os.startfile(st.session_state.dir1_path)
                        os.startfile(st.session_state.dir2_path)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # File actions row
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("🚀 Open File 1", use_container_width=True):
                    try:
                        os.startfile(matches[selected_idx]['file1_path'])
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                if st.button("🚀 Open File 2", use_container_width=True):
                    try:
                        os.startfile(matches[selected_idx]['file2_path'])
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    elif 'duplicate_matches' in st.session_state:
        st.info("No duplicates found with current thresholds. Try lowering the similarity thresholds.")


def file_renamer_page():
    """Original file renaming interface."""
    st.title("📁 File Name Cleaner")
    st.markdown("Clean up and standardize your file names with ease!")
    
    # How to use walkthrough
    with st.expander("ℹ️ How to Use - File Cleaner", expanded=False):
        st.markdown(FILE_CLEANER_HOW_TO)
    
    # Date format help - collapsed by default
    with st.expander("ℹ️ Supported Date Formats", expanded=False):
        st.markdown(FILE_CLEANER_DATE_FORMATS)
    
    # Use directory explorer
    directory = directory_explorer()
    
    # Check for files in selected directory
    if directory and Path(directory).exists() and Path(directory).is_dir():
        dir_path = Path(directory)
        files = [f.name for f in dir_path.iterdir() if f.is_file()]
    else:
        files = []
    
    # Main content area - File renaming operations
    
    # Main content area - Cleanup operations
    st.header("Cleanup Operations")
    st.markdown("Select and configure the operations to apply:")
    
    operations = []
    
    # Operation 1: Replace string (with multiple pairs)
    use_string_replace = st.checkbox("Replace strings in filenames", value=False)
    if use_string_replace:
        # Initialize replacement pairs in session state
        if 'replacement_pairs' not in st.session_state:
            st.session_state.replacement_pairs = [{'source': '.', 'replacement': '_'}]
        
        st.markdown("**String Replacement Pairs** (applied in order)")
        
        # Display existing pairs
        for idx, pair in enumerate(st.session_state.replacement_pairs):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                source = st.text_input(
                    f"Replace:",
                    value=pair['source'],
                    key=f"replace_source_{idx}",
                    placeholder="text to find"
                )
            with col2:
                replacement = st.text_input(
                    f"With:",
                    value=pair['replacement'],
                    key=f"replace_with_{idx}",
                    placeholder="replacement text"
                )
            with col3:
                st.write("")  # Spacing
                if st.button("🗑️", key=f"delete_pair_{idx}", help="Delete this pair"):
                    st.session_state.replacement_pairs.pop(idx)
                    st.rerun()
            
            # Update the pair in session state
            st.session_state.replacement_pairs[idx] = {'source': source, 'replacement': replacement}
        
        # Add new pair button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("➕ Add Pair"):
                st.session_state.replacement_pairs.append({'source': '', 'replacement': ''})
                st.rerun()
        
        # Add all valid pairs to operations
        for pair in st.session_state.replacement_pairs:
            if pair['source']:  # Only add if source is not empty
                operations.append({
                    'type': 'replace_string',
                    'source': pair['source'],
                    'replacement': pair['replacement']
                })
    
    # Operation 2: Camel Case
    col1, col2 = st.columns([3, 1])
    with col1:
        use_camel = st.checkbox("Convert to camelCase", value=False)
    with col2:
        if use_camel:
            upper_first = st.checkbox("PascalCase", value=False, key="pascal")
            operations.append({'type': 'camel_case', 'upper_first': upper_first})
    
    # Operation 3: Regex Replace
    use_regex = st.checkbox("Apply regex find and replace (advanced)", value=False)
    if use_regex:
        st.markdown("**Regex Pattern Matching** - Use capture groups `()` and reference them with `\\1`, `\\2`, etc.")
        
        col1, col2 = st.columns(2)
        with col1:
            regex_pattern = st.text_input("Pattern:", placeholder=r"(\d+) - (.+)", help="Use () to capture groups")
        with col2:
            regex_replacement = st.text_input("Replacement:", placeholder=r"\2 - \1", help=r"Use \1, \2, etc. to reference captured groups")
        
        col1, col2 = st.columns(2)
        with col1:
            preserve_ext = st.checkbox("Preserve extension", value=True, key="preserve")
        with col2:
            if st.button("ℹ️ Examples", key="regex_examples"):
                st.session_state.show_regex_examples = not st.session_state.get('show_regex_examples', False)
        
        if st.session_state.get('show_regex_examples', False):
            st.info("""
**Examples:**
- Swap parts: Pattern `(\\d+) - (.+)` → Replacement `\\2 - \\1`
  - `123 - Dogs and Cats.txt` → `Dogs and Cats - 123.txt`
- Remove prefix: Pattern `^prefix_` → Replacement `` (empty)
- Add suffix: Pattern `(.+)` → Replacement `\\1_backup`
- Uppercase word: Pattern `(\\w+)` → Replacement `\\U\\1`
- Lowercase word: Pattern `(\\w+)` → Replacement `\\L\\1`
- Title case: Pattern `(\\w+)` → Replacement `\\T\\1`
- Date with dashes: Pattern `\\d{4}-\\d{2}-\\d{2}` → Replacement `\\1` (captures 2025-01-31)
- Date with dots: Pattern `([\\d.]+)` → Replacement `\\1` (captures 2025.01.31)

**Case Conversion:** Use `\\U\\1` (uppercase), `\\L\\1` (lowercase), `\\T\\1` (title case) with captured groups
            """)
        
        if regex_pattern:
            # Validate regex pattern before adding to operations
            try:
                import re
                re.compile(regex_pattern)
                # Pattern is valid, add to operations
                operations.append({
                    'type': 'regex',
                    'pattern': regex_pattern,
                    'replacement': regex_replacement if regex_replacement else '',
                    'preserve_extension': preserve_ext
                })
            except re.error as e:
                st.error(f"Invalid regex pattern: {str(e)}")
            except Exception as e:
                st.error(f"Error with regex: {str(e)}")
    
    # Operation 4: Standardize dates
    col1, col2 = st.columns([3, 1])
    with col1:
        use_dates = st.checkbox("Standardize date formats", value=False)
    with col2:
        if use_dates:
            date_format = st.selectbox(
                "Output format:",
                ["%Y.%m.%d", "%Y-%m-%d", "%Y_%m_%d", "%d-%m-%Y"],
                key="date_format"
            )
            operations.append({'type': 'standardize_dates', 'format': date_format})
    
    st.markdown("---")
    
    # Preview section - Always show files
    st.header("File Preview")
    
    if directory and files:
        # File selection
        st.subheader("Select Files")
        
        # Initialize selected files in session state
        if 'selected_files' not in st.session_state:
            st.session_state.selected_files = set()
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("Select All"):
                st.session_state.selected_files = set(files)
                st.rerun()
        with col2:
            if st.button("Deselect All"):
                st.session_state.selected_files = set()
                st.rerun()
        
        # Create a cache key based on directory and operations to avoid regenerating preview on every checkbox click
        import json
        operations_key = json.dumps(operations, sort_keys=True) + directory
        
        # Only regenerate preview if operations or directory changed
        if 'preview_cache_key' not in st.session_state or st.session_state.preview_cache_key != operations_key:
            with st.spinner("Generating preview..."):
                # Get all changes if operations exist, otherwise show original names
                if operations:
                    changes = FileNameCleaner.preview_changes(directory, operations)
                    st.session_state.cached_changes_dict = {original: new_name for original, new_name, _ in changes}
                else:
                    st.session_state.cached_changes_dict = {}
                st.session_state.preview_cache_key = operations_key
        
        changes_dict = st.session_state.cached_changes_dict
        
        # Build preview table for all files with selection checkboxes
        preview_data = []
        altered_count = 0
        
        # Sort files alphabetically and create index mapping
        sorted_files = sorted(files)
        
        for idx, filename in enumerate(sorted_files, start=1):
            new_name = changes_dict.get(filename, filename)
            is_altered = new_name != filename
            is_selected = filename in st.session_state.selected_files
            
            if is_altered:
                altered_count += 1
            
            preview_data.append({
                "#": idx,
                "Select": is_selected,
                "Current Filename": filename,
                "New Filename": new_name,
                "Altered": is_altered
            })
        
        # Display preview table with selection column
        edited_df = st.data_editor(
            preview_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "#": st.column_config.NumberColumn(
                    "#",
                    help="Alphabetical index",
                    width="small",
                ),
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select files to apply operations to",
                    default=False,
                )
            },
            disabled=["#", "Current Filename", "New Filename", "Altered"],
            key="file_selector"
        )
        
        # Summarize changes button
        st.markdown("---")
        if st.button("📊 Summarize Potential Changes", use_container_width=True):
            # Extract selections from edited dataframe when button is clicked
            new_selected = set()
            if isinstance(edited_df, list):
                # st.data_editor returns a list when input is a list
                for row in edited_df:
                    if row['Select']:
                        new_selected.add(row['Current Filename'])
            else:
                # Handle DataFrame case
                for row in edited_df.to_dict('records'):
                    if row['Select']:
                        new_selected.add(row['Current Filename'])
            
            # Update session state with selections
            st.session_state.selected_files = new_selected
            st.session_state.show_summary = True
        
        # Show summary and apply button if summarize was clicked
        if st.session_state.get('show_summary', False):
            # Calculate selected altered count
            selected_altered_count = sum(1 for filename in st.session_state.selected_files 
                                         if changes_dict.get(filename, filename) != filename)
            
            # Display summary message
            if altered_count > 0:
                st.success(f"Found {altered_count} file(s) to rename out of {len(files)} total files | Selected: {len(st.session_state.selected_files)} ({selected_altered_count} will be renamed)")
            else:
                st.info(f"Showing {len(files)} file(s) - no changes will be applied | Selected: {len(st.session_state.selected_files)}")
            
            # Apply changes button (only show if there are selected files with changes)
            if selected_altered_count > 0:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("✅ Apply Changes to Selected Files", type="primary", use_container_width=True):
                        with st.spinner("Applying changes..."):
                            # Reconstruct changes list for apply_changes function (only selected files)
                            changes_to_apply = []
                            for filename in st.session_state.selected_files:
                                new_name = changes_dict.get(filename)
                                if new_name and new_name != filename:
                                    file_path = str(Path(directory) / filename)
                                    changes_to_apply.append((filename, new_name, file_path))
                            
                            success_count, errors = FileNameCleaner.apply_changes(changes_to_apply)
                        
                        if success_count > 0:
                            st.success(f"✓ Successfully renamed {success_count} file(s)!")
                            # Clear selection and summary after successful rename
                            st.session_state.selected_files = set()
                            st.session_state.show_summary = False
                        
                        if errors:
                            st.error("Some errors occurred:")
                            for error in errors:
                                st.error(f"• {error}")
                        
                        # Rerun to refresh the file list
                        if success_count > 0:
                            st.rerun()
        
        # File launcher section
        st.markdown("---")
        st.subheader("Quick Actions")
        
        # Create a selectbox for file selection
        selected_file = st.selectbox(
            "Select a file to open:",
            options=[""] + sorted(files),
            key="file_launcher"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🚀 Open File", disabled=not selected_file, use_container_width=True):
                if selected_file:
                    file_path = str(Path(directory) / selected_file)
                    try:
                        os.startfile(file_path)
                        st.success(f"Opened: {selected_file}")
                    except Exception as e:
                        st.error(f"Error opening file: {str(e)}")
        
        with col2:
            if st.button("📂 Open Folder", use_container_width=True):
                try:
                    os.startfile(directory)
                    st.success("Opened folder in Explorer")
                except Exception as e:
                    st.error(f"Error opening folder: {str(e)}")
    
    elif directory and not files:
        st.warning("No files found in the selected directory.")
    
    # Instructions
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        ### Instructions
        
        1. **Select a directory** in the sidebar containing the files you want to rename
        2. **Choose operations** by checking the boxes for the cleanup functions you want to apply
        3. **Configure each operation** with the desired settings
        4. **Preview the changes** to see what the new names will look like
        5. **Apply changes** when you're satisfied with the preview
        
        ### Operation Details
        
        - **Replace string**: Replace any string or character in filenames with another (extension preserved)
        - **CamelCase**: Converts filenames to camelCase or PascalCase
        - **Regex**: Advanced find and replace using regular expressions (supports groups like \\1, \\2)
        - **Standardize dates**: Automatically detects dates in various formats and standardizes them
        
        ### Tips
        
        - Operations are applied in the order shown
        - File extensions are always preserved
        - The preview shows exactly what will happen before you commit
        - If a filename conflict occurs, that file will be skipped
        """)


def main():
    """Main application with tabbed interface."""
    st.set_page_config(
        page_title="File Management App",
        page_icon="📁",
        layout="wide"
    )
    
    # Create tabs
    tab1, tab2 = st.tabs(["📁 File Renamer", "🔍 Duplicate Finder"])
    
    with tab1:
        file_renamer_page()
    
    with tab2:
        duplicate_finder_page()


if __name__ == "__main__":
    main()
