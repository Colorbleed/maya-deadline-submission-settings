from avalon.vendor.Qt import QtWidgets, QtCore

from . import lib
from . import mayalib


class App(QtWidgets.QWidget):
    """Main application for alter settings per render job (layer)"""

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setObjectName("deadlineSubmissionSettings")
        self.setWindowTitle("Deadline Submission setting")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setFixedSize(250, 500)

        self.setup_ui()
        self.connections()
        self.create_machine_limit_options()
        self.create_pools_options()

        # Apply any settings based off the renderglobalsDefault instance
        self._apply_settings()

    def setup_ui(self):
        """Build the initial UI"""

        MULTI_SELECT = QtWidgets.QAbstractItemView.ExtendedSelection

        layout = QtWidgets.QVBoxLayout(self)

        publish = QtWidgets.QCheckBox("Suspend Publish Job")
        extend_frames = QtWidgets.QCheckBox("Extend Frames")
        override_frames = QtWidgets.QCheckBox("Override Frames")
        override_frames.setEnabled(False)
        defaultlayer = QtWidgets.QCheckBox("Include Default Render Layer")

        # region Priority
        priority_grp = QtWidgets.QGroupBox("Priority")
        priority_hlayout = QtWidgets.QHBoxLayout()

        priority_value = QtWidgets.QSpinBox()
        priority_value.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        priority_value.setEnabled(False)
        priority_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        priority_slider.setMinimum(0)
        priority_slider.setMaximum(99)

        priority_hlayout.addWidget(priority_value)
        priority_hlayout.addWidget(priority_slider)
        priority_grp.setLayout(priority_hlayout)
        # endregion Priority

        # region pools
        pools_grp = QtWidgets.QGroupBox("Pools")
        pools_vlayout = QtWidgets.QVBoxLayout()

        primary_hlayout = QtWidgets.QHBoxLayout()
        primary_label = QtWidgets.QLabel("Primary")
        primary_pool = QtWidgets.QComboBox()
        primary_hlayout.addWidget(primary_label)
        primary_hlayout.addWidget(primary_pool)

        secondary_hlayout = QtWidgets.QHBoxLayout()
        secondary_label = QtWidgets.QLabel("Secondary")
        secondary_pool = QtWidgets.QComboBox()
        secondary_hlayout.addWidget(secondary_label)
        secondary_hlayout.addWidget(secondary_pool)

        pools_vlayout.addLayout(primary_hlayout)
        pools_vlayout.addLayout(secondary_hlayout)

        pools_grp.setLayout(pools_vlayout)
        # endregion pools

        # Group box for type of machine list
        list_type_grp = QtWidgets.QGroupBox("Machine List Type")
        list_type_hlayout = QtWidgets.QHBoxLayout()

        black_list = QtWidgets.QRadioButton("Blacklist")
        black_list.setChecked(True)
        black_list.setToolTip("List machines which the job WILL NOT use")

        white_list = QtWidgets.QRadioButton("Whitelist")
        white_list.setToolTip("List machines which the job WILL use")

        list_type_hlayout.addWidget(black_list)
        list_type_hlayout.addWidget(white_list)
        list_type_grp.setLayout(list_type_hlayout)

        # region Machine selection
        machines_hlayout = QtWidgets.QHBoxLayout()
        machines_hlayout.setSpacing(2)
        machine_list = QtWidgets.QListWidget()
        listed_machines = QtWidgets.QListWidget()

        # Buttons
        button_vlayout = QtWidgets.QVBoxLayout()
        button_vlayout.setAlignment(QtCore.Qt.AlignCenter)
        button_vlayout.setSpacing(4)

        add_machine_btn = QtWidgets.QPushButton(">")
        add_machine_btn.setFixedWidth(25)

        remove_machine_btn = QtWidgets.QPushButton("<")
        remove_machine_btn.setFixedWidth(25)

        button_vlayout.addWidget(add_machine_btn)
        button_vlayout.addWidget(remove_machine_btn)

        machines_hlayout.addWidget(machine_list)
        machines_hlayout.addLayout(button_vlayout)
        machines_hlayout.addWidget(listed_machines)

        # Machine selection widget settings
        machine_list.setSelectionMode(MULTI_SELECT)
        listed_machines.setSelectionMode(MULTI_SELECT)

        # endregion
        accept_btn = QtWidgets.QPushButton("Use Settings")

        layout.addWidget(defaultlayer)
        layout.addWidget(publish)
        layout.addWidget(extend_frames)
        layout.addWidget(override_frames)
        layout.addWidget(priority_grp)
        layout.addWidget(pools_grp)
        layout.addWidget(list_type_grp)
        layout.addLayout(machines_hlayout)
        layout.addWidget(accept_btn)

        # Enable access for all methods
        self.publish = publish
        self.extend_frames = extend_frames
        self.override_frames = override_frames
        self.defaultlayer = defaultlayer

        self.priority_value = priority_value
        self.priority_slider = priority_slider
        self.primary_pool = primary_pool
        self.secondary_pool = secondary_pool

        self.black_list = black_list
        self.white_list = white_list
        self.machine_list = machine_list

        self.listed_machines = listed_machines
        self.add_machine_btn = add_machine_btn
        self.remove_machine_btn = remove_machine_btn
        self.accept = accept_btn

        self.setLayout(layout)

    def connections(self):
        self.priority_slider.valueChanged[int].connect(
            self.priority_value.setValue)
        self.add_machine_btn.clicked.connect(self.add_selected_machines)
        self.remove_machine_btn.clicked.connect(self.remove_selected_machines)
        self.accept.clicked.connect(self.parse_settings)
        self.extend_frames.toggled.connect(self._toggle_override_enabled)

        self.priority_slider.setValue(50)

    def _toggle_override_enabled(self):
        self.override_frames.setEnabled(self.extend_frames.isChecked())

    def add_selected_machines(self):
        """Add selected machines to the list which is going to be used"""

        # Get currently list machine for use
        listed_machines = self._get_listed_machines()

        # Get all machines selected from available
        machines = self.machine_list.selectedItems()
        machine_names = [m.text() for m in machines if m.text()
                         not in listed_machines]

        # Add to list of machines to use
        self.listed_machines.addItems(machine_names)

    def remove_selected_machines(self):
        machines = self.listed_machines.selectedItems()
        for machine in machines:
            self.listed_machines.takeItem(self.listed_machines.row(machine))

    def create_machine_limit_options(self):
        """Build the checks for the machine limit"""

        for name in lib.get_machine_list():
            self.machine_list.addItem(name)

    def create_pools_options(self):
        pools = lib.get_pool_list()
        for pool in pools:
            self.primary_pool.addItem(pool)
            self.secondary_pool.addItem(pool)

    def create_groups_options(self):
        groups = lib.get_group_list()
        for group in groups:
            self.groups.addItem(group)

    def refresh(self):

        self.primary_pool.clear()
        self.secondary_pool.clear()
        self.groups.clear()
        self.machine_list.clear()

        self.create_machine_limit_options()
        self.create_pools_options()
        self.create_groups_options()

    def parse_settings(self):

        # Get the  node, create node if none exists
        instance = mayalib.find_render_instance()
        if not instance:
            instance = mayalib.create_renderglobals_node()

        # Get UI settings as dict
        job_info = self._get_settings()
        mayalib.apply_settings(instance, job_info)

    def renderglobals_message(self):

        message = ("Please use the Creator from the Avalon menu to create "
                   "a renderglobalsDefault instance")

        button = QtWidgets.QMessageBox.StandardButton.Ok

        QtWidgets.QMessageBox.critical(self,
                                       "Missing renderglobalsDefault node",
                                       message,
                                       button)
        return

    def _get_settings(self):

        settings = {}
        machine_list_type = self._get_list_type()

        machine_limits = self._get_listed_machines()
        machine_limits = ",".join(machine_limits)

        settings["priority"] = self.priority_value.value()
        settings["includeDefaultRenderLayer"] = self.defaultlayer.isChecked()
        settings["suspendPublishJob"] = self.publish.isChecked()

        override = False
        extend_frames = self.extend_frames.isChecked()
        if extend_frames:
            override = self.override_frames.isChecked()

        settings["extendFrames"] = extend_frames
        settings["overrideExistingFrame"] = override

        settings[machine_list_type] = machine_limits

        # Get pools
        primary_pool = self.primary_pool.currentText()
        secondary_pool = self.secondary_pool.currentText()
        settings["pools"] = ";".join([primary_pool, secondary_pool])

        return settings

    def _apply_settings(self):

        instance = mayalib.find_render_instance()
        if not instance:
            return

        settings = mayalib.read_settings(instance)

        # Apply settings from node
        self.publish.setChecked(settings.get("suspendPublishJob", False))

        include_def_layer = settings.get("includeDefaultRenderLayer", False)
        self.defaultlayer.setChecked(include_def_layer)

        self.priority_slider.setValue(settings.get("priority", 50))
        self.extend_frames.setChecked(settings.get("extendFrames", False))

        override_frames = settings.get("overrideExistingFrame", False)
        self.override_frames.setChecked(override_frames)

        pools = [i for i in settings.get("pools", "").split(";") if i != ""]
        if not pools:
            pools = ["none", "none"]
        elif len(pools) == 1:
            pools.append("none")

        primary_pool, secondary_pool = pools

        for idx in range(self.primary_pool.count()):
            text = self.primary_pool.itemText(idx)
            if text == primary_pool:
                self.primary_pool.setCurrentIndex(idx)
                break

        for idx in range(self.secondary_pool.count()):
            text = self.secondary_pool.itemText(idx)
            if text == secondary_pool:
                self.secondary_pool.setCurrentIndex(idx)
                break

        white_list = settings.get("Whitelist", False)
        self.white_list.setChecked(white_list)
        self.black_list.setChecked(not white_list)

    def _get_list_type(self):
        if self.white_list.isChecked():
            return "Whitelist"
        else:
            return "Blacklist"

    def _get_listed_machines(self):
        items = [self.listed_machines.item(r) for r in
                 range(self.listed_machines.count())]
        listed_machines = [i.text() for i in items]

        return listed_machines


def launch():
    global application

    toplevel_widgets = QtWidgets.QApplication.topLevelWidgets()
    mainwindow = next(widget for widget in toplevel_widgets if
                      widget.objectName() == "MayaWindow")

    application = App(parent=mainwindow)
    application.show()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    test = App()
    test.show()
    app.exec_()
