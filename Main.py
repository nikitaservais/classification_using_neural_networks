import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyleFactory, QApplication, QTabWidget, QGridLayout, QVBoxLayout, QWidget, QPushButton, \
    QDoubleSpinBox, QComboBox, QLabel

import Cifar10Loader
import MnistLoader
from DataVisualize import VisualizeData
from Graphics import Graphics
from Network import Network
from Thread import Thread
from WeightVisualize import VisualizeWeight

DATASET = {"MNIST digit": {"Small": "train_small.csv", "Big": "train.csv"},
           "MNIST fashion": {"Small": "fashion-mnist_train_small.csv", "Big": "fashion-mnist_train.csv", },
           "Cifar-10": {"Small": True, "Big": False}}


def init_label(text):
    """
    init labels
    """
    label = QLabel()
    label.setText(text)
    label.setAlignment(Qt.AlignCenter)
    return label


def init_combo_box(*argv):
    """
    init combo_box
    """
    combo_box = QComboBox()
    for item in argv:
        combo_box.addItem(str(item))
    return combo_box


def init_double_spin_box(step, maximum, minimum, decimals, value):
    """
    init double_spin_box
    """
    double_spin_box = QDoubleSpinBox()
    double_spin_box.setSingleStep(step)
    double_spin_box.setMaximum(maximum)
    double_spin_box.setMinimum(minimum)
    double_spin_box.setDecimals(decimals)
    double_spin_box.setValue(value)
    return double_spin_box


def init_button(text, parent, link):
    """
    init buttons
    """
    button = QPushButton(text, parent)
    button.clicked.connect(link)
    return button


