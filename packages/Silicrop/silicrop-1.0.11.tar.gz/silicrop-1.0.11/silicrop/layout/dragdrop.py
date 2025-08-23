from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
import os
from PyQt5.QtWidgets import QSizePolicy

class FileDropListWidget(QListWidget):
    def __init__(self, on_files_dropped=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.on_files_dropped = on_files_dropped
        self.placeholder_item = None
        # Configurer le mode de sélection simple pour la sélection manuelle
        self.setSelectionMode(QListWidget.SingleSelection)
        # Flag pour distinguer la sélection programmatique de la sélection manuelle
        self.programmatic_selection = False
        # Flag permanent pour indiquer si Select All a été utilisé
        self.select_all_used = False
        self.show_placeholder()

    def show_placeholder(self):
        self.clear()
        self.placeholder_item = QListWidgetItem("🡇 Drag and Drop Images Below 🡇")
        self.placeholder_item.setFlags(Qt.NoItemFlags)
        self.placeholder_item.setForeground(Qt.gray)
        self.addItem(self.placeholder_item)

    def hide_placeholder(self):
        if self.placeholder_item:
            self.takeItem(self.row(self.placeholder_item))
            self.placeholder_item = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        added = False
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path) and file_path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")):
                    file_name = os.path.basename(file_path)
                    item = QListWidgetItem(file_name)
                    item.setData(Qt.UserRole, file_path)
                    self.hide_placeholder()
                    self.addItem(item)
                    if self.on_files_dropped:
                        self.on_files_dropped(file_path)
                    added = True
        if not added and self.count() == 0:
            self.show_placeholder()
        event.acceptProposedAction()




class FileDropListPanel(QWidget):
    def __init__(self, on_files_dropped=None):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # 📘 Instruction message
        self.hint_label = QLabel("📂 Drag and drop images here (.jpg, .png...)")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet("color: #555; font-style: italic;")

        # 📋 List widget
        self.list_widget = FileDropListWidget(on_files_dropped)
        self.list_widget.setStyleSheet("""
            font-size: 13px;
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e1e1e1;
            }
        """)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 🧹 Action buttons (fixés en bas)
        select_all_btn = QPushButton("☑ Select All")
        select_all_btn.setObjectName("select_all_btn")  # Donner un nom pour pouvoir le retrouver
        deselect_all_btn = QPushButton("☐ Deselect All")
        deselect_all_btn.setObjectName("deselect_all_btn")
        delete_selected_btn = QPushButton("🗑 Delete Selected")
        delete_all_btn = QPushButton("🧹 Delete All")

        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn.clicked.connect(self.deselect_all)
        delete_selected_btn.clicked.connect(self.remove_selected)
        delete_all_btn.clicked.connect(self.remove_all)

        # Layout en deux lignes
        button_layout = QVBoxLayout()
        
        # Première ligne : Select All, Deselect All
        first_row = QHBoxLayout()
        first_row.addWidget(select_all_btn)
        first_row.addWidget(deselect_all_btn)
        
        # Deuxième ligne : Delete Selected, Delete All
        second_row = QHBoxLayout()
        second_row.addWidget(delete_selected_btn)
        second_row.addWidget(delete_all_btn)
        
        button_layout.addLayout(first_row)
        button_layout.addLayout(second_row)

        # 🔽 Séparateur visuel au-dessus des boutons
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        # 📦 Organisation dans le layout principal
        layout.addWidget(self.hint_label)
        layout.addWidget(self.list_widget)
        layout.addWidget(line)
        layout.addLayout(button_layout)

    def remove_selected(self):
        selected_items = self.list_widget.selectedItems()
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))
        if self.list_widget.count() == 0:
            self.list_widget.show_placeholder()

    def reset_item_appearance(self, item):
        """Reset the appearance of an item to default."""
        item.setBackground(Qt.transparent)
        item.setForeground(Qt.black)

    def select_all(self):
        """Mark all items as selected for batch processing."""
        # Marquer comme sélection programmatique
        self.list_widget.programmatic_selection = True
        self.list_widget.select_all_used = True
        
        selected_count = 0
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item != self.list_widget.placeholder_item:
                selected_count += 1
        
        # Réinitialiser le flag temporaire après un court délai
        QTimer.singleShot(100, lambda: setattr(self.list_widget, 'programmatic_selection', False))
        
        # Afficher un message de confirmation
        print(f"✅ {selected_count} éléments marqués pour traitement batch")
        
        # Mettre à jour le texte du bouton temporairement pour confirmation visuelle
        select_all_btn = self.findChild(QPushButton, "select_all_btn")
        if select_all_btn:
            original_text = select_all_btn.text()
            select_all_btn.setText(f"☑ Batch ({selected_count})")
            # Remettre le texte original après 2 secondes
            QTimer.singleShot(2000, lambda: select_all_btn.setText(original_text))

    def deselect_all(self):
        """Deselect all items in the list widget."""
        # Marquer comme sélection programmatique
        self.list_widget.programmatic_selection = True
        self.list_widget.select_all_used = False
        
        self.list_widget.clearSelection()
        
        # Réinitialiser le flag temporaire après un court délai
        QTimer.singleShot(100, lambda: setattr(self.list_widget, 'programmatic_selection', False))
        
        print("✅ Tous les éléments désélectionnés")
        
        # Mettre à jour le texte du bouton temporairement pour confirmation visuelle
        deselect_all_btn = self.findChild(QPushButton, "deselect_all_btn")
        if deselect_all_btn:
            original_text = deselect_all_btn.text()
            deselect_all_btn.setText("☐ Deselected")
            # Remettre le texte original après 2 secondes
            QTimer.singleShot(2000, lambda: deselect_all_btn.setText(original_text))

    def remove_all(self):
        self.list_widget.clear()
        self.list_widget.show_placeholder()

    def get_selected_paths(self):
        """Get the file paths of all selected items."""
        # Si Select All a été utilisé, retourner tous les chemins
        if hasattr(self.list_widget, 'select_all_used') and self.list_widget.select_all_used:
            return self.get_all_paths()
        
        # Sinon, retourner seulement les éléments visuellement sélectionnés
        selected_items = self.list_widget.selectedItems()
        paths = []
        for item in selected_items:
            if item != self.list_widget.placeholder_item:
                file_path = item.data(Qt.UserRole)
                if file_path:
                    paths.append(file_path)
        return paths

    def get_all_paths(self):
        """Get the file paths of all items in the list."""
        paths = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item != self.list_widget.placeholder_item:
                file_path = item.data(Qt.UserRole)
                if file_path:
                    paths.append(file_path)
        return paths

    def get_list_widget(self):
        return self.list_widget
