from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget, QHeaderView, QTableWidgetItem, QMessageBox, QDialog, QTextEdit,
    QInputDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QFileDialog, QAbstractItemView, QCheckBox, QSizePolicy, QComboBox, QMainWindow
    
    )
class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super(CustomTitleBar, self).__init__(parent)
        self.parent = parent  # Store a reference to the parent window
        self.mousePressed = False
        self.initUI()

    def initUI(self):
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Highlight)
        self.setFixedHeight(40)  

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  

        # Version title setup
        self.title = QLabel("Version 1.0.0", self)
        self.title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.title)

        # Tool buttons (minimize, maximize/restore, close)
        self.minimizeButton = QPushButton("─", self)
        self.maximizeButton = QPushButton("☐", self)
        self.closeButton = QPushButton("✕", self)
        self.helpButton = QPushButton("?", self)

        self.minimizeButton.clicked.connect(self.parent.showMinimized)
        self.maximizeButton.clicked.connect(self.toggleMaximizeRestore)
        self.closeButton.clicked.connect(self.parent.close)
        self.helpButton.clicked.connect(self.showHelp)

        # Add buttons to the layout
        for button in [self.helpButton, self.minimizeButton, self.maximizeButton, self.closeButton]:
            layout.addWidget(button)
            button.setFixedSize(35, 35)  # Example size, adjust as needed

        self.setLayout(layout)

    def defineToolButtons(self):
        self.minimize_button = QPushButton("ㅡ", self)
        self.minimize_button.clicked.connect(lambda: self.parent().showMinimized())

        self.maximize_button = QPushButton("☐", self)
        self.maximize_button.clicked.connect(self.toggleMaximizeRestore)

        self.close_button = QPushButton("✕", self)
        self.close_button.clicked.connect(lambda: self.parent().close())

        self.normal_button = QPushButton("🗗", self)
        self.normal_button.clicked.connect(lambda: self.parent().showNormal())
        self.normal_button.setVisible(False)

        self.help_Button = QPushButton("?", self)
        self.help_Button.clicked.connect(self.showHelp)
    

    def adjustHeight(self):
        max_height = max([widget.sizeHint().height() for widget in self.children() if isinstance(widget, QPushButton)])
        padding = 10  # Add some padding
        self.setFixedHeight(max_height + padding)

    def mousePressEvent(self, event):
        self.mousePressed = True
        self.mousePos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.mousePressed:
            # Calculate the difference and move the window
            diff = event.globalPos() - self.mousePos
            self.parent.move(self.parent.pos() + diff)
            self.mousePos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.mousePressed = False

    def mouseDoubleClickEvent(self, event):
        self.toggleMaximizeRestore()

    def toggleMaximizeRestore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximizeButton.setText("☐")
        else:
            self.parent.showMaximized()
            self.maximizeButton.setText("🗗")
    

    def showHelp(self):
        help_dialog = HelpDialog(self)
        help_dialog.exec_()


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        self.setWindowTitle("Help")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)

        help_text = """
이 프로그램은 API를 호출하고 API간 병합을 도와주는 프로그램 입니다.

기능:

- API 호출: API_URL과 서비스 키 값 그리고 여러 요청 변수들을 입력받아 사용자가 원하는 데이터를 호출하여 파일로 저장하게 도와줍니다.

- API & API 병합: 2개의 호출된 데이터를 바탕으로 사용자가 원하는 새 데이터를 만들어 줍니다. 조인은 같은 내용을 바탕으로 한 칼럼끼리만 가능합니다.

- 캐시 기반 데이터 호출 및 조인을 지원하여 최근 불러온 데이터는 더 빠르게 불러올 수 있습니다.

- 레지스트리 기반 데이터 저장을 지원합니다. sqlite파일이 제거되어도 최신 10개의 데이터는 유지됩니다.

사용 방법:

1. API 호출을 위해 먼저 API 주소, 서비스 키 값을 입력합니다.

2. 데이터 입력시 요청변수와 해당 값들을 추가/제거하여 입력합니다.

3. OpenAPI 호출 버튼을 눌러 API를 호출하고, 결과 데이터를 확인합니다.

4. 호출된 데이터를 저장하고 싶다면 원하는 형식을 선택하여 저장합니다.

API & API 병합을 위해:

1. 병합하고 싶은 데이터를 입력합니다. 이전에 호출 목록에서 저장된 데이터만 가능합니다.

2. 병합하고 싶은 데이터들간의 기준을 설정합니다.

3. 데이터 조인을 통해 새로운 데이터를 생성합니다.
"""
        
        self.help_text_edit = QTextEdit()
        self.help_text_edit.setText(help_text)
        self.help_text_edit.setReadOnly(True)
        
        layout.addWidget(self.help_text_edit)
        
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        
class ApiCall:

    def __init__(self, api_cache):
        self.ch = api_cache  # APICache 인스턴스를 인스턴스 변수로 저장합니다.

    def call_params(self, key, url, **kwargs):
        from urllib.parse import urlencode, urljoin
        params = {'dataType': 'XML', 'serviceKey': key}

        for v in kwargs.keys():
            params[v] = kwargs[v]
        query_string = urlencode(params)
        url = urljoin(url, '?' + query_string)
        return self.call_with_url(url)
        
    def call_with_url(self, url):
        import requests
        if url in self.ch.cache:
            return self.ch.cache[url]
        else:
            try:
                response =  requests.get(url)
                self.save_cache(response)
                return response
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(None, '에러', '호출 중 오류 발생! 응답 상태 코드: ' + str(response.status_code))
                return None
          
    def save_cache(self, response):
        # API 호출 결과를 캐시에 저장
        cache_key = response.url
        self.ch.set(cache_key, response)  # Cache the successful response
    
        
