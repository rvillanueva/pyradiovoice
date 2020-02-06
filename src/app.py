from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout, QComboBox, QPushButton
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
        self.run_button = QPushButton('Run')
        self.devices = get_devices()
        self.base_layout = None
        self.layout = None

        self.selected_devices = {
            "input_device_index": None,
            "output_device_index": None,
            "playback_device_index": None
        }

        self.init_ui()

    def init_ui(self):
        self.base_layout = QFormLayout()
        self.generate_setup_layout()
        self.setGeometry(self.left, self.top, self.width, self.height)

    def generate_setup_layout(self):
        self.clear_layout()
        layout = QFormLayout()
        input_label = QLabel('Microphone Input')
        input_dropdown, input_dropdown_values = self.create_device_dropdown(filter='maxInputChannels')
        if len(input_dropdown_values) > 0:
            self.input_device_index = input_dropdown_values[0]
        input_dropdown.activated[int].connect(self.handle_dropdown_selection(input_dropdown_values, 'input_device_index'))

        output_label = QLabel('Primary Output')
        output_dropdown, output_dropdown_values = self.create_device_dropdown(filter='maxOutputChannels')
        if len(output_dropdown_values) > 0:
            self.output_device_index = output_dropdown_values[0]
        output_dropdown.activated[int].connect(self.handle_dropdown_selection(output_dropdown_values, 'output_device_index'))

        playback_label = QLabel('Playback Output')
        playback_dropdown, playback_dropdown_values = self.create_device_dropdown(items=['No playback'], values=[None], filter='maxOutputChannels')
        playback_dropdown.activated[int].connect(self.handle_dropdown_selection(playback_dropdown_values, 'playback_device_index'))

        layout.addRow(input_label, input_dropdown)
        layout.addRow(output_label, output_dropdown)
        layout.addRow(playback_label, playback_dropdown)
        layout.addRow(self.run_button)

        self.run_button.clicked.connect(self.on_submit)

        self.setLayout(layout)
        self.layout = layout

    def clear_layout(self):
        if self.layout:
            self.base_layout.removeItem(self.layout)
            self.layout = None

    def generate_running_layout(self):
        self.clear_layout()
        layout = QFormLayout()
        running_label = QLabel('Running...')
        layout.addRow(running_label)
        stop_button = QPushButton('Stop')
        layout.addRow(stop_button)

    def handle_dropdown_selection(self, dropdown_values, key):
        def handle_dropdown_select_nested(index):
            self.selected_devices[key] = dropdown_values[index]
        return handle_dropdown_select_nested

    def on_submit(self):
        input_device = self.get_device_by_index(self.selected_devices["input_device_index"])
        output_device = self.get_device_by_index(self.selected_devices["output_device_index"])
        playback_device = self.get_device_by_index(self.selected_devices["playback_device_index"])

        self.runnable = self.run_callback(input_device=input_device, output_device=output_device, playback_device=playback_device, enable_burst=True)
        self.generate_running_layout()

    def kill_changer(self):
        if self.runnable:
            self.runnable.exit()

    def get_device_by_index(self, index):
        if index == None:
            return None
        return self.devices[index]

    def create_device_dropdown(self, filter, items=[], values=[]):
        dropdown = QComboBox()
        dropdown_values = []
        for i in range(0, len(items)):
            dropdown.addItem(items[i])
            dropdown_values.append(values[i])
        for device in self.devices:
            if device.get(filter) > 0:
                dropdown.addItem(device.get('name'))
                dropdown_values.append(device.get('index'))
        return dropdown, dropdown_values
