import os

from ..client.pofile import find_po_files


def test_find_po_files(tmp_path):
    # Set up the directory structure and files
    # tmp_path is a pytest-provided temporary directory that is unique per test

    # Create a structure within the temp directory
    nested_dir_1 = tmp_path / "level1"
    nested_dir_2 = nested_dir_1 / "level2"
    nested_dir_3 = nested_dir_2 / "level3"
    nested_dir_4 = nested_dir_3 / "level4"
    nested_dir_5 = nested_dir_4 / "level5"
    nested_dir_6 = nested_dir_5 / "level6"

    # Create directories
    nested_dir_1.mkdir()
    nested_dir_2.mkdir()
    nested_dir_3.mkdir()
    nested_dir_4.mkdir()
    nested_dir_5.mkdir()
    nested_dir_6.mkdir()

    # Create .po files in various directories
    po_file_1 = nested_dir_1 / "file1.po"
    po_file_2 = nested_dir_3 / "file2.po"
    po_file_3 = nested_dir_5 / "file3.po"
    po_file_1.touch()
    po_file_2.touch()
    po_file_3.touch()

    # Create non-.po files
    non_po_file = nested_dir_4 / "file.txt"
    non_po_file.touch()

    # Test with default dir_depth=5
    result = find_po_files(tmp_path)
    expected_files = [
        os.path.relpath(po_file_1, tmp_path),
        os.path.relpath(po_file_2, tmp_path),
        os.path.relpath(po_file_3, tmp_path),
    ]
    assert sorted(result) == sorted(expected_files)

    # Test with dir_depth=3, expecting only files within the depth limit
    result = find_po_files(tmp_path, dir_depth=3)
    expected_files = [
        os.path.relpath(po_file_1, tmp_path),
        os.path.relpath(po_file_2, tmp_path),
    ]
    assert sorted(result) == sorted(expected_files)

    # Test with dir_depth=1, expecting only top-level .po files
    result = find_po_files(tmp_path, dir_depth=1)
    expected_files = [
        os.path.relpath(po_file_1, tmp_path),
    ]
    assert sorted(result) == sorted(expected_files)

    # Test when no .po files are within the allowed depth
    result = find_po_files(tmp_path, dir_depth=0)
    assert result == []

    # Test in an empty directory
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    result = find_po_files(empty_dir)
    assert result == []