class Window(QWidget):

    def __init__(self):
        """
        window with 2 tabs : graphics that plot cost and accuracy of the network
        visualization that show the data images and the weights of the network layer by layer
        on top is a main grid with parameters for the network
        """
        super(Window, self).__init__()
        # self.showMaximized()
        self.workThread = None
        self.setWindowTitle("Partie 4")
        self.setWindowIcon(QIcon('ULBLogo.png'))
        self._setup_layout()
        self.show()

    def _setup_layout(self):
        """
        setup layouts
        """
        self.MainVLayout = QVBoxLayout()
        self.MainGridLaypout = QGridLayout()
        self._setup_main_grid_layout()
        self._setup_tabs()
        self.MainVLayout.addLayout(self.MainGridLaypout)
        self.MainVLayout.addWidget(self.MainTabWidget)
        self.setLayout(self.MainVLayout)

    def _setup_tabs(self):
        """
        setup tabs
        """
        self.MainTabWidget = QTabWidget(self)
        self.MainTabWidget.addTab(graphics_widget, "Graphics")
        self.MainTabWidget.addTab(visualize_data_widget, "Visualize data")
        self.MainTabWidget.addTab(visualize_weight_widget, "Visualize weight")

    def _setup_main_grid_layout(self):
        """
        setup MainGridLayout
        """
        self.dataSetLabel = init_label("Data Set")
        self.dataSet = init_combo_box("MNIST digit", "MNIST fashion", "Cifar-10")

        self.dataFileLabel = init_label("Data size")
        self.dataFile = init_combo_box("Big", "Small")

        self.nbHiddenLayerLabel = init_label("Nb hidden layer")
        self.nbHiddenLayer = init_double_spin_box(1, 100, 0, 0, 1)

        self.nbNeuronsLabel = init_label("Nb neurons")
        self.nbNeurons = init_double_spin_box(1, 10000, 0, 0, 36)

        self.trainingSizeLabel = init_label("training size")
        self.trainingSize = init_double_spin_box(0.1, 0.99, 0.01, 2, 0.90)

        self.probDropoutLabel = init_label("Prob dropout")
        self.probDropout = init_double_spin_box(0.1, 0.9, 0, 1, 0.0)

        self.cLabel = init_label("Max norm")
        self.c = init_double_spin_box(1, 100, 0, 0, 0)

        self.lmbdaLabel = init_label("L2 factor")
        self.lmbda = init_double_spin_box(0.1, 100, 0, 1, 4)

        self.learningRateLabel = init_label("Learning rate")
        self.learningRate = init_double_spin_box(0.01, 100, 0, 2, 0.1)

        self.epochLabel = init_label("Epochs")
        self.epoch = init_double_spin_box(1, 1000, 2, 0, 30)

        self.start = init_button("Start !", self, self.start_action)
        self.cancel = init_button("Cancel !", self, self.cancel_action)
        self.cancel.setEnabled(False)
        self.add_box()

    def add_box(self):
        """
        add box to MainGridLayout
        """
        self.MainGridLaypout.addWidget(self.dataSetLabel, 0, 0)
        self.MainGridLaypout.addWidget(self.dataFileLabel, 0, 1)
        self.MainGridLaypout.addWidget(self.trainingSizeLabel, 0, 2)
        self.MainGridLaypout.addWidget(self.nbHiddenLayerLabel, 0, 3)
        self.MainGridLaypout.addWidget(self.nbNeuronsLabel, 0, 4)
        self.MainGridLaypout.addWidget(self.probDropoutLabel, 0, 5)
        self.MainGridLaypout.addWidget(self.cLabel, 0, 6)
        self.MainGridLaypout.addWidget(self.lmbdaLabel, 0, 7)
        self.MainGridLaypout.addWidget(self.learningRateLabel, 0, 8)
        self.MainGridLaypout.addWidget(self.epochLabel, 0, 9)
        self.MainGridLaypout.addWidget(self.cancel, 0, 10)

        self.MainGridLaypout.addWidget(self.dataSet, 1, 0)
        self.MainGridLaypout.addWidget(self.dataFile, 1, 1)
        self.MainGridLaypout.addWidget(self.trainingSize, 1, 2)
        self.MainGridLaypout.addWidget(self.nbHiddenLayer, 1, 3)
        self.MainGridLaypout.addWidget(self.nbNeurons, 1, 4)
        self.MainGridLaypout.addWidget(self.probDropout, 1, 5)
        self.MainGridLaypout.addWidget(self.c, 1, 6)
        self.MainGridLaypout.addWidget(self.lmbda, 1, 7)
        self.MainGridLaypout.addWidget(self.learningRate, 1, 8)
        self.MainGridLaypout.addWidget(self.epoch, 1, 9)
        self.MainGridLaypout.addWidget(self.start, 1, 10)

    def get_data(self):
        """
        get data from all widgets
        """
        data_set = self.dataSet.currentText()
        dataFile = self.dataFile.currentText()
        training_size = self.trainingSize.value()
        nb_hidden_layer = int(self.nbHiddenLayer.value())
        nb_neurons = int(self.nbNeurons.value())
        prob_dropout = self.probDropout.value()
        c = int(self.c.value())
        lmbda = self.lmbda.value()
        learningRate = self.learningRate.value()
        epoch = int(self.epoch.value())
        return data_set, dataFile, training_size, nb_hidden_layer, nb_neurons, prob_dropout, c, lmbda, learningRate, epoch

    def done(self):
        """
        Enable button when thread is finished
        """
        self.cancel.setEnabled(False)
        self.start.setEnabled(True)

    def cancel_action(self):
        """
        terminate the thread and enable button
        """
        self.workThread.stop = True
        self.cancel.setEnabled(False)
        self.start.setEnabled(True)
        print("Canceled")

    def start_action(self):
        """
        create a thread to launch the network with the settings from get_data
        start the thread and connect signal to modules
        """
        global net
        dataSet, dataFile, trainingSize, nbHiddenLayer, nbNeurons, probDropout, c, lmbda, learning_rate, epoch = GUI.get_data()
        file = DATASET[dataSet][dataFile]
        if dataSet == "Cifar-10":
            data = Cifar10Loader.read_file(file)
            layer = [3072]
        else:
            data = MnistLoader.read_file(file)
            layer = [784]
        for i in range(nbHiddenLayer):
            layer.append(nbNeurons // nbHiddenLayer)
        if nbNeurons % nbHiddenLayer != 0:
            layer.append(nbNeurons % nbHiddenLayer)
        layer.append(10)
        net = Network(layers=layer)
        mTA, mTC, mVA, mVC = graphics_widget.get_data()
        self.workThread = Thread(False, net, graphics_widget, visualize_data_widget, visualize_weight_widget, data,
                                 trainingSize, 1 - probDropout, int(c), lmbda, learning_rate, int(epoch), mTA, mTC, mVA,
                                 mVC)
        self.workThread.start()
        self.start.setEnabled(False)
        self.cancel.setEnabled(True)
        self.workThread.updateBar.connect(graphics_widget.progress)
        self.workThread.updateGraphs.connect(graphics_widget.draw_plot)
        self.workThread.finished.connect(self.done)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Plastique'))
    visualize_weight_widget = VisualizeWeight()
    visualize_data_widget = VisualizeData()
    graphics_widget = Graphics()
    GUI = Window()
    sys.exit(app.exec_())