class RegistryManager:
    
    def __init__(self):
        self.reg_path = r"Software\Kwater\APIDOWNLOADER"
        self.backup_reg_path = r"Software\Kwater\APIDOWNLOADER\Backup"
        self.recent_entries_max = 10  # 최근 10개의 항목을 추적하기 위한 크기 지정
        self.load_settings()  # 인스턴스가 생성될 때 설정을 불러오도록 수정합니다.

    def load_settings(self):
        import winreg as reg
        """레지스트리에서 설정을 로드합니다. 키가 없으면 무시합니다."""
        settings = {}
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, self.reg_path, 0, reg.KEY_READ) as key:
                for i in range(self.recent_entries_max):
                    id_val, url_val = self.get_registry_value(key, f"ID_{i}"), self.get_registry_value(key, f"URL_{i}")
                    if id_val is not None and url_val is not None:
                        settings[f"ID_{i}"] = id_val
                        settings[f"URL_{i}"] = url_val
        except FileNotFoundError:
            print("레지스트리 경로를 찾을 수 없습니다.")
        except Exception as e:
            print(f"레지스트리 로딩 중 오류 발생: {e}")
        return settings
    
    def get_registry_value(self, key, name):
        import winreg as reg
        """레지스트리에서 값을 안전하게 조회합니다."""
        try:
            return reg.QueryValueEx(key, name)[0]
        except WindowsError:
            return None


    def save_settings(self, id_url_list):
        import winreg as reg
        """레지스트리에 설정을 저장합니다."""
        try:
            with reg.CreateKey(reg.HKEY_CURRENT_USER, self.reg_path) as key:
                # 새로운 값 맨 앞에 추가
                new_id, new_url = id_url_list[0]
                # 기존 값들을 뒤로 밀기
                for i in range(self.recent_entries_max - 1, 0, -1):
                    try:
                        prev_id, _ = reg.QueryValueEx(key, f"ID_{i-1}")
                        prev_url, _ = reg.QueryValueEx(key, f"URL_{i-1}")
                        reg.SetValueEx(key, f"ID_{i}", 0, reg.REG_SZ, prev_id)
                        reg.SetValueEx(key, f"URL_{i}", 0, reg.REG_SZ, prev_url)
                    except WindowsError:
                        # 이전 값이 없으면 이 위치에서 멈추고 반복을 중단
                        break

                # 새로운 값 맨 앞에 저장
                reg.SetValueEx(key, "ID_0", 0, reg.REG_SZ, new_id)
                reg.SetValueEx(key, "URL_0", 0, reg.REG_SZ, new_url)
        except Exception as e:
            print(f"Settings saving error: {e}")

    def recover_param_db_from_registry(self, db_path):
        """레지스트리 백업에서 param_db 파일의 데이터를 복구합니다."""
        import winreg as reg
        import os
        import sqlite3
        from urllib.parse import parse_qs, urlparse
        try:
            # 데이터베이스 파일 생성
            if not os.path.exists(db_path):
                open(db_path, 'a').close()
            
            db_connection = sqlite3.connect(db_path)
            db_cursor = db_connection.cursor()
            
            # 필요한 테이블 생성
            db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS URL_TB (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL
                )''')
            db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS PARAMS_TB (
                    id TEXT,
                    param TEXT,
                    FOREIGN KEY (id) REFERENCES URL_TB(id)
                )''')
            db_connection.commit()
            
            with reg.OpenKey(reg.HKEY_CURRENT_USER, self.reg_path, 0, reg.KEY_READ) as key:
                for i in range(10):
                    try:
                        id_val, _ = reg.QueryValueEx(key, f"ID_{i}")
                        url_val, _ = reg.QueryValueEx(key, f"URL_{i}")

                        # URL_TB에 데이터 삽입
                        db_cursor.execute("INSERT OR IGNORE INTO URL_TB (id, url) VALUES (?, ?)", (id_val, url_val))
                        
                        # URL에서 파라미터 추출하여 PARAMS_TB에 삽입
                        parsed_url = urlparse(url_val)
                        api_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
                        # API 기본 URL을 PARAMS_TB에 저장. 여기에서 api_url= 접두사를 제거합니다.
                        db_cursor.execute("INSERT INTO PARAMS_TB (id, param) VALUES (?, ?)", (id_val, api_url))
                        
                        query_params = parse_qs(parsed_url.query)
                        for param, values in query_params.items():
                            for value in values:
                                db_cursor.execute("INSERT INTO PARAMS_TB (id, param) VALUES (?, ?)", (id_val, f"{param}={value}"))
                        
                        db_connection.commit()
                    except WindowsError:
                        break
                        
            db_cursor.close()
            db_connection.close()
            QMessageBox.information(None, "복구 성공", "데이터베이스가 성공적으로 복구되었습니다.")
            
        except Exception as e:
            QMessageBox.critical(None, "복구 실패", f"데이터베이스 복구 중 오류 발생: {e}")

