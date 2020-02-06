from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout, QComboBox, QPushButton, QVBoxLayout
from utils import get_devices
from audio import DeviceInputStream, DeviceOutputStream

class Window(QWidget):
    def __init__(self, run_callback):
        super().__init__()
        self.left = 200
        self.top = 200
        self.width = 400
        self.height = 120
        self.run_callback = run_callback
        self.custom_state_rows = []

        self.input_dropdown = None
        self.output_dropdown = None
        self.playback_dropdown = None

        self.devices = get_devices()
        self.layout = QFormLayout()

        self.selected_devices = {
            "input_device_index": None,
            "output_device_index": None,
            "playback_device_index": None
        }

        self.init_ui()

    def init_ui(self):
        input_label = QLabel('Microphone Input')
        self.input_dropdown, input_dropdown_values = self.create_device_dropdown(filter='maxInputChannels', field_name='input_device_index')
        if len(input_dropdown_values) > 0:
            self.input_device_index = input_dropdown_values[0]
        self.input_dropdown.activated[int].connect(self.handle_dropdown_selection(input_dropdown_values, 'input_device_index'))

        output_label = QLabel('Primary Output')
        self.output_dropdown, output_dropdown_values = self.create_device_dropdown(filter='maxOutputChannels', field_name='output_device_index')
        if len(output_dropdown_values) > 0:
            self.output_device_index = output_dropdown_values[0]
        self.output_dropdown.activated[int].connect(self.handle_dropdown_selection(output_dropdown_values, 'output_device_index'))

        playback_label = QLabel('Playback Output')
        self.playback_dropdown, playback_dropdown_values = self.create_device_dropdown(items=['No playback'], values=[None], filter='maxOutputChannels', field_name='playback_device_index')
        self.playback_dropdown.activated[int].connect(self.handle_dropdown_selection(playback_dropdown_values, 'playback_device_index'))

        self.layout.addRow(input_label, self.input_dropdown)
        self.layout.addRow(output_label, self.output_dropdown)
        self.layout.addRow(playback_label, self.playback_dropdown)

        self.set_setup_state()

        self.setLayout(self.layout)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def clear_custom_state(self):
        for row in self.custom_state_rows:
            self.layout.removeRow(row)
        self.custom_state_rows = []

    def set_setup_state(self):
        self.clear_custom_state()
        self.input_dropdown.setEnabled(True)
        self.output_dropdown.setEnabled(True)
        self.playback_dropdown.setEnabled(True)


        self.run_button = QPushButton('Run')
        self.run_button.clicked.connect(self.on_submit)

        self.layout.addRow(self.run_button)
        self.custom_state_rows.append(self.run_button)

    def set_running_state(self):
        self.clear_custom_state()
        self.input_dropdown.setEnabled(False)
        self.output_dropdown.setEnabled(False)
        self.playback_dropdown.setEnabled(False)

        self.stop_button = QPushButton('Stop')
        self.running_label = QLabel('Running...')
        self.stop_button.clicked.connect(self.on_kill)

        self.layout.addRow(self.running_label)
        self.layout.addRow(self.stop_button)
        self.custom_state_rows.append(self.running_label)
        self.custom_state_rows.append(self.stop_button)

    def handle_dropdown_selection(self, dropdown_values, key):
        def handle_dropdown_select_nested(index):
            self.selected_devices[key] = dropdown_values[index]
        return handle_dropdown_select_nested

    def on_submit(self):
        print('Running...')
        input_device = self.get_device_by_index(self.selected_devices["input_device_index"])
        output_device = self.get_device_by_index(self.selected_devices["output_device_index"])
        playback_device = self.get_device_by_index(self.selected_devices["playback_device_index"])
        self.runnable = self.run_callback(input_device=input_device, output_device=output_device, playback_device=playback_device, enable_burst=True)
        self.set_running_state()

    def on_kill(self):
        print('Stopping...')
        if self.runnable:
            self.runnable.exit()
        self.set_setup_state()

    def get_device_by_index(self, index):
        if index == None:
            return None
        return self.devices[index]

    def create_device_dropdown(self, filter, field_name, items=[], values=[]):
        dropdown = QComboBox()
        dropdown_values = []
        for i in range(0, len(items)):
            dropdown.addItem(items[i])
            dropdown_values.append(values[i])
        for device in self.devices:
            if int(device.get(filter)) > 0:
                dropdown.addItem(device.get('name'))
                dropdown_values.append(device.get('index'))
        if len(dropdown_values) > 0:
            self.selected_devices[field_name] = dropdown_values[0]
        return dropdown, dropdown_values
