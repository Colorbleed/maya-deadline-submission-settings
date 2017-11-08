from avalon.vendor.Qt import QtWidgets


class RenderLayerOptions(QtWidgets.QWidget):

    def __init__(self):

        layout = QtWidgets.QVBoxLayout()
        frame_list = QtWidgets.QLineEdit()
        frames_per_task = QtWidgets.QLineEdit()

        layout.addWidget(frame_list)
        layout.addWidget(frames_per_task)

        self.main_layout = layout
        self.frame_list = frame_list
        self.frames_per_task = frames_per_task

        self.setLayout(layout)