class ParameterSaver:
    db_connection = None
    db_cursor = None
    
    def __init__(self, id, url):
        self.id = id
        self.url = url

    def is_first_run():
        import os
        config_path = 'app_config.txt'
        if not os.path.exists(config_path):
            # 설정 파일이 없으면 첫 실행으로 간주
            with open(config_path, 'w') as f:
                f.write('run=true')
            return True
        return False
    
    
    @staticmethod
    def F_connectPostDB():
        import sqlite3
        import os
        db_path = 'params_db.sqlite'
        
        if not os.path.exists(db_path):
            if ParameterSaver.is_first_run():
                open(db_path, 'a').close()
                print("첫 설정: 데이터베이스 생성됨.")
            else:
                reply = QMessageBox.question(None, '데이터베이스 손상!', '데이터베이스 손상! 복구하시겠습니까?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.No:
                    secondaryReply = QMessageBox.question(None, '주의', '복구하지 않으면 저장된 데이터는 모두 소실됩니다. 정말 복구하지 않겠습니까?',
                                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if secondaryReply == QMessageBox.No:
                        ParameterSaver.recover_database(db_path)
                    else:
                        open(db_path, 'a').close()
                else:
                    ParameterSaver.recover_database(db_path)

        try:
            ParameterSaver.db_connection = sqlite3.connect(db_path)
            ParameterSaver.db_cursor = ParameterSaver.db_connection.cursor()
            ParameterSaver.ensure_database_schema()
        except sqlite3.Error as error:
            QMessageBox.critical(None, 'SQLite 연결 오류', "데이터베이스 연결에 실패했습니다.")
            return None, None

        return ParameterSaver.db_connection, ParameterSaver.db_cursor

    @staticmethod
    def recover_database(db_path):
        registry_manager = RegistryManager()
        try:
            registry_manager.recover_param_db_from_registry(db_path)
        except Exception as e:
            QMessageBox.critical(None, '복구 실패', f'복구 중 오류 발생: {e}')
            # 복구 실패 후에도 연결 시도를 계속하기 위해 빈 파일 생성
            open(db_path, 'a').close()
    
    def ensure_database_schema():
        # Assuming your schema creation logic is here
        ParameterSaver.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS URL_TB (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL
            )''')
        ParameterSaver.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS PARAMS_TB (
                id TEXT,
                param TEXT,
                FOREIGN KEY (id) REFERENCES URL_TB(id)
            )''')
        ParameterSaver.db_connection.commit()

    @staticmethod
    def F_ConnectionClose():
        if ParameterSaver.db_connection:
            ParameterSaver.db_cursor.close()
            ParameterSaver.db_connection.close()
            print("데이터베이스 연결 해제")
            ParameterSaver.db_connection = None
            ParameterSaver.db_cursor = None

    def save_parameters(self):
        from urllib.parse import parse_qs, urlparse
        import sqlite3
        # 데이터베이스 연결
        self.F_connectPostDB()
        if ParameterSaver.db_connection is None or ParameterSaver.db_cursor is None:
            return

        try:
            # 중복된 ID인지 확인
            ParameterSaver.db_cursor.execute("SELECT COUNT(*) FROM URL_TB WHERE id = ?", (self.id,))
            count = ParameterSaver.db_cursor.fetchone()[0]
            if count > 0:
                QMessageBox.warning(None, '중복된 값', '중복된 ID 값입니다.')
                return

            # URL_TB에 데이터 삽입
            ParameterSaver.db_cursor.execute("INSERT INTO URL_TB (id, url) VALUES (?, ?)", (self.id, self.url))
            ParameterSaver.db_connection.commit()

            # URL에서 파라미터 분리 및 PARAMS_TB에 삽입
            parsed_url = urlparse(self.url)
            api_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            ParameterSaver.db_cursor.execute("INSERT INTO PARAMS_TB (id, param) VALUES (?, ?)", (self.id, api_url))
            query_params = parse_qs(parsed_url.query)
            for param, values in query_params.items():
                for value in values:
                    ParameterSaver.db_cursor.execute("INSERT INTO PARAMS_TB (id, param) VALUES (?, ?)", (self.id, f"{param}={value}"))
            ParameterSaver.db_connection.commit()

            QMessageBox.information(None, '성공', 'URL 및 파라미터가 성공적으로 저장되었습니다.')
        except sqlite3.Error as e:
            QMessageBox.critical(None, '에러', f"데이터베이스 오류 발생: {e}")
        finally:
            self.F_ConnectionClose()

    def delete_row(self, id):
        import sqlite3
        try:
            # 선택된 ID의 행 전체 삭제
            connection, cursor = ParameterSaver.F_connectPostDB()
            if connection is not None and cursor is not None:
                cursor.execute("DELETE FROM URL_TB WHERE id = ?", (id,))
                cursor.execute("DELETE FROM PARAMS_TB WHERE id = ?", (id,))
                connection.commit()
                
                QMessageBox.information(None, '성공', '선택한 파라미터가 성공적으로 삭제되었습니다.')
            else:
                QMessageBox.critical(None, '에러', '데이터베이스 연결에 실패했습니다.')
        except sqlite3.Error as e:
            QMessageBox.critical(None, '에러', f"데이터베이스 오류 발생: {e}")
        finally:
            if connection:
                ParameterSaver.F_ConnectionClose()

    def get_params(self, id):
        import sqlite3
        try:
            connection, cursor = ParameterSaver.F_connectPostDB()
            if connection is not None and cursor is not None:
                cursor.execute("SELECT param FROM PARAMS_TB WHERE id = ?", (id,))
                rows = cursor.fetchall()
                return rows
            else:
                QMessageBox.critical(None, '에러', '데이터베이스 연결에 실패했습니다.')
                return []
        except sqlite3.Error as e:
            QMessageBox.critical(None, '에러', f"데이터베이스 오류 발생: {e}")
            return []
        finally:
            if connection:
                ParameterSaver.F_ConnectionClose()

    def load_parameter_list(param_table):
        import sqlite3
        connection, cursor = ParameterSaver.F_connectPostDB()
        if not connection or not cursor:
            return

        try:
            cursor.execute("SELECT * FROM URL_TB")
            rows = cursor.fetchall()
            num_rows = len(rows)
            num_cols = len(rows[0]) if num_rows > 0 else 0

            # 행과 열 수 설정
            param_table.setRowCount(num_rows)
            param_table.setColumnCount(num_cols)

            # 헤더 설정
            header_labels = ["ID", "URL"] 
            param_table.setHorizontalHeaderLabels(header_labels)

            # 데이터 추가
            for row_idx, row in enumerate(rows):
                for col_idx, col_value in enumerate(row):
                    item = QTableWidgetItem(str(col_value))
                    param_table.setItem(row_idx, col_idx, item)

            param_table.resizeColumnsToContents()

        except sqlite3.Error as e:
            QMessageBox.critical(None, '에러', f"데이터베이스 오류 발생: {e}")

        finally:
            ParameterSaver.F_ConnectionClose()



class PreviewUpdater:
    @staticmethod
    def show_preview(preview_table, data):
        # 미리보기 테이블 업데이트
        preview_table.setRowCount(data.shape[0])
        preview_table.setColumnCount(data.shape[1])
        preview_table.setHorizontalHeaderLabels(data.columns)

        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                item = QTableWidgetItem(str(data.iloc[row, col]))
                preview_table.setItem(row, col, item)

class APICache:
    def __init__(self, capacity=10):
        self.cache = {}
        self.capacity = capacity

    def get(self, key):
        return self.cache[key]
    
    def set(self, key, value):
        """API 호출 결과 캐시에 저장. 캐시가 가득 차면 가장 오래된 항목 제거"""
        if key not in self.cache:
            if len(self.cache) >= self.capacity:
                oldest_key = next(iter(self.cache))  # 가장 오래된 항목의 키를 가져옵니다.
                del self.cache[oldest_key]  # 가장 오래된 항목을 제거합니다.
        self.cache[key] = value
        
    def clear(self):
        """캐시 초기화"""
        self.cache.clear()
        self.keys.clear()

class ParameterViewer(QWidget):
    def __init__(self, widget_instance, api_cache, parent_widget_type, target_url_field="api_url1_edit"):
        super().__init__()
        self.api_cache = api_cache
        self.widget_instance = widget_instance
        self.parent_widget_type = parent_widget_type
        self.target_url_field = target_url_field  # 추가된 인자
        self.setWindowTitle('파라미터 목록')
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.param_table = QTableWidget()
        self.param_table.resizeColumnsToContents()
        self.param_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.param_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.param_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.param_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.load_parameters()
        layout.addWidget(self.param_table)

        confirm_button = QPushButton('파라미터 불러오기')
        confirm_button.clicked.connect(self.on_confirm_button_clicked)
        layout.addWidget(confirm_button)

        # Delete button
        delete_button = QPushButton('파라미터 삭제')
        delete_button.clicked.connect(self.on_delete_button_clicked)
        layout.addWidget(delete_button)

        self.setLayout(layout)
        self.resize(800, 600)
        self.param_table.itemDoubleClicked.connect(self.on_table_item_double_clicked)
    

    def load_parameters(self):
         ParameterSaver.load_parameter_list(self.param_table)

    def on_table_item_double_clicked(self):
        # 더블클릭 이벤트를 처리하기 위해 on_confirm_button_clicked 메서드 호출
        self.on_confirm_button_clicked()

    def on_delete_button_clicked(self):
        import sqlite3
        selected_items = self.param_table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            id_item = self.param_table.item(selected_row, 0)  # Assuming the first column contains the ID for deletion
            if id_item:
                id = id_item.text()
                try:
                    # Delete the parameter from the database
                    connection, cursor = ParameterSaver.F_connectPostDB()
                    if connection is not None and cursor is not None:
                        # Assuming 'URL_TB' table contains the 'id' column. Adjust if your schema is different.
                        cursor.execute("DELETE FROM URL_TB WHERE id = ?", (id,))
                        cursor.execute("DELETE FROM PARAMS_TB WHERE id = ?", (id,))
                        connection.commit()
                        
                        # After successful deletion from the database, remove the row from the table
                        self.param_table.removeRow(selected_row)
                        QMessageBox.information(None, '성공', '선택한 파라미터가 성공적으로 삭제되었습니다.')
                    else:
                        QMessageBox.critical(None, '에러', '데이터베이스 연결에 실패했습니다.')
                except sqlite3.Error as e:
                    QMessageBox.critical(None, '에러', f"데이터베이스 오류 발생: {e}")
                finally:
                    if connection:
                        ParameterSaver.F_ConnectionClose()
        else:
            QMessageBox.warning(None, '경고', '선택된 행이 없습니다.')



    def on_confirm_button_clicked(self):
        import sqlite3
        selected_items = self.param_table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            url_item = self.param_table.item(selected_row, 1)
            if url_item:
                url = url_item.text()

                if self.parent_widget_type == "MyWidget":
                    # Clear the preview table in MyWidget before setting new parameters
                    self.widget_instance.preview_table.clearContents()
                    self.widget_instance.preview_table.setRowCount(0)
                    self.widget_instance.preview_table.setColumnCount(0)

                    id_item = self.param_table.item(selected_row, 0)
                    if id_item:
                        id = id_item.text()

                    try:
                        connection, cursor = ParameterSaver.F_connectPostDB()
                        cursor.execute("SELECT param FROM PARAMS_TB WHERE id = ?", (id,))
                        rows = cursor.fetchall()
                        self.widget_instance.api_input.setText(rows[0][0])
                        
                        parameters = {}
                        for row in rows[2:]:
                            key, value = row[0].split("=", 1)
                            if key == 'serviceKey':
                                self.widget_instance.key_input.setText(value)
                            else:
                                parameters[key] = value

                        self.widget_instance.auto_add_parameters(parameters)

                    except sqlite3.Error as e:
                        print(f"Error: {e}")
                    finally:
                        ParameterSaver.F_ConnectionClose()
                elif self.parent_widget_type == "DataJoinerApp":
                    api_caller = ApiCall(self.api_cache)
                    if self.target_url_field == "api_url1_edit":
                        self.widget_instance.api_url1_edit.setText(url)
                        self.widget_instance.df1 = fetch_data(api_caller.call_with_url(url).text)
                        self.widget_instance.join_column1_combobox.clear()
                        self.widget_instance.join_column1_combobox.addItems(self.widget_instance.df1.columns)
                    elif self.target_url_field == "api_url2_edit":
                        self.widget_instance.api_url2_edit.setText(url)
                        self.widget_instance.df2 = fetch_data(api_caller.call_with_url(url).text)
                        self.widget_instance.join_column2_combobox.clear()
                        self.widget_instance.join_column2_combobox.addItems(self.widget_instance.df2.columns)
                self.close()
        else:
            QMessageBox.information(None, '알림', '선택된 행이 없습니다.')

class MyWidget(QWidget):
    def __init__(self, api_cache):
        import pandas as pd
        super().__init__()
        self.df_data = pd.DataFrame() # 데이터 프레임?!!?
        self.origin_data = None
        self.param_labels = []  # 파라미터 라벨 리스트
        self.param_inputs = []  # 파라미터 입력 필드 리스트
        self.param_names = []
        self.selected_params = []
        self.param_grid_row = 0  # 현재 그리드 레이아웃의 행 위치
        self.param_grid_col = 0  # 변경: 첫 번째 파라미터부터 첫 번째 열에 배치
        self.max_cols = 3  # 한 행에 최대 파라미터 개수
        self.setup()  # UI 설정
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.api_cache = api_cache

    def setup(self):
        self.setWindowTitle('API 다운로더')
        self.setGeometry(500, 500, 500, 500)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        main_layout = QVBoxLayout()  # 먼저 메인 레이아웃을 생성합니다.

        self.custom_title_bar = CustomTitleBar(self)  # 사용자 정의 타이틀 바 인스턴스 생성 및 추가
        main_layout.addWidget(self.custom_title_bar)  # 여기서 메인 레이아웃에 추가합니다.

        self.fixed_layout = QVBoxLayout()
        main_layout.addLayout(self.fixed_layout)

        self.api_label = QLabel('API URL')
        self.api_input = EnterLineEdit(self)
        self.add_param_to_layout(self.fixed_layout, self.api_label, self.api_input)
        self.api_input.setToolTip("API의 URL을 입력하세요.")

        self.key_label = QLabel('serviceKey')
        self.key_input = QLineEdit(self)  # EnterLineEdit를 QLineEdit으로 변경했습니다. EnterLineEdit 정의가 필요합니다.
        self.add_param_to_layout(self.fixed_layout, self.key_label, self.key_input)
        self.key_input.setToolTip("서비스 키를 입력하세요.")

        self.param_grid_layout = QGridLayout()
        main_layout.addLayout(self.param_grid_layout)
        self.param_grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.add_param_button = QPushButton('파라미터 추가', self)
        self.add_param_button.clicked.connect(self.add_parameter)
        self.add_param_button.setToolTip("요청 변수를 추가합니다.")

        self.remove_param_button = QPushButton('파라미터 삭제', self)
        self.remove_param_button.clicked.connect(self.remove_parameter)
        self.remove_param_button.setToolTip("요청 변수를 제거합니다.")

        self.download_params_button = QPushButton('호출 주소 저장', self)
        self.download_params_button.clicked.connect(self.download_parameters)

        self.show_params_button = QPushButton('호출 주소 목록', self)
        self.show_params_button.clicked.connect(self.show_parameters)
        self.show_params_button.setToolTip("저장된 데이터 url값을 확인하고 불러옵니다.")

        self.call_button = QPushButton('OpenAPI 호출', self)
        self.call_button.clicked.connect(self.api_call)
        self.call_button.setToolTip("입력된 API와 요청 변수를 바탕으로 API를 호출합니다.")


        self.download_button = QPushButton('API 호출정보 저장', self)
        self.download_button.clicked.connect(self.download_data)
        self.download_button.setToolTip("호출된 API data를 다운로드 합니다.")

        button_layout1 = QHBoxLayout()
        button_layout1.addWidget(self.show_params_button)
        button_layout1.addWidget(self.add_param_button)
        button_layout1.addWidget(self.remove_param_button)
        button_layout1.addWidget(self.download_params_button)

        button_layout2 = QHBoxLayout()
        button_layout2.addWidget(self.call_button)
        button_layout2.addWidget(self.download_button)

        main_layout.addLayout(button_layout1)
        main_layout.addLayout(button_layout2)

        self.preview_label = QLabel('미리보기')
        main_layout.addWidget(self.preview_label)
        self.preview_table = QTableWidget(self)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.preview_table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.preview_table)

        self.setLayout(main_layout)

    def onTextChanged(self):
        import pandas as pd
        # input 텍스트가 변경되면 api_data를 None으로 설정
        self.df_data = pd.DataFrame()
        self.origin_data = None
        self.preview_table.clearContents()  # 셀 내용 비우기
        self.preview_table.setRowCount(0)  # 행 수 초기화
        self.preview_table.setColumnCount(0)  # 열 수 초기화

    def add_param_to_layout(self, layout, label_widget, edit_widget, checkbox_widget=None):
        h_layout = QHBoxLayout()
        if checkbox_widget:
            checkbox_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            h_layout.addWidget(checkbox_widget)
            label_widget.setMinimumWidth(130)
            label_widget.setMaximumWidth(130)
        else:
            label_widget.setMinimumWidth(100)
            label_widget.setMaximumWidth(100)
        h_layout.addWidget(label_widget)
        h_layout.addWidget(edit_widget)
        #h_layout.setSpacing(10)
        #h_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        if isinstance(layout, QGridLayout):
            self.param_grid_layout.addLayout(h_layout, self.param_grid_row, self.param_grid_col)

            self.param_grid_col += 1
            if self.param_grid_col >= self.max_cols:
                self.param_grid_col = 0
                self.param_grid_row += 1
        else:
            self.fixed_layout.addLayout(h_layout)

    def add_parameter(self):
        param, ok = QInputDialog.getText(self, '파라미터 추가', '파라미터명:')
        if ok and param:
            param_name = param.replace(" ", "")
            
            if param_name in set(self.param_names):
                QMessageBox.warning(self, '중복된 파라미터명', '이미 존재하는 파라미터명입니다.')
                return
            
            display_name = (param_name[:12] + '...') if len(param_name) > 12 else param_name

            param_label = QLabel(display_name)
            param_input = EnterLineEdit(self)
            param_input.setMaximumWidth(200)
            param_input.setMinimumWidth(200)

            param_label.setToolTip(param_name)  # 툴팁에 전체 이름을 표시

            param_checkbox = QCheckBox()  # 체크박스 생성

            self.param_labels.append(param_label)
            self.param_inputs.append(param_input)
            self.param_names.append(param_name)
            self.selected_params.append(param_checkbox)
            self.add_param_to_layout(self.param_grid_layout, param_label, param_input, param_checkbox)
            param_input.setFocus()

    def auto_add_parameters(self, parameters):
        # First, clear any existing parameter widgets to avoid duplication.
        for param_label in self.param_labels:
            self.param_grid_layout.removeWidget(param_label)
            param_label.deleteLater()

        for param_input in self.param_inputs:
            self.param_grid_layout.removeWidget(param_input)
            param_input.deleteLater()

        for param_checkbox in self.selected_params:
            self.param_grid_layout.removeWidget(param_checkbox)
            param_checkbox.deleteLater()

        # Clear the lists after deleting the widgets
        self.param_labels.clear()
        self.param_inputs.clear()
        self.selected_params.clear()
        self.param_names.clear()

        # Reset the grid layout counters for re-adding widgets
        self.param_grid_row = 0
        self.param_grid_col = 0

        for key, value in parameters.items():
            param_label = QLabel(key)
            param_label.setMinimumWidth(130)
            param_label.setMaximumWidth(130)
            param_input = EnterLineEdit(self)
            param_input.setMaximumWidth(200)
            param_input.setMinimumWidth(200)
            param_input.setText(value)
            param_checkbox = QCheckBox()
            self.selected_params.append(param_checkbox)
            self.param_labels.append(param_label)
            self.param_inputs.append(param_input)
            self.param_names.append(key)
            self.add_param_to_layout(self.param_grid_layout, param_label, param_input, param_checkbox)    

        # After re-adding all parameters, refresh the layout to reflect the changes
        self.param_grid_layout.update()


    def remove_parameter(self):
        removed_indices = [i for i, checkbox in enumerate(self.selected_params) if checkbox.isChecked()]
        if not removed_indices:
            return  # No selected parameter to remove

        for index in sorted(removed_indices, reverse=True):
            # Remove widgets from layout and delete them
            self.param_grid_layout.removeWidget(self.selected_params[index])
            self.param_grid_layout.removeWidget(self.param_labels[index])
            self.param_grid_layout.removeWidget(self.param_inputs[index])
            self.selected_params[index].deleteLater()
            self.param_labels[index].deleteLater()
            self.param_inputs[index].deleteLater()
            # Remove items from lists
            del self.selected_params[index]
            del self.param_labels[index]
            del self.param_inputs[index]
            del self.param_names[index]

        self.rearrange_parameters()

    def rearrange_parameters(self):
        # 그리드 레이아웃 초기화
        self.param_grid_row = 0
        self.param_grid_col = 0

        # 현재 입력된 값들을 유지하기 위해 딕셔너리에 추가
        params = {}
        for label, input_widget in zip(self.param_labels, self.param_inputs):
            param_name = label.text()
            param_value = input_widget.text()
            params[param_name] = param_value

        # 기존의 파라미터를 유지하면서 새로운 파라미터 추가
        self.auto_add_parameters(params)

    def get_parameters(self):
        # 입력된 파라미터 수집
        params = {}
        for label, input_field in zip(self.param_labels, self.param_inputs):
            param_name = label.text()
            param_value = input_field.text()
            if param_name and param_value:
                params[param_name] = param_value
        return params

    def api_call(self):
        url = self.api_input.text().strip()
        key = self.key_input.text().strip()

        if not url:
            QMessageBox.critical(self, 'Error', "URL을 입력하세요.")
            return
        elif not key:
            QMessageBox.critical(self, 'Error', '서비스 키를 입력하세요.')
            return

        try:
            api_caller = ApiCall(self.api_cache)
            params = self.get_parameters()
            response = api_caller.call_params(key=key, url=url, **params)

            if response and response.status_code == 200:
                response_data = fetch_data(response.text)

                # Check if 'resultCode' exists and equals '00'
                if 'resultCode' in response_data.columns and any(response_data['resultCode'] == '00'):
                    QMessageBox.critical(self, 'Error', '불러올 데이터가 없음. 파라미터 값을 확인해주세요.')
                    return
                
                if not response_data.empty:
                    self.origin_data = response  # Save the original response
                    self.df_data = response_data  # Save the processed DataFrame
                    PreviewUpdater.show_preview(self.preview_table, self.df_data)
                else:
                    QMessageBox.critical(self, 'Error', '잘못된 API 호출. 호출된 데이터가 없음.')
            else:
                QMessageBox.critical(self, 'Error', f'서버 오류: {response.status_code}, API URL을 확인해주세요')
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'API 호출 중 오류 발생.')

    def download_parameters(self):

        if self.origin_data:
            id, ok = QInputDialog.getText(self, '저장명 입력', '저장명를 입력하세요')
            if ok:
                parameter_saver = ParameterSaver(id, self.origin_data.url)
                parameter_saver.save_parameters()
                try:
                        manager = RegistryManager()
                        id_url_list = [(id, self.origin_data.url)]
                        manager.save_settings(id_url_list)
                        settings = manager.load_settings()
                        print("레지스트리에 저장된 설정:", settings)
                except Exception as e:
                    QMessageBox.critical(None, '에러', f'레지스트리에 설정을 저장하는 도중 오류가 발생했습니다: {e}')
        else:
            QMessageBox.critical(None, '에러', '먼저 API를 호출하세요.')
            return
        
    def show_parameters(self):
        # Clear the preview table before showing the parameters
        self.preview_table.clearContents()
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        
        # Instantiate and show the ParameterViewer
        self.parameter_viewer = ParameterViewer(self, self.api_cache, "MyWidget")
        self.parameter_viewer.show()

    def download_data(self):
        if not self.df_data.empty:
            file_types = "CSV files (*.csv);;XML files (*.xml);;JSON files (*.json);;Excel files (*.xlsx)"
            file_path, file_type = QFileDialog.getSaveFileName(self, "Save File", "", file_types)
            if file_path:
                downloader = DataDownload(self.df_data)
                if file_type == "XML files (*.xml)":
                    downloader.save_xml(file_path)
                elif file_type == "JSON files (*.json)":
                    downloader.save_json(file_path)
                elif file_type == "CSV files (*.csv)":
                    downloader.save_csv(file_path)
                elif file_type == "Excel files (*.xlsx)":
                    downloader.save_xlsx(file_path)
        else:
            QMessageBox.critical(None, '에러', 'API 데이터를 가져오지 못했습니다.')
            
