from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal

class AppCard(QWidget):
    install_clicked = pyqtSignal(dict)  # Signal emitting package data
    remove_clicked = pyqtSignal(dict)

    def __init__(self, package_data, is_installed=False):
        super().__init__()
        self.package_data = package_data
        self.is_installed = is_installed
        
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Icon (Placeholder for now)
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setStyleSheet("background-color: #ddd; border-radius: 5px;")
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        name_label = QLabel(self.package_data.get('Name', 'Unknown'))
        name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        
        desc_text = self.package_data.get('Description', 'No description available.')
        if len(desc_text) > 80:
            desc_text = desc_text[:77] + "..."
        desc_label = QLabel(desc_text)
        desc_label.setStyleSheet("color: #cccccc;")
        desc_label.setWordWrap(True)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        layout.addLayout(info_layout)
        
        # Action Button
        action_layout = QVBoxLayout()
        action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.is_installed:
            self.btn_action = QPushButton("Remove")
            self.btn_action.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c9302c;
                }
            """)
            self.btn_action.clicked.connect(self.on_remove)
        else:
            self.btn_action = QPushButton("Install")
            self.btn_action.setStyleSheet("""
                QPushButton {
                    background-color: #5cb85c;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4cae4c;
                }
            """)
            self.btn_action.clicked.connect(self.on_install)
            
        action_layout.addWidget(self.btn_action)
        
        # Version Label
        version_label = QLabel(self.package_data.get('Version', ''))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #888; font-size: 10px;")
        action_layout.addWidget(version_label)
        
        layout.addLayout(action_layout)
        
        # Styling
        self.setStyleSheet("""
            AppCard {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 5px;
            }
        """)

    def on_install(self):
        self.install_clicked.emit(self.package_data)

    def on_remove(self):
        self.remove_clicked.emit(self.package_data)
