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

        # Menu widgets
        self.menuProgram = QtWidgets.QMenu(self.menubar)
        self.menuMachine = QtWidgets.QMenu(self.menubar)

        # Action widgets
        self.actionNew = QtWidgets.QAction(self)
        self.actionLoad = QtWidgets.QAction(self)
        self.actionLoad_additional = QtWidgets.QAction(self)
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

        # Buttons
        self.stop_machine = QtWidgets.QPushButton(self.central_widget)
        self.reset_machine = QtWidgets.QPushButton(self.central_widget)
        self.do_one_step = QtWidgets.QPushButton(self.central_widget)
        self.run_assembly = QtWidgets.QPushButton(self.central_widget)

        # Labels
        self.program_label = QtWidgets.QLabel(self.central_widget)
        self.machine_code_label = QtWidgets.QLabel(self.central_widget)
        self.label_3 = QtWidgets.QLabel(self.central_widget)
        self.symbol_table_label = QtWidgets.QLabel(self.central_widget)
        self.registers_label = QtWidgets.QLabel(self.central_widget)
        self.buttons_label = QtWidgets.QLabel(self.central_widget)
        self.cycle_label = QtWidgets.QLabel(self.central_widget)

        # Setup
        self.setup_ui()
        self.retranslate_ui()
        self.connect_actions()

        # Executors
        self._stop = False
        self.device = Device()

    def setup_ui(self):
        # Main window
        self.setObjectName("MainWindow")
        self.setFixedSize(1200, 800)

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

        self.buttons_label.setGeometry(QtCore.QRect(1050, 305, 81, 31))
        self.buttons_label.setFont(segoe_font)

        self.cycle_label.setGeometry(QtCore.QRect(1050, 345, 91, 21))
        self.cycle_label.setFont(consolas_font)

    def setup_buttons_ui(self):
        segoe_font = QtGui.QFont()
        segoe_font.setFamily("Segoe UI")
        segoe_font.setPointSize(12)

        self.run_assembly.setGeometry(QtCore.QRect(1000, 380, 191, 38))
        self.run_assembly.setFont(segoe_font)

        self.do_one_step.setGeometry(QtCore.QRect(1000, 423, 191, 38))
        self.do_one_step.setFont(segoe_font)

        self.stop_machine.setGeometry(QtCore.QRect(1000, 467, 191, 38))
        self.stop_machine.setFont(segoe_font)

        self.reset_machine.setGeometry(QtCore.QRect(1000, 510, 191, 38))
        self.reset_machine.setFont(segoe_font)

    def setup_lists_ui(self):
        consolas_font = QtGui.QFont()
        consolas_font.setFamily("Consolas")
        consolas_font.setPointSize(11)

        self.machine_code.setGeometry(QtCore.QRect(430, 50, 290, 500))
        self.machine_code.setFont(consolas_font)
        self.machine_code.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.mapped_symbols.setGeometry(QtCore.QRect(740, 50, 240, 500))
        self.mapped_symbols.setFont(consolas_font)
        self.mapped_symbols.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.output.setGeometry(QtCore.QRect(10, 560, 1181, 181))
        self.output.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.output.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

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
        self.menuProgram.addAction(self.actionLoad_additional)
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
        self.assembly_code.setGeometry(QtCore.QRect(10, 50, 400, 500))
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 29))
        self.setMenuBar(self.menubar)
        self.setStatusBar(self.statusbar)

    def retranslate_ui(self):
        self.setWindowTitle("Viking")

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

        self.cycle_label.setText(translate("MainWindow", "Cycle: 0"))

        self.buttons_label.setText(
            translate("MainWindow",
                      "<html><head/><body><p>Control<span style=\" font-weight:600;\">:</span></p></body></html>"))

    def retranslate_menu_ui(self, translate):
        self.menuProgram.setTitle(translate("MainWindow", "Program"))
        self.menuMachine.setTitle(translate("MainWindow", "Machine"))

    def retranslate_actions_ui(self, translate):
        self.actionNew.setText(translate("MainWindow", "New"))

        self.actionLoad.setText(translate("MainWindow", "Load"))
        self.actionLoad_additional.setText(translate("MainWindow", "Load aditional"))

        self.actionSave_as.setText(translate("MainWindow", "Save as"))

        self.actionAssemble.setText(translate("MainWindow", "Assemble"))
        self.actionAssemble.setShortcut(translate("MainWindow", "Ctrl+A"))

        self.actionExit.setText(translate("MainWindow", "Exit"))
        self.actionExit.setShortcut(translate("MainWindow", "Ctrl+Del"))

        self.actionSet_breakpoint.setText(translate("MainWindow", "Set breakpoint"))

        self.actionSet_machine_cycle_delay.setText(translate("MainWindow", "Set machine cycle delay"))

        self.actionClear_terminal.setText(translate("MainWindow", "Clear terminal"))

        self.actionMemory_dump.setText(translate("MainWindow", "Memory dump"))

    def retranslate_lists_ui(self):
        self.registers_table.setSortingEnabled(False)
        for i in range(1, 5):
            self.registers_table.item(i).setText(f"r{i}      : 0000")

        self.registers_table.item(0).setText("r0 (at) : 0000")
        self.registers_table.item(5).setText("r5 (sr) : 0000")
        self.registers_table.item(6).setText("r6 (lr) : 0000")
        self.registers_table.item(7).setText("r7 (sp) : dffe")
        self.registers_table.item(9).setText("PC      : 0000")
        self.registers_table.setSortingEnabled(False)

        self.output.setSortingEnabled(False)

    def retranslate_buttons_ui(self, translate):
        self.stop_machine.setText(translate("MainWindow", "Stop"))
        self.reset_machine.setText(translate("MainWindow", "Reset"))
        self.do_one_step.setText(translate("MainWindow", "Step"))
        self.run_assembly.setText(translate("MainWindow", "Run"))

    def get_program(self):
        program = self.assembly_code.toPlainText().splitlines()

        if not program:
            return []

        program_without_end_lines = program.copy()
        for i in range(len(program)-1, 0, -1):
            if not program[i]:
                program_without_end_lines.pop(i)
            else:
                break

        return program_without_end_lines

    def connect_actions(self):
        self.run_assembly.clicked.connect(self.run)
        self.actionNew.triggered.connect(self.assembly_code.clear)
        self.actionAssemble.triggered.connect(self.assemble)
        self.actionExit.triggered.connect(self.quit_app)
        self.reset_machine.clicked.connect(self.reset)
        self.stop_machine.clicked.connect(self.stop)

    def quit_app(self):
        raise SystemExit

    def set_output_item_text(self, item):
        idx = 0
        while 1:
            if item == self.output.item(idx):
                self.output.item(idx).setText(item.text() + ' Done.')
                break
            idx += 1

    def reset(self):
        self.device.reset()
        self.machine_code.clear()
        self.mapped_symbols.clear()

    def stop(self):
        self._stop = True

    def assemble(self):
        first_item = QtWidgets.QListWidgetItem('Assembling...')
        self.output.addItem(first_item)
        self.machine_code.clear()
        self.mapped_symbols.clear()

        program = self.get_program()

        # No program given
        if not program:
            self.set_output_item_text(first_item)
            self.output.addItem(QtWidgets.QListWidgetItem())
            self.output.scrollToItem(first_item, QtWidgets.QAbstractItemView.PositionAtTop)
            return

        codes, result, output, symbols = self.device.generate_output(program)
        self.set_output_item_text(first_item)

        # Output the machine_code
        for machine_code in codes:
            self.machine_code.addItem(QtWidgets.QListWidgetItem(machine_code))

        # Output the information about the program
        for line in result:
            self.output.addItem(QtWidgets.QListWidgetItem(line))

        for symbol in symbols:
            self.mapped_symbols.addItem(QtWidgets.QListWidgetItem(symbol))

        # Output the result of the program
        self.output.addItem(QtWidgets.QListWidgetItem())
        self.output.scrollToItem(first_item, QtWidgets.QAbstractItemView.PositionAtTop)

    def run(self):
        self.assemble()

        # Simulates the machine doing the steps

        # import time
        # for step in self.device.get_steps():
        #     time.sleep(2)
        #     if not self._stop:
        #         print(step)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    x = MainWindow()
    x.show()
    sys.exit(app.exec())
