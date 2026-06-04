import sys
import os
import random
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, 
                             QScrollArea, QHBoxLayout, QMenu, QVBoxLayout, 
                             QFileIconProvider, QLineEdit, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRect, QFileInfo, QTimer
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRect, QFileInfo, QTimer, QParallelAnimationGroup


# Cartella ufficiale del progetto
BASE_DIR = r"C:\customstart"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(BASE_DIR, "config_tiles.json")

class TileSize:
    PICCOLO = (1, 1)
    MEDIO = (2, 2)
    LARGO = (4, 2)
    GRANDE = (4, 4)

class Tile(QPushButton):
    def __init__(self, name, path, lnk_path=None, parent=None, saved_data=None):
        super().__init__(parent)
        self.name = name
        self.path = path
        self.lnk_path = lnk_path if lnk_path else path
        
        # Carica dati da JSON o imposta i default
        if saved_data:
            self.grid_x = saved_data.get("grid_x", -1)
            self.grid_y = saved_data.get("grid_y", -1)
            size_name = saved_data.get("grid_size", "MEDIO")
            self.grid_size = getattr(TileSize, size_name, TileSize.MEDIO)
            self.base_color = QColor(saved_data.get("color", "#0078D7"))
        else:
            self.grid_x = -1
            self.grid_y = -1
            self.grid_size = TileSize.MEDIO  
            self.base_color = QColor(random.randint(15, 170), random.randint(15, 170), random.randint(15, 170))
        
        self.layout_interno = QVBoxLayout(self)
        self.layout_interno.setContentsMargins(12, 12, 12, 12)
        
        self.icon_label = QLabel(self)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.text_label = QLabel(self.name, self)
        self.text_label.setStyleSheet("color: white; font-family: 'Segoe UI', sans-serif; font-size: 11px; font-weight: bold;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.text_label.setWordWrap(True)
        
        self.layout_interno.addWidget(self.icon_label, 1)
        self.layout_interno.addWidget(self.text_label, 0)
        
        self.estrai_icona_windows()
        self.update_style()
        
        self.dragging = False
        self.drag_ready = False
        self.drag_start_pos = QPoint()
        
        self.hold_timer = QTimer(self)
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self.attiva_drag_ready)

    def estrai_icona_windows(self):
        try:
            if self.path == "close": return
            file_info = QFileInfo(self.lnk_path if os.path.exists(self.lnk_path) else self.path)
            provider = QFileIconProvider()
            icon = provider.icon(file_info)
            if not icon.isNull():
                self.icon_label.setPixmap(icon.pixmap(48, 48))
                return
        except: pass
        self.icon_label.setText(self.name[0].upper())
        self.icon_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 28px; font-weight: bold;")

    def update_style(self):
        self.setStyleSheet(f"QPushButton {{ background-color: {self.base_color.name()}; border: none; }} QPushButton:hover {{ border: 3px solid white; }}")
        if self.grid_size == TileSize.PICCOLO:
            self.text_label.setVisible(False)
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.text_label.setVisible(True)
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    def attiva_drag_ready(self):
        self.drag_ready = True
        self.raise_()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.position().toPoint()
            self.dragging = False
            self.drag_ready = False
            self.hold_timer.start(300)
        elif event.button() == Qt.MouseButton.RightButton:
            self.mostra_menu_contestuale(event.position().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if (event.position().toPoint() - self.drag_start_pos).manhattanLength() > 15:
                self.drag_ready = True
            if self.drag_ready:
                self.dragging = True
                delta = event.position().toPoint() - self.drag_start_pos
                self.move(self.pos() + delta)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hold_timer.stop()
            if not self.dragging and not self.drag_ready:
                self.esegui_applicazione()
                return
            if self.dragging:
                self.dragging = False
                main_window = self.window()
                if hasattr(main_window, 'gestisci_snap_libero'):
                    main_window.gestisci_snap_libero(self)
            self.drag_ready = False
        else:
            super().mouseReleaseEvent(event)

    def esegui_applicazione(self):
        if self.path == "close": self.window().close()
        elif self.path:
            try:
                os.startfile(self.path)
                self.window().close()
            except: pass

    def mostra_menu_contestuale(self, pos):
        menu = QMenu(self)
        
        menu_resize = menu.addMenu("resize tile")
        p = menu_resize.addAction("small")
        m = menu_resize.addAction("Medium")
        l = menu_resize.addAction("Large")
        g = menu_resize.addAction("big")
        
        rimuovi_azione = menu.addAction("unpin from Start")
        azione = menu.exec(self.mapToGlobal(pos))
        
        if azione == rimuovi_azione:
            if hasattr(self.window(), 'rimuovi_tile'):
                self.window().rimuovi_tile(self)
            return

        action_map = {p: (TileSize.PICCOLO, "PICCOLO"), m: (TileSize.MEDIO, "MEDIO"), l: (TileSize.LARGO, "LARGO"), g: (TileSize.GRANDE, "GRANDE")}
        if azione in action_map:
            self.grid_size, _ = action_map[azione]
            self.update_style()
            if hasattr(self.window(), 'recalcola_posizioni_evita_overlap'):
                self.window().recalcola_posizioni_evita_overlap()

class Windows8StartScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.tile_base_size = 65  
        self.spacing = 12
        self.tiles = []
        self.tutte_le_app_list = [] 
        self.widgets_all_apps = [] 
        self.saved_config = self.carica_configurazione_json()
        self.init_ui()

    def carica_configurazione_json(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def salva_configurazione_json(self):
        data_to_save = {}
        for tile in self.tiles:
            size_str = "MEDIO"
            for attr in dir(TileSize):
                if getattr(TileSize, attr) == tile.grid_size:
                    size_str = attr
                    break
            
            data_to_save[tile.name] = {
                "grid_x": tile.grid_x,
                "grid_y": tile.grid_y,
                "grid_size": size_str,
                "color": tile.base_color.name(),
                "path": tile.path,
                "lnk_path": tile.lnk_path
            }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Errore salvataggio: {e}")

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()
        
        try:
            accent_color = QApplication.palette().color(QPalette.ColorRole.Highlight).name()
        except:
            accent_color = "#0078D7"
        self.setStyleSheet(f"background-color: {accent_color};")

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # START PRINCIPALE
        self.start_screen_widget = QWidget(self)
        self.start_layout = QVBoxLayout(self.start_screen_widget)
        self.start_layout.setContentsMargins(0, 0, 0, 0)
        
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(60, 30, 60, 0)
        self.titolo = QLabel("Start", self)
        self.titolo.setStyleSheet("color: white; font-size: 48px; font-family: 'Segoe UI Light';")
        top_bar.addWidget(self.titolo)
        top_bar.addStretch()
        self.start_layout.addLayout(top_bar)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")

        self.griglia_widget = QWidget()
        self.griglia_widget.setStyleSheet("background: transparent;")
        self.griglia_widget.setMinimumWidth(6000) 
        self.scroll_area.setWidget(self.griglia_widget)
        self.start_layout.addWidget(self.scroll_area)

        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(60, 0, 60, 20)
        
        sys_layout = QHBoxLayout()
        sys_layout.setSpacing(10)
        
        btn_shutdown = QPushButton("Shutdown", self.start_screen_widget)
        btn_shutdown.setStyleSheet("QPushButton { background: rgba(0,0,0,0.2); color: white; border: 1px solid rgba(255,255,255,0.4); padding: 6px 12px; font-family: 'Segoe UI'; font-size: 13px; } QPushButton:hover { background: #cc0000; border-color: white; }")
        btn_shutdown.clicked.connect(lambda: os.system("shutdown /s /t 0"))
        
        btn_restart = QPushButton("Reset", self.start_screen_widget)
        btn_restart.setStyleSheet("QPushButton { background: rgba(0,0,0,0.2); color: white; border: 1px solid rgba(255,255,255,0.4); padding: 6px 12px; font-family: 'Segoe UI'; font-size: 13px; } QPushButton:hover { background: #ff8c00; border-color: white; }")
        btn_restart.clicked.connect(lambda: os.system("shutdown /r /t 0"))
        
        sys_layout.addWidget(btn_shutdown)
        sys_layout.addWidget(btn_restart)
        bottom_bar.addLayout(sys_layout)
        bottom_bar.addStretch()
        
        self.btn_tutte_app = QPushButton("⬇ all apps", self.start_screen_widget)
        self.btn_tutte_app.setStyleSheet("QPushButton { background: transparent; color: rgba(255,255,255,0.7); border: none; font-size: 16px; font-family: 'Segoe UI'; } QPushButton:hover { color: white; }")
        self.btn_tutte_app.clicked.connect(self.mostra_schermata_tutte_le_app)
        bottom_bar.addWidget(self.btn_tutte_app)
        bottom_bar.addStretch()
        bottom_bar.addSpacerItem(QSpacerItem(220, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))
        
        self.start_layout.addLayout(bottom_bar)
        self.main_layout.addWidget(self.start_screen_widget)

        # SCHERMATA "TUTTE LE APP"
        self.apps_screen_widget = QWidget(self)
        self.apps_screen_widget.setVisible(False)
        apps_layout = QVBoxLayout(self.apps_screen_widget)
        apps_layout.setContentsMargins(60, 40, 60, 40)
        
        apps_top_bar = QHBoxLayout()
        lbl_apps_titolo = QLabel("Applicazions", self)
        lbl_apps_titolo.setStyleSheet("color: white; font-size: 36px; font-family: 'Segoe UI Light';")
        apps_top_bar.addWidget(lbl_apps_titolo)
        apps_top_bar.addStretch()
        
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search application")
        self.search_bar.setStyleSheet("background: rgba(255,255,255,0.2); border: 2px solid transparent; color: white; padding: 8px; font-size: 15px; font-family: 'Segoe UI'; width: 280px;")
        
        # CORREZIONE ERRORE: Puntiamo al nome esatto del metodo definito sotto
        self.search_bar.textChanged.connect(self.filtra_ricerca_applicazioni)
        
        apps_top_bar.addWidget(self.search_bar)
        apps_layout.addLayout(apps_top_bar)
        
        self.apps_scroll = QScrollArea(self)
        self.apps_scroll.setWidgetResizable(True)
        self.apps_scroll.setStyleSheet("border: none; background: transparent;")
        self.apps_grid_container = QWidget()
        self.apps_grid = QGridLayout(self.apps_grid_container)
        self.apps_grid.setSpacing(12)
        self.apps_scroll.setWidget(self.apps_grid_container)
        apps_layout.addWidget(self.apps_scroll)
        
        btn_back = QPushButton("⬆ return to Start", self)
        btn_back.setStyleSheet("QPushButton { background: transparent; color: white; border: 1px solid white; padding: 8px 16px; font-family: 'Segoe UI'; } QPushButton:hover { background: rgba(255,255,255,0.2); }")
        btn_back.clicked.connect(self.mostra_schermata_start)
        apps_layout.addWidget(btn_back, 0, Qt.AlignmentFlag.AlignLeft)
        
        self.main_layout.addWidget(self.apps_screen_widget)

        self.carica_collegamenti_start_menu()
        self.ricostruisci_start_da_json()

    def carica_collegamenti_start_menu(self):
        percorsi_start = [
            os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), r"Microsoft\Windows\Start Menu\Programs"),
            os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
        ]
        
        visti = set()
        for directory in percorsi_start:
            if not os.path.exists(directory): continue
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(".lnk"):
                        nome_pulito = file.replace(".lnk", "")
                        path_completo = os.path.join(root, file)
                        if nome_pulito.lower() not in visti:
                            visti.add(nome_pulito.lower())
                            self.tutte_le_app_list.append({
                                "nome": nome_pulito,
                                "path": path_completo,
                                "lnk": path_completo
                            })

    def ricostruisci_start_da_json(self):
        if self.saved_config:
            for nome_app, info in self.saved_config.items():
                tile = Tile(nome_app, info["path"], lnk_path=info.get("lnk_path"), parent=self.griglia_widget, saved_data=info)
                self.tiles.append(tile)
        else:
            tile_desktop = Tile("Desktop", "close", parent=self.griglia_widget)
            tile_desktop.base_color = QColor("#008a00")
            tile_desktop.grid_size = TileSize.LARGO
            tile_desktop.update_style()
            self.tiles.append(tile_desktop)
            
        self.disponi_griglia_iniziale()

    def disponi_griglia_iniziale(self):
        riga, colonna = 0, 0
        for tile in self.tiles:
            if tile.grid_x != -1 and tile.grid_y != -1:
                continue
                
            w, h = tile.grid_size
            if riga + h > 8:
                riga = 0
                colonna += 4
            tile.grid_x = colonna
            tile.grid_y = riga
            riga += h
        self.riposiziona_tutte_le_tiles(inizializzazione=True)

    def riposiziona_tutte_le_tiles(self, inizializzazione=False):
        # Se è l'apertura iniziale, usiamo l'effetto Windows 8 a comparsa progressiva
        if inizializzazione:
            self.avvia_animazione_apertura_win8()
            return

        # Altrimenti mantiene il normale comportamento fluido per il drag & drop
        for tile in self.tiles:
            w_blocchi, h_blocchi = tile.grid_size
            target_x = 60 + tile.grid_x * (self.tile_base_size + self.spacing)
            target_y = 40 + tile.grid_y * (self.tile_base_size + self.spacing)
            target_w = w_blocchi * self.tile_base_size + (w_blocchi - 1) * self.spacing
            target_h = h_blocchi * self.tile_base_size + (h_blocchi - 1) * self.spacing
            self.anima_tile(tile, QRect(target_x, target_y, target_w, target_h))
        self.salva_configurazione_json()

    def avvia_animazione_apertura_win8(self):
        # Ordiniamo le piastrelle da sinistra a destra (in base a grid_x)
        tiles_ordinate = sorted(self.tiles, key=lambda t: (t.grid_x, t.grid_y))
        
        # Creiamo una lista nella classe per tenere in memoria le animazioni ed evitare che Python le cancelli
        if not hasattr(self, 'animazioni_attive'):
            self.animazioni_attive = []
        self.animazioni_attive.clear()
        
        for i, tile in enumerate(tiles_ordinate):
            w_blocchi, h_blocchi = tile.grid_size
            
            # Posizione finale esatta sulla griglia
            final_x = 60 + tile.grid_x * (self.tile_base_size + self.spacing)
            final_y = 40 + tile.grid_y * (self.tile_base_size + self.spacing)
            final_w = w_blocchi * self.tile_base_size + (w_blocchi - 1) * self.spacing
            final_h = h_blocchi * self.tile_base_size + (h_blocchi - 1) * self.spacing
            
            # CALCOLO PROSPETTICO (EFFETTO 3D): 
            # Partono il 40% più grandi (1.4), ma scalate verso il basso-destra per simulare la profondità d'impatto
            start_w = int(final_w * 1.4)
            start_h = int(final_h * 1.4)
            start_x = final_x + 50  # Scivolamento dall'esterno verso il centro
            start_y = final_y + 30  # Leggero sollevamento prospettico
            
            tile.setGeometry(start_x, start_y, start_w, start_h)
            tile.hide()
            
            # Creazione dell'animazione dinamica
            anim = QPropertyAnimation(tile, b"geometry", self)
            anim.setDuration(420)  # Tempo perfetto per dare peso alla "bomba"
            anim.setStartValue(QRect(start_x, start_y, start_w, start_h))
            anim.setEndValue(QRect(final_x, final_y, final_w, final_h))
            
            # Usiamo OutBack ma addolcito: crea il micro-rimbalzo finale che simula l'impatto sul display
            anim.setEasingCurve(QEasingCurve.Type.OutBack)
            
            self.animazioni_attive.append(anim)
            
            def avvia_singola_tile(t=tile, a=anim):
                t.show()
                a.start()
                
            # Ritardo a cascata fluido (30ms per un effetto "onda" continuo e non scattoso)
            QTimer.singleShot(i * 30, avvia_singola_tile)



            
        self.salva_configurazione_json()




    def gestisci_snap_libero(self, tile_trascinata):
        x_relativo = tile_trascinata.pos().x() - 60
        y_relativo = tile_trascinata.pos().y() - 40
        
        colonna_snap = max(0, round(x_relativo / (self.tile_base_size + self.spacing)))
        riga_snap = max(0, min(8, round(y_relativo / (self.tile_base_size + self.spacing))))
        
        tile_trascinata.grid_x = colonna_snap
        tile_trascinata.grid_y = riga_snap
        
        self.recalcola_posizioni_evita_overlap()

    def recalcola_posizioni_evita_overlap(self):
        matrice_occupati = set()
        for tile in sorted(self.tiles, key=lambda t: (t.grid_x, t.grid_y)):
            w, h = tile.grid_size
            conflitto = False
            for r in range(tile.grid_y, tile.grid_y + h):
                for c in range(tile.grid_x, tile.grid_x + w):
                    if (r, c) in matrice_occupati or r >= 9:
                        conflitto = True
                        break
                if conflitto: break
            
            if conflitto:
                trovato = False
                colonna = tile.grid_x
                while not trovato:
                    for riga in range(0, 9):
                        slot_libero = True
                        for r in range(riga, riga + h):
                            for c in range(colonna, colonna + w):
                                if (r, c) in matrice_occupati or r >= 9:
                                    slot_libero = False
                                    break
                            if not slot_libero: break
                        
                        if slot_libero:
                            tile.grid_x = colonna
                            tile.grid_y = riga
                            trovato = True
                            break
                    colonna += 1

            for r in range(tile.grid_y, tile.grid_y + h):
                for c in range(tile.grid_x, tile.grid_x + w):
                    matrice_occupati.add((r, c))
                    
        self.riposiziona_tutte_le_tiles()

    def rimuovi_tile(self, tile):
        if tile in self.tiles:
            self.tiles.remove(tile)
            tile.setParent(None)
            tile.deleteLater()
            self.recalcola_posizioni_evita_overlap()

    def aggiungi_nuova_tile_da_menu_applicazioni(self, app_info):
        # Evita duplicati sulla home
        if any(t.name == app_info["nome"] for t in self.tiles):
            self.mostra_schermata_start()
            return
            
        # Creiamo la nuova tile posizionandola temporaneamente in fondo a destra della griglia attuale
        # per dare un punto di partenza coerente al sistema di posizionamento
        max_x = max([t.grid_x for t in self.tiles], default=0)
        
        nuova_tile = Tile(app_info["nome"], app_info["path"], lnk_path=app_info["lnk"], parent=self.griglia_widget)
        nuova_tile.grid_x = max_x + 2 # La posiziona provvisoriamente a destra
        nuova_tile.grid_y = 0
        
        self.tiles.append(nuova_tile)
        
        # Questa funzione spingerà automaticamente la nuova piastrella nel primo slot 
        # veramente vuoto ed eviterà qualsiasi sovrapposizione fin dal primo istante
        self.recalcola_posizioni_evita_overlap()
        
        self.mostra_schermata_start()


    def anima_tile(self, tile, target_rect):
        tile.show()
        anim = QPropertyAnimation(tile, b"geometry", self)
        anim.setDuration(220)
        anim.setStartValue(tile.geometry())
        anim.setEndValue(target_rect)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        tile.current_animation = anim

    def mostra_schermata_tutte_le_app(self):
        self.search_bar.clear()
        self.rigenera_lista_all_apps()
        self.start_screen_widget.setVisible(False)
        self.apps_screen_widget.setVisible(True)

    def rigenera_lista_all_apps(self, filtro=""):
        for w in self.widgets_all_apps:
            w.setParent(None)
        self.widgets_all_apps.clear()
            
        riga, col = 0, 0
        provider = QFileIconProvider()
        for app in sorted(self.tutte_le_app_list, key=lambda x: x["nome"].lower()):
            if filtro and filtro.lower() not in app["nome"].lower():
                continue
                
            btn = QPushButton(app["nome"])
            btn.setStyleSheet("QPushButton { background: rgba(255,255,255,0.1); color: white; border: none; text-align: left; padding: 10px; font-family: 'Segoe UI'; font-size: 13px; } QPushButton:hover { background: white; color: black; }")
            
            file_info = QFileInfo(app["lnk"])
            icon = provider.icon(file_info)
            if not icon.isNull(): btn.setIcon(icon)
            
            # Nuova riga: il click sinistro ora avvia direttamente l'applicazione e chiude lo Start
            btn.clicked.connect(lambda checked, path=app["path"]: (os.startfile(path) if os.path.exists(path) else None, self.close()))

            
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, a=app: self.mostra_menu_aggiungi(pos, a))

            self.apps_grid.addWidget(btn, riga, col)
            self.widgets_all_apps.append(btn)
            
            col += 1
            if col > 3:
                col = 0
                riga += 1

    def mostra_menu_aggiungi(self, pos, app_info):
        sender_btn = self.sender()
        menu = QMenu(self)
        aggiungi_azione = menu.addAction("Aggiungi a Start")
        azione = menu.exec(sender_btn.mapToGlobal(pos))
        if azione == aggiungi_azione:
            self.aggiungi_nuova_tile_da_menu_applicazioni(app_info)

    def mostra_schermata_start(self):
        self.apps_screen_widget.setVisible(False)
        self.start_screen_widget.setVisible(True)

    # DEFINIZIONE CORRETTA DEL METODO DI RICERCA RICHIESTO AL PUNTO 290
    def filtra_ricerca_applicazioni(self, testo):
        self.rigenera_lista_all_apps(testo)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    start = Windows8StartScreen()
    sys.exit(app.exec())
