import pytest
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication
from scripts.Window import Window

def test_slots():

    app = QApplication([])

    test_window = Window()
    assert hasattr(test_window, "start"), "'start' slot is missing"
    assert hasattr(test_window, "kill_thread"), "'kill_thread' slot is missing"
    assert hasattr(test_window, "load_file"), "'load_file' slot is missing"

    test_window.start()

    with patch("PyQt5.QtWidgets.QFileDialog.getOpenFileName") as mock_file:
        mock_file.return_value = ('E:/OneDrive - ApplusGlobal/dev/Detection-Interface/tests/test_data/video-test1.mp4', '')
        test_window.load_file()
        assert test_window.th.file_path == "E:/OneDrive - ApplusGlobal/dev/Detection-Interface/tests/test_data/video-test1.mp4"

    test_window.kill_thread()
    app.processEvents()

    
