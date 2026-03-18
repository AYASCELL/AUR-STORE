from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QLabel, QLineEdit, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ui.components import AppCard
from backend.aur_api import AurApi
from backend.package_manager import PackageManager

class SearchThread(QThread):
    results_ready = pyqtSignal(list)

    def __init__(self, query):
        super().__init__()
        self.query = query
        self.api = AurApi()

    def run(self):
        results = self.api.search(self.query)
        self.results_ready.emit(results)

class ProcessWaiter(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, process):
        super().__init__()
        self.process = process

    def run(self):
        if self.process:
            self.process.wait()
        self.finished_signal.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AYASCELL - Arch Software Store")
        self.resize(1000, 700)
        
        self.package_manager = PackageManager()
        
        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e; 
                color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #cdcdcd;
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:horizontal {
                background: #cdcdcd;
                min-width: 20px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #252526; border-right: 1px solid #333333;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(10)
        
        self.btn_explore = self.create_sidebar_button("Explore")
        self.btn_installed = self.create_sidebar_button("Installed")
        self.btn_updates = self.create_sidebar_button("Updates")
        
        sidebar_layout.addWidget(self.btn_explore)
        sidebar_layout.addWidget(self.btn_installed)
        sidebar_layout.addWidget(self.btn_updates)
        sidebar_layout.addStretch()
        
        # Content Area
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: #1e1e1e;")
        
        # Explore Page
        self.page_explore = QWidget()
        self.setup_explore_page()
        
        # Installed Page
        self.page_installed = QWidget()
        self.setup_installed_page()
        
        # Updates Page
        self.page_updates = QWidget()
        self.setup_updates_page()
        
        self.content_area.addWidget(self.page_explore)
        self.content_area.addWidget(self.page_installed)
        self.content_area.addWidget(self.page_updates)
        
        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
        
        # Connect signals
        self.btn_explore.clicked.connect(lambda: self.content_area.setCurrentWidget(self.page_explore))
        self.btn_installed.clicked.connect(self.load_installed_apps)
        self.btn_updates.clicked.connect(self.load_updates)

    def create_sidebar_button(self, text):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 20px;
                border: none;
                background-color: transparent;
                font-size: 14px;
                color: #cccccc;
            }
            QPushButton:checked {
                background-color: #37373d;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #2a2d2e;
            }
        """)
        if text == "Explore":
            btn.setChecked(True)
        return btn

    def setup_explore_page(self):
        layout = QVBoxLayout(self.page_explore)
        
        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search applications...")
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #333333;
                border-radius: 5px;
                font-size: 14px;
                background-color: #3c3c3c;
                color: #ffffff;
            }
        """)
        self.btn_search = QPushButton("Search")
        self.btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_search.clicked.connect(self.perform_search)
        self.btn_search.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
        """)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        
        layout.addLayout(search_layout)
        
        # Results Area
        self.results_list = QListWidget()
        self.results_list.setFrameShape(QListWidget.Shape.NoFrame)
        self.results_list.setSpacing(5)
        self.results_list.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        layout.addWidget(self.results_list)

    def setup_installed_page(self):
        layout = QVBoxLayout(self.page_installed)
        label = QLabel("Installed Applications")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #ffffff;")
        layout.addWidget(label)
        
        self.installed_list = QListWidget()
        self.installed_list.setFrameShape(QListWidget.Shape.NoFrame)
        self.installed_list.setSpacing(5)
        self.installed_list.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        layout.addWidget(self.installed_list)

    def setup_updates_page(self):
        layout = QVBoxLayout(self.page_updates)
        
        header_layout = QHBoxLayout()
        label = QLabel("Updates Available")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #ffffff;")
        
        self.btn_update_all = QPushButton("Update All (System)")
        self.btn_update_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update_all.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #5cb85c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)
        self.btn_update_all.clicked.connect(self.handle_update_all)
        
        header_layout.addWidget(label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_update_all)
        
        layout.addLayout(header_layout)
        
        self.updates_list = QListWidget()
        self.updates_list.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        layout.addWidget(self.updates_list)

    def handle_update_all(self):
        process = self.package_manager.update_system_in_terminal()
        if process:
            self.waiter = ProcessWaiter(process)
            self.waiter.finished_signal.connect(self.load_updates)
            self.waiter.start()



    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        
        self.results_list.clear()
        self.search_thread = SearchThread(query)
        self.search_thread.results_ready.connect(self.display_search_results)
        self.search_thread.start()

    def display_search_results(self, results):
        self.results_list.clear()
        for pkg in results:
            item = QListWidgetItem(self.results_list)
            # Check if installed
            is_installed = self.package_manager.is_installed(pkg['Name'])
            
            card = AppCard(pkg, is_installed=is_installed)
            card.install_clicked.connect(self.handle_install)
            card.remove_clicked.connect(self.handle_remove)
            
            item.setSizeHint(card.sizeHint())
            self.results_list.setItemWidget(item, card)

    def load_installed_apps(self):
        self.content_area.setCurrentWidget(self.page_installed)
        self.installed_list.clear()
        # This can be slow, might need a thread
        pkgs = self.package_manager.list_installed()
        for pkg in pkgs:
            # We need more info than just name/version for the card ideally, 
            # but for now we use what we have.
            pkg_data = {
                'Name': pkg['name'],
                'Version': pkg['version'],
                'Description': 'Installed package'
            }
            item = QListWidgetItem(self.installed_list)
            card = AppCard(pkg_data, is_installed=True)
            card.remove_clicked.connect(self.handle_remove)
            item.setSizeHint(card.sizeHint())
            self.installed_list.setItemWidget(item, card)


    def handle_install(self, package_data):
        pkg_name = package_data['Name']
        print(f"Starting installation for: {pkg_name}")
        process = self.package_manager.install_package_in_terminal(pkg_name)
        if process:
            # Wait for it to finish then refresh
            self.waiter = ProcessWaiter(process)
            # Determine which page to refresh based on current index
            current_index = self.content_area.currentIndex()
            if current_index == 2: # Updates page
                self.waiter.finished_signal.connect(self.load_updates)
            elif current_index == 1: # Installed page
                self.waiter.finished_signal.connect(self.load_installed_apps)
            else:
                # If in explore, maybe refresh installed list in background or do nothing
                # But user might want to see the button change to "Remove"
                # For now, let's just refresh installed list if we are there, 
                # or if we are in explore, we might need to refresh the search results?
                # Refreshing search results is expensive (network).
                # Let's just refresh installed list as a safe bet if user switches.
                self.waiter.finished_signal.connect(self.load_installed_apps)
            
            self.waiter.start()
        else:
            print("Failed to launch terminal.")

    def handle_remove(self, package_data):
        pkg_name = package_data['Name']
        print(f"Removing: {pkg_name}")
        
        success = self.package_manager.remove_package(pkg_name)
        if success:
            self.load_installed_apps()
            # If we are in Updates page, we should refresh it too?
            if self.content_area.currentIndex() == 2:
                self.load_updates()

    def load_updates(self):
        self.content_area.setCurrentWidget(self.page_updates)
        self.updates_list.clear()
        
        # This should definitely be threaded
        updates = self.package_manager.check_updates()
        
        if not updates:
            item = QListWidgetItem("No updates available.")
            self.updates_list.addItem(item)
            return

        for pkg in updates:
            item = QListWidgetItem(self.updates_list)
            
            # Custom card for updates might show "v1.0 -> v1.1"
            current_ver = pkg.get('CurrentVersion', '?')
            new_ver = pkg.get('Version', '?')
            
            # Update description to show versions clearly
            if pkg.get('IsOfficial'):
                pkg['Description'] = f"System Update: {current_ver} -> {new_ver}"
            else:
                pkg['Description'] = f"AUR Update: {current_ver} -> {new_ver}"
            
            card = AppCard(pkg, is_installed=True) # It is installed
            # Change button to "Update"
            card.btn_action.setText("Update")
            card.btn_action.setStyleSheet("""
                QPushButton {
                    background-color: #f0ad4e;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #ec971f;
                }
            """)
            # Reuse install logic (it does the same thing: makepkg -si)
            card.btn_action.clicked.disconnect()
            card.btn_action.clicked.connect(lambda checked, p=pkg: self.handle_install(p))
            
            item.setSizeHint(card.sizeHint())
            self.updates_list.setItemWidget(item, card)


