import re
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from device import Device


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Main widgets
        self.central_widget = QtWidgets.QWidget(self)
        self.menubar = QtWidgets.QMenuBar(self)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.assembly_code = QtWidgets.QPlainTextEdit(self.central_widget)
        self.memory_dump_window = QtWidgets.QMainWindow(self)

        # Menu widgets
        self.menuProgram = QtWidgets.QMenu(self.menubar)
        self.menuMachine = QtWidgets.QMenu(self.menubar)

        # Action widgets
        self.actionNew = QtWidgets.QAction(self)
        self.actionLoad = QtWidgets.QAction(self)
        self.actionSave_as = QtWidgets.QAction(self)
        self.actionAssemble = QtWidgets.QAction(self)
        self.actionExit = QtWidgets.QAction(self)
        self.actionSet_breakpoint = QtWidgets.QAction(self)
        self.actionSet_machine_cycle_delay = QtWidgets.QAction(self)
        self.actionClear_terminal = QtWidgets.QAction(self)
        self.actionMemory_dump = QtWidgets.QAction(self)

        # List widgets
        self.machine_code = QtWidgets.QListWidget(self.central_widget)
        self.output = QtWidgets.QListWidget(self.central_widget)
        self.registers_table = QtWidgets.QListWidget(self.central_widget)
        self.mapped_symbols = QtWidgets.QListWidget(self.central_widget)
        self.memory_line_list = QtWidgets.QListWidget(self.memory_dump_window)

        # Buttons
        self.stop_machine = QtWidgets.QPushButton(self.central_widget)
        self.reset_machine = QtWidgets.QPushButton(self.central_widget)
        self.do_one_step = QtWidgets.QPushButton(self.central_widget)
        self.run_assembly = QtWidgets.QPushButton(self.central_widget)
        self.assemble_button = QtWidgets.QPushButton(self.central_widget)

        # Labels
        self.program_label = QtWidgets.QLabel(self.central_widget)
        self.machine_code_label = QtWidgets.QLabel(self.central_widget)
        self.label_3 = QtWidgets.QLabel(self.central_widget)
        self.symbol_table_label = QtWidgets.QLabel(self.central_widget)
        self.registers_label = QtWidgets.QLabel(self.central_widget)
        self.cycle_label = QtWidgets.QLabel(self.central_widget)
        self.label_value = QtWidgets.QLabel(self.central_widget)

        # Setup
        self.setup_ui()
        self.retranslate_ui()
        self.connect_actions()

        # Executors
        self._stop = False
        self._reset = False
        self._assembled = False
        self._running = False
        self._stepping = False
        self._current_step = 0
        self._current_id = None
        self._breakpoint_value = None
        self._delay = 0.05
        self.device = Device()

    def setup_ui(self):
        # Main window
        self.setObjectName("MainWindow")
        self.setFixedSize(1200, 650)

        self.setup_main_widgets_ui()
        self.setup_lists_ui()
        self.setup_labels_ui()
        self.setup_buttons_ui()
        self.setup_actions_ui()

        self.setCentralWidget(self.central_widget)

    def setup_labels_ui(self):
        segoe_font = QtGui.QFont()
        segoe_font.setFamily("Segoe UI")
        segoe_font.setPointSize(14)
        segoe_font.setBold(False)
        segoe_font.setWeight(50)

        consolas_font = QtGui.QFont()
        consolas_font.setFamily("Consolas")
        consolas_font.setPointSize(11)

        self.program_label.setGeometry(QtCore.QRect(10, 10, 101, 31))
        self.program_label.setFont(segoe_font)

        self.machine_code_label.setGeometry(QtCore.QRect(430, 10, 291, 31))
        self.machine_code_label.setFont(segoe_font)

        self.label_3.setGeometry(QtCore.QRect(826, 10, 55, 16))
        self.label_3.setFont(segoe_font)

        self.symbol_table_label.setGeometry(QtCore.QRect(760, 10, 151, 31))
        self.symbol_table_label.setFont(segoe_font)

        self.registers_label.setGeometry(QtCore.QRect(1040, 10, 111, 31))
        self.registers_label.setFont(segoe_font)

        self.cycle_label.setGeometry(QtCore.QRect(1055, 305, 81, 31))
        self.cycle_label.setFont(segoe_font)

        self.label_value.setGeometry(QtCore.QRect(1083, 345, 10, 21))
        self.label_value.setFont(consolas_font)

    def setup_buttons_ui(self):
        segoe_font = QtGui.QFont()
        segoe_font.setFamily("Segoe UI")
        segoe_font.setPointSize(12)

        self.assemble_button.setGeometry(QtCore.QRect(1000, 380, 191, 38))
        self.assemble_button.setFont(segoe_font)

        self.run_assembly.setGeometry(QtCore.QRect(1000, 423, 191, 38))
        self.run_assembly.setFont(segoe_font)

        self.do_one_step.setGeometry(QtCore.QRect(1000, 467, 191, 38))
        self.do_one_step.setFont(segoe_font)

        self.stop_machine.setGeometry(QtCore.QRect(1000, 510, 191, 38))
        self.stop_machine.setFont(segoe_font)

        self.reset_machine.setGeometry(QtCore.QRect(1000, 553, 191, 38))
        self.reset_machine.setFont(segoe_font)

    def setup_lists_ui(self):
        consolas_font = QtGui.QFont()
        consolas_font.setFamily("Consolas")
        consolas_font.setPointSize(11)

        self.machine_code.setGeometry(QtCore.QRect(430, 50, 290, 350))
        self.machine_code.setFont(consolas_font)
        self.machine_code.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.machine_code.setStyleSheet("""
            QListWidget::item:selected{
                background-color: #71d6ff;
            }
        """)
        self.machine_code.itemDoubleClicked.connect(self.set_item_breakpoint)

        self.mapped_symbols.setGeometry(QtCore.QRect(740, 50, 240, 350))
        self.mapped_symbols.setFont(consolas_font)
        self.mapped_symbols.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.output.setGeometry(QtCore.QRect(10, 410, 970, 181))
        self.output.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.output.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.memory_line_list.setGeometry(QtCore.QRect(15, 10, 685, 450))
        self.memory_line_list.setFont(consolas_font)
        self.memory_line_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.memory_line_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.memory_line_list.setAutoScroll(False)

        self.registers_table.setGeometry(QtCore.QRect(1000, 50, 191, 251))
        self.registers_table.setFont(consolas_font)
        self.registers_table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.registers_table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.registers_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.registers_table.setAutoScroll(False)
        self.registers_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.registers_table.setProperty("showDropIndicator", True)
        self.registers_table.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.registers_table.setAlternatingRowColors(True)
        self.registers_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        for i in range(10):
            self.registers_table.addItem(QtWidgets.QListWidgetItem())

    def setup_actions_ui(self):
        # Program
        self.menuProgram.addAction(self.actionNew)
        self.menuProgram.addAction(self.actionLoad)
        self.menuProgram.addAction(self.actionSave_as)

        self.menuProgram.addSeparator()
        self.menuProgram.addAction(self.actionAssemble)
        self.menuProgram.addSeparator()

        self.menuProgram.addAction(self.actionExit)

        # Machine
        self.menuMachine.addAction(self.actionSet_breakpoint)
        self.menuMachine.addAction(self.actionSet_machine_cycle_delay)

        self.menuMachine.addSeparator()
        self.menuMachine.addAction(self.actionClear_terminal)
        self.menuMachine.addSeparator()

        self.menuMachine.addAction(self.actionMemory_dump)
        self.menubar.addAction(self.menuProgram.menuAction())
        self.menubar.addAction(self.menuMachine.menuAction())

    def setup_main_widgets_ui(self):
        self.assembly_code.setGeometry(QtCore.QRect(10, 50, 400, 350))
        self.assembly_code.setAcceptDrops(True)
        self.assembly_code.dropEvent = self.drop_event

        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 29))
        self.setMenuBar(self.menubar)

        self.setStatusBar(self.statusbar)

        self.memory_dump_window.setFixedSize(715, 470)

    def retranslate_ui(self):
        self.setWindowTitle("Viking")
        self.memory_dump_window.setWindowTitle('Memory dump')

        _translate = QtCore.QCoreApplication.translate

        self.retranslate_menu_ui(_translate)
        self.retranslate_actions_ui(_translate)
        self.retranslate_lists_ui()
        self.retranslate_buttons_ui(_translate)
        self.retranslate_labels_ui(_translate)

    def retranslate_labels_ui(self, translate):
        self.program_label.setText(
            translate("MainWindow",
                      "<html><head/><body><p>Program<span style=\" font-weight:600;\">:</span></p></body></html>"))

        self.machine_code_label.setText(
            translate("MainWindow",
                      "<html><head/><body><p>Object code / disassembly<span style=\" font-weight:600;\">"
                      ":</span></p></body></html>"))

        self.symbol_table_label.setText(
            translate("MainWindow",
                      "<html><head/><body><p>Symbol table<span style=\" font-weight:600;\">:</span></p></body></html>"))

        self.registers_label.setText(
            translate("MainWindow",
                      "<html><head/><body><p>Registers<span style=\" font-weight:600;\">:</span></p></body></html>"))

        self.label_value.setText(translate("MainWindow", "0"))

        self.cycle_label.setText(
            translate("MainWindow",
                      "<html><head/><body><p>Cycle<span style=\" font-weight:600;\">:</span></p></body></html>"))

    def retranslate_menu_ui(self, translate):
        self.menuProgram.setTitle(translate("MainWindow", "Program"))
        self.menuMachine.setTitle(translate("MainWindow", "Machine"))

    def retranslate_actions_ui(self, translate):
        self.actionNew.setText(translate("MainWindow", "New"))
        self.actionNew.setShortcut(translate("MainWindow", "Ctrl+N"))

        self.actionLoad.setText(translate("MainWindow", "Load"))
        self.actionLoad.setShortcut(translate("MainWindow", "Ctrl+L"))

        self.actionSave_as.setText(translate("MainWindow", "Save as"))
        self.actionSave_as.setShortcut(translate("MainWindow", "Ctrl+S"))

        self.actionAssemble.setText(translate("MainWindow", "Assemble"))
        self.actionAssemble.setShortcut(translate("MainWindow", "Ctrl+K"))

        self.actionExit.setText(translate("MainWindow", "Exit"))
        self.actionExit.setShortcut(translate("MainWindow", "Ctrl+Del"))

        self.actionSet_breakpoint.setText(translate("MainWindow", "Set breakpoint"))

        self.actionSet_machine_cycle_delay.setText(translate("MainWindow", "Set machine cycle delay"))
        self.actionSet_machine_cycle_delay.setShortcut(translate("MainWindow", "Ctrl+D"))

        self.actionClear_terminal.setText(translate("MainWindow", "Clear terminal"))

        self.actionMemory_dump.setText(translate("MainWindow", "Memory dump"))
        self.actionMemory_dump.setShortcut(translate("MainWindow", "Ctrl+M"))

    def retranslate_lists_ui(self):
        self.registers_table.setSortingEnabled(False)
        for i in range(1, 5):
            self.registers_table.item(i).setText(f"r{i}      : 0000")

        self.registers_table.item(0).setText("r0 (at) : 0000")
        self.registers_table.item(5).setText("r5 (sr) : 0000")
        self.registers_table.item(6).setText("r6 (lr) : 0000")
        self.registers_table.item(7).setText("r7 (sp) : dffe")
        self.registers_table.item(9).setText("PC      : 0000")

        self.output.setSortingEnabled(False)

    def retranslate_buttons_ui(self, translate):
        self.stop_machine.setText(translate("MainWindow", "Stop"))
        self.reset_machine.setText(translate("MainWindow", "Reset"))
        self.do_one_step.setText(translate("MainWindow", "Step"))
        self.run_assembly.setText(translate("MainWindow", "Run"))
        self.assemble_button.setText(translate("MainWindow", 'Assemble'))

    def drop_event(self, e: QtGui.QDropEvent) -> None:
        with open(str(e.mimeData().text())[8:], 'r') as file:
            self.assembly_code.setPlainText(file.read())

    def connect_actions(self):
        self.run_assembly.clicked.connect(self.run)
        self.do_one_step.clicked.connect(self.do_step)
        self.actionNew.triggered.connect(self.assembly_code.clear)
        self.actionAssemble.triggered.connect(self.assemble)
        self.actionClear_terminal.triggered.connect(self.clear_terminal)
        self.actionSet_machine_cycle_delay.triggered.connect(self.set_machine_cycle_delay)
        self.actionSet_breakpoint.triggered.connect(self.set_breakpoint)
        self.actionMemory_dump.triggered.connect(self.show_memory_dump)
        self.actionLoad.triggered.connect(self.open_file)
        self.actionSave_as.triggered.connect(self.save_file)
        self.actionExit.triggered.connect(self.quit_app)
        self.reset_machine.clicked.connect(self.reset)
        self.stop_machine.clicked.connect(self.stop)

    def open_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "Asm Files (*.asm)",
                                                             options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.assembly_code.setPlainText(file.read())

    def save_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                             "Asm Files (*.asm)", options=options)
        if file_name:
            with open(file_name, 'w') as file:
                file.write(self.assembly_code.toPlainText())

    def set_machine_cycle_delay(self):
        segoe_font = QtGui.QFont()
        segoe_font.setFamily("Segoe UI")
        segoe_font.setPointSize(10)
        segoe_font.setBold(False)
        segoe_font.setWeight(50)

        input_dialog = QtWidgets.QInputDialog(self)
        input_dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
        input_dialog.setFixedSize(300, 700)
        input_dialog.setFont(segoe_font)

        input_dialog.setWindowTitle('Machine delay')
        input_dialog.setLabelText('Enter the new delay value:')

        ok = input_dialog.exec()

        if ok:
            self._delay = float(input_dialog.textValue())

    def set_breakpoint(self):
        segoe_font = QtGui.QFont()
        segoe_font.setFamily("Segoe UI")
        segoe_font.setPointSize(10)
        segoe_font.setBold(False)
        segoe_font.setWeight(50)

        input_dialog = QtWidgets.QInputDialog(self)
        input_dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
        input_dialog.setFixedSize(300, 700)
        input_dialog.setFont(segoe_font)

        input_dialog.setWindowTitle('Breakpoint')
        input_dialog.setLabelText('Enter the hex address to set breakpoint:')
        ok = input_dialog.exec()

        if ok:
            self._breakpoint_value = input_dialog.textValue()

    def set_item_breakpoint(self, item):
        self._breakpoint_value = item.text()[5:9]
        segoe_font = QtGui.QFont()
        segoe_font.setFamily("Segoe UI")
        segoe_font.setPointSize(10)
        segoe_font.setBold(False)
        segoe_font.setWeight(50)

        warning = QtWidgets.QMessageBox(self)
        warning.setFixedSize(340, 200)
        warning.setFont(segoe_font)

        warning.setWindowTitle('Breakpoint')
        warning.setText(f'Breakpoint set to address "{self._breakpoint_value}"')
        warning.exec()

    def show_memory_dump(self):
        self.memory_dump_window.show()

    def clear_terminal(self):
        self.output.clear()

    def reset(self):
        self._stop = True
        self._stepping = False
        self._current_step = 0
        self._current_id = None
        self.device.reset()
        self.machine_code.clear()
        self.mapped_symbols.clear()
        self.memory_line_list.clear()
        self.label_value.setText('0')
        self.label_value.setGeometry(QtCore.QRect(1083, 345, 10, 21))
        self._assembled = False

    def stop(self):
        self._stop = True

    def quit_app(self):
        raise SystemExit

    def assemble(self):
        self._assembled = True
        first_item = QtWidgets.QListWidgetItem('Assembling...')
        self.output.addItem(first_item)
        self.machine_code.clear()
        self.mapped_symbols.clear()

        program = self.get_program()

        # No program given
        if not program:
            if not self.set_output_item_text(first_item):
                first_item = QtWidgets.QListWidgetItem('Assembling...')
                self.output.addItem(first_item)
            self.output.addItem(QtWidgets.QListWidgetItem())
            self.output.scrollToItem(first_item, QtWidgets.QAbstractItemView.PositionAtTop)
            return

        symbols, program_info, codes = self.device.generate_symbols(program)

        self.set_output_item_text(first_item)

        # Output the machine_code
        for machine_code in codes:
            item = QtWidgets.QListWidgetItem(machine_code)
            self.machine_code.addItem(item)

        # Output the information about the program
        for line in program_info:
            self.output.addItem(QtWidgets.QListWidgetItem(line))

        for symbol in symbols:
            self.mapped_symbols.addItem(QtWidgets.QListWidgetItem(symbol))

        # Output the result of the program
        self.output.addItem(QtWidgets.QListWidgetItem())
        self.output.scrollToItem(first_item, QtWidgets.QAbstractItemView.PositionAtTop)

    def run(self):
        if not self._assembled:
            self.assemble()

        self._running = True

        self._stop = False
        self._reset = False

        while 1:
            if not self.do_step():
                break

            if self._stop:
                if self._reset:
                    self.device.reset()
                    self.machine_code.clear()
                    self.mapped_symbols.clear()
                    self.label_value.setText('0')
                    self.label_value.setGeometry(QtCore.QRect(1083, 345, 10, 21))
                    self._assembled = False
                break

        self._stop = False
        self._reset = False
        self._running = False

    def do_step(self):
        if not self._assembled:
            self.assemble()

        step, result = self.device.get_step()

        message = getattr(step, 'message')

        if result is None and self._current_step == 0:
            item = QtWidgets.QListWidgetItem('No program written.')
            self.output.addItem(item)
            self.output.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
            self._assembled = False
            return False

        elif result is None and not message:
            item = QtWidgets.QListWidgetItem('No more steps available.')
            self.output.addItem(item)
            self.output.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
            return False

        if self._current_step == 0:
            item = QtWidgets.QListWidgetItem()
            self._current_id = id(item)
            self.output.addItem(item)
            self.output.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)

        context = getattr(step, 'context')
        self.update_registers(context)

        memory = getattr(step, 'memory')
        self.update_memory_dump(memory)

        instruction = getattr(step, 'instruction')
        cycle = getattr(step, 'cycle')
        output = getattr(step, 'output')
        message = getattr(step, 'message')

        if len(str(cycle)) > len(self.label_value.text()):
            geo = self.label_value.geometry()
            self.label_value.setGeometry(QtCore.QRect(geo.x() - 5, 345, geo.width() + 10, 21))

        self.label_value.setText(str(cycle))
        if self._current_step == 1:
            self.update_machine_code(str(instruction)[2:].rjust(4, '0'), True)
        else:
            self.update_machine_code(str(instruction)[2:].rjust(4, '0'), False)

        if message:
            item = QtWidgets.QListWidgetItem(message)
            self.output.addItem(item)
            self.output.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
            return False

        if output:
            if not self.set_output_item_text(self._current_id, output):
                item = QtWidgets.QListWidgetItem(output)
                self._current_id = id(item)
                self.output.addItem(item)
                self.output.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)

        if self._breakpoint_value == str(instruction)[2:].rjust(4, '0'):
            return False

        self.wait()
        self._current_step += 1

        return True

    def update_machine_code(self, current_instruction, first):
        idx = 0
        unselected = False
        while 1:
            if self.machine_code.item(idx) is None:
                break

            if re.findall(current_instruction, self.machine_code.item(idx).text()):
                self.machine_code.item(idx).setSelected(True)
                break

            elif self.machine_code.item(idx).isSelected():
                self.machine_code.item(idx).setSelected(False)
                unselected = True

            idx += 1

        if not unselected and not first:
            idx += 1
            while not unselected:
                if self.machine_code.item(idx) is None:
                    break

                if self.machine_code.item(idx).isSelected():
                    self.machine_code.item(idx).setSelected(False)
                    unselected = True

                idx += 1

    def update_registers(self, registers):
        hex_registers = []
        for val in registers:
            hex_registers.append(hex(int(val))[2:].rjust(4, '0'))

        idx = 0
        for i in range(10):
            if i == 8:
                continue

            self.registers_table.item(i).setText(self.registers_table.item(i).text()[:-4] + hex_registers[idx])
            idx += 1

    def update_memory_dump(self, memory):
        k = 0
        self.memory_line_list.clear()
        while k < len(memory) * 2:
            dump_line = str(self.to_hex(k)) + ': '
            l = 0
            while l < 8:
                dump_line = dump_line + self.to_hex(memory[int(k / 2) + l]) + ' '
                l += 1
            dump_line += '|'
            l = 0

            while l < 8:
                ch1 = memory[int(k / 2) + l] >> 8
                ch2 = memory[int(k / 2) + l] & 0xff
                if 32 <= ch1 <= 126:
                    dump_line += chr(ch1)
                else:
                    dump_line += '.'
                if 32 <= ch2 <= 126:
                    dump_line += chr(ch2)
                else:
                    dump_line += '.'
                l += 1

            dump_line += '|'
            item = QtWidgets.QListWidgetItem()
            item.setText(dump_line)
            self.memory_line_list.addItem(item)
            k += 16

    def set_output_item_text(self, item_id, text=' Done.'):
        idx = 0
        while 1:
            if self.output.item(idx) is None:
                return False

            if str(item_id) == str(id(self.output.item(idx))):
                self.output.item(idx).setText(self.output.item(idx).text() + text)
                return True
            idx += 1

    def get_program(self):
        program = self.assembly_code.toPlainText().splitlines()

        if not program:
            return []

        program_without_end_lines = program.copy()
        for i in range(len(program) - 1, 0, -1):
            if not program[i]:
                program_without_end_lines.pop(i)
            else:
                break

        return program_without_end_lines

    def wait(self):
        QtWidgets.qApp.processEvents()

        if self._delay == 0:
            return

        started = time.time()
        while time.time() - started < self._delay:
            QtWidgets.qApp.processEvents()

    @staticmethod
    def to_hex(n):
        return '%s' % ('0000%x' % (n & 0xffff))[-4:]


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    x = MainWindow()
    x.show()
    sys.exit(app.exec())