# Enter를 눌렀을 때 다음 위젯으로 넘어가는 QLineEdit 서브클래스
class EnterLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(EnterLineEdit, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.focusNextChild()
        else:
            super().keyPressEvent(event)

class DataDownload:
    def __init__(self, api_data):
        self.api_data = api_data # 데이터 프레임임!!!

    def save_xml(self, file_path):
        data = self.api_data.to_xml(index=False)
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(data)
            QMessageBox.information(None, '알림', 'XML 파일 저장 성공!')
        except Exception as e:
            QMessageBox.information(None, '알림', 'XML 파일 저장 실패!')
            print("XML 파일 저장 실패:", e)

    def save_csv(self, file_path):
        try:
            # UTF-8 인코딩으로 CSV 파일 저장, 인덱스는 제외하고, 각 레코드는 '\n'으로 종료
            self.api_data.to_csv(file_path, index=False, encoding='utf-8-sig')
            print("csv 파일 저장 성공")
        except Exception as e:
            print(f"csv 파일 저장 실패: {e}")

    def save_json(self, file_path):
        import json
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.api_data.to_dict(orient='records'), file, ensure_ascii=False, indent=4)
            print("JSON 파일 저장 성공")
        except Exception as e:
            print("JSON 파일 저장 실패:", e)
            
    def save_xlsx(self, file_path):
        import pandas as pd
        try:
        # 엑셀 파일로 저장할 때는 ExcelWriter 객체를 생성하여 사용
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                self.api_data.to_excel(writer, index=False)
            print("엑셀 파일 저장 성공")
        except Exception as e:
            print("엑셀 파일 저장 실패:", e)
                
def fetch_data(xml_data):
    import pandas as pd
    data = parse_xml_to_dict(xml_data)
    df = pd.DataFrame(data)
    return df

def parse_xml_to_dict(xml_data): 
    data_list = []
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml_data)
        if root.findall('.//item'):
            for item in root.findall('.//item'):
                data = {child.tag: child.text for child in item}
                data_list.append(data)
        else:
            data_dict = {}
            result_code = root.find(".//resultCode")
            if result_code is not None:
                data_dict['resultCode'] = result_code.text

            result_msg = root.find(".//resultMsg")
            if result_msg is not None:
                data_dict['resultMsg'] = result_msg.text
            data_list.append(data_dict)
    except ET.ParseError as e:
        print("XML 파싱 오류:", e)
    return data_list

class DataJoinerApp(QWidget):
    def __init__(self, api_cache):
        super().__init__()
        self.api_cache = api_cache
        self.df1 = None
        self.df2 = None
        self.joined_data = None
        self.initUI()

    def initUI(self):
        # Window flags are adjusted to allow for a custom title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(700, 700, 700, 700)

        # Layout for the entire widget
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Custom title bar is created and added first
        self.custom_title_bar = CustomTitleBar(self)
        layout.addWidget(self.custom_title_bar)

        # Input fields for API URLs
        self.api_url1_edit = QLineEdit(self)
        self.api_url1_edit.setReadOnly(True)
        self.select_button1 = QPushButton('URL1 선택', self)
        self.select_button1.clicked.connect(lambda: self.show_parameters('api_url1_edit'))

        self.api_url2_edit = QLineEdit(self)
        self.api_url2_edit.setReadOnly(True)
        self.select_button2 = QPushButton('URL2 선택', self)
        self.select_button2.clicked.connect(lambda: self.show_parameters('api_url2_edit'))

        # Adding the API URL fields and buttons to the layout
        layout.addWidget(QLabel('첫 번째 API 주소:'))
        layout.addWidget(self.api_url1_edit)
        layout.addWidget(self.select_button1)

        layout.addWidget(QLabel('두 번째 API 주소:'))
        layout.addWidget(self.api_url2_edit)
        layout.addWidget(self.select_button2)

        # Comboboxes for selecting the columns to join on
        self.join_column1_combobox = QComboBox(self)
        self.join_column2_combobox = QComboBox(self)

        layout.addWidget(QLabel('조인할 컬럼1 이름:'))
        layout.addWidget(self.join_column1_combobox)

        layout.addWidget(QLabel('조인할 컬럼2 이름:'))
        layout.addWidget(self.join_column2_combobox)


        self.join_button = QPushButton('데이터 조인', self)
        self.join_button.clicked.connect(self.join_data)
        layout.addWidget(self.join_button)

        self.result_table = QTableWidget(self)
        layout.addWidget(self.result_table)

        self.save_btn = QPushButton('파일 저장', self)
        self.save_btn.clicked.connect(self.download)
        layout.addWidget(self.save_btn)
        
        
        self.setLayout(layout)

    def show_parameters(self, target_field):
        self.parameter_viewer = ParameterViewer(self, self.api_cache, "DataJoinerApp", target_url_field=target_field)
        self.parameter_viewer.show()


    def join_data(self):
        import pandas as pd
        join_column1 = self.join_column1_combobox.currentText()
        join_column2 = self.join_column2_combobox.currentText()

        if not self.api_url1_edit.text():
            QMessageBox.warning(self, '경고', '첫 번째 API URL을(를) 선택해야 합니다!')
            return
        elif not self.api_url2_edit.text():
            QMessageBox.warning(self, '경고', '두 번째 API URL을(를) 선택해야 합니다!')
            return
        elif not self.join_column1_combobox.currentText():
            QMessageBox.warning(self, '경고', '첫 번째 API URL을(를) 선택해야 합니다!')
            return
        elif not self.join_column1_combobox.currentText():
            QMessageBox.warning(self, '경고', '첫 번째 API URL을(를) 선택해야 합니다!')
            return
        
        # self.df1 = fetch_data(api_url_1)
        # self.df2 = fetch_data(api_url_2)

        if self.df1 is None or self.df2 is None:
            QMessageBox.critical(self, '오류', '데이터를 가져오는 데 실패했습니다. API URL을 확인해주세요.')
            return

        if join_column1 in self.df1.columns and join_column2 in self.df2.columns:
            self.joined_data = pd.merge(self.df1, self.df2, left_on=join_column1, right_on=join_column2, how='inner')
            self.show_data_in_table(self.joined_data)
        else:
            QMessageBox.warning(self, '오류', '조인할 컬럼이 누락되었거나 잘못되었습니다.')
            self.result_table.clear()  # 테이블 초기화
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(0)

    def show_data_in_table(self, data):
        self.result_table.setRowCount(data.shape[0])
        self.result_table.setColumnCount(data.shape[1])
        self.result_table.setHorizontalHeaderLabels(data.columns)

        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                item = QTableWidgetItem(str(data.iloc[row, col]))
                self.result_table.setItem(row, col, item)

    def download(self):
        data = self.joined_data

        if not data.empty:
            file_types = "CSV files (*.csv);;XML files (*.xml);;JSON files (*.json);;Excel files (*.xlsx)"
            file_path, file_type = QFileDialog.getSaveFileName(self, "Save File", "", file_types)
            if file_path:
                downloader = DataDownload(data)
                if file_type == "XML files (*.xml)":
                    downloader.save_xml(file_path)
                elif file_type == "JSON files (*.json)":
                    downloader.save_json(file_path)
                elif file_type == "CSV files (*.csv)":
                    downloader.save_csv(file_path)
                elif file_type == "Excel files (*.xlsx)":
                    downloader.save_xlsx(file_path)
        else:
            QMessageBox.critical(None, '에러', 'API 데이터를 가져오지 못했습니다.')

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.api_cache = APICache()

        self.registry_manager = RegistryManager()
        self.settings = self.registry_manager.load_settings()

        # Initially set these to None to indicate they're not loaded yet
        self.myWidgetApp = None
        self.dataJoiner = None

        self.initUI()
        # self.setStyleSheet("QMainWindow {background: 'white';}")
    
    def initUI(self):
        self.setWindowTitle('API')
        self.setGeometry(600, 600, 600, 600)
        
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        hbox = QVBoxLayout()
        btn1 = QPushButton('API 호출', centralWidget)
        btn1.clicked.connect(self.showMyWidgetApp)
        
        btn2 = QPushButton('API && API 병합', centralWidget)
        btn2.clicked.connect(self.showDataJoinerApp)
        
        hbox.addWidget(btn1)
        hbox.addWidget(btn2)
        
        centralWidget.setLayout(hbox)
        
        # Custom title bar setup
        self.custom_title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.custom_title_bar)


    def showMyWidgetApp(self):
        if self.myWidgetApp is None:  # MyWidget 인스턴스가 없으면 생성
            self.myWidgetApp = MyWidget(self.api_cache)  # 이 부분을 MyWidget()으로 수정
        self.myWidgetApp.show()  # MyWidget 표시

    def showDataJoinerApp(self):
        if self.dataJoiner is None:  # DataJoinerApp 인스턴스가 없으면 생성
            self.dataJoiner = DataJoinerApp(self.api_cache)
        self.dataJoiner.show()  # DataJoinerApp 표시

if __name__ == '__main__':
    import sys
    app = QApplication.instance()  # 기존 인스턴스 확인
    if not app:  # 인스턴스가 없을 경우 새로 생성
        app = QApplication(sys.argv)
    mainApp = MainApp()  # MainApp 인스턴스 생성
    mainApp.show()
    sys.exit(app.exec_())