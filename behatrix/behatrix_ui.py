# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'behatrix.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QDoubleSpinBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPlainTextEdit, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QSpinBox, QSplitter, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1969, 1017)
        self.actionDocumentation = QAction(MainWindow)
        self.actionDocumentation.setObjectName(u"actionDocumentation")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionLoad_behavioral_sequences = QAction(MainWindow)
        self.actionLoad_behavioral_sequences.setObjectName(u"actionLoad_behavioral_sequences")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_strings = QWidget()
        self.tab_strings.setObjectName(u"tab_strings")
        self.verticalLayout_15 = QVBoxLayout(self.tab_strings)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.splitter = QSplitter(self.tab_strings)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout_12 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_12.addWidget(self.label_2)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.pte_behav_seq = QPlainTextEdit(self.layoutWidget)
        self.pte_behav_seq.setObjectName(u"pte_behav_seq")
        font = QFont()
        font.setFamilies([u"Monospace"])
        self.pte_behav_seq.setFont(font)

        self.horizontalLayout_19.addWidget(self.pte_behav_seq)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pb_clear_behavioral_strings = QPushButton(self.layoutWidget)
        self.pb_clear_behavioral_strings.setObjectName(u"pb_clear_behavioral_strings")

        self.verticalLayout_3.addWidget(self.pb_clear_behavioral_strings)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_4)


        self.horizontalLayout_19.addLayout(self.verticalLayout_3)


        self.verticalLayout_12.addLayout(self.horizontalLayout_19)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_17 = QLabel(self.layoutWidget)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_16.addWidget(self.label_17)

        self.le_behaviors_separator = QLineEdit(self.layoutWidget)
        self.le_behaviors_separator.setObjectName(u"le_behaviors_separator")

        self.horizontalLayout_16.addWidget(self.le_behaviors_separator)

        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_16.addWidget(self.label_6)

        self.sb_ngram = QSpinBox(self.layoutWidget)
        self.sb_ngram.setObjectName(u"sb_ngram")
        self.sb_ngram.setMinimum(1)
        self.sb_ngram.setMaximum(3)
        self.sb_ngram.setSingleStep(1)

        self.horizontalLayout_16.addWidget(self.sb_ngram)

        self.cb_remove_repeated_behaviors = QCheckBox(self.layoutWidget)
        self.cb_remove_repeated_behaviors.setObjectName(u"cb_remove_repeated_behaviors")

        self.horizontalLayout_16.addWidget(self.cb_remove_repeated_behaviors)

        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_15)


        self.verticalLayout_12.addLayout(self.horizontalLayout_16)

        self.splitter.addWidget(self.layoutWidget)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.verticalLayout_14 = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_4 = QLabel(self.layoutWidget1)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_10.addWidget(self.label_4)

        self.pte_statistics = QPlainTextEdit(self.layoutWidget1)
        self.pte_statistics.setObjectName(u"pte_statistics")
        self.pte_statistics.setFont(font)
        self.pte_statistics.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.pte_statistics.setReadOnly(True)

        self.verticalLayout_10.addWidget(self.pte_statistics)


        self.horizontalLayout.addLayout(self.verticalLayout_10)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_9 = QLabel(self.layoutWidget1)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_7.addWidget(self.label_9)

        self.tw_observed_transitions = QTableWidget(self.layoutWidget1)
        self.tw_observed_transitions.setObjectName(u"tw_observed_transitions")

        self.verticalLayout_7.addWidget(self.tw_observed_transitions)

        self.label_10 = QLabel(self.layoutWidget1)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_7.addWidget(self.label_10)


        self.horizontalLayout.addLayout(self.verticalLayout_7)


        self.verticalLayout_14.addLayout(self.horizontalLayout)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.pb_save_results = QPushButton(self.layoutWidget1)
        self.pb_save_results.setObjectName(u"pb_save_results")

        self.horizontalLayout_12.addWidget(self.pb_save_results)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer_8)


        self.verticalLayout_14.addLayout(self.horizontalLayout_12)

        self.splitter.addWidget(self.layoutWidget1)

        self.verticalLayout_15.addWidget(self.splitter)

        self.tabWidget.addTab(self.tab_strings, "")
        self.tab_flow_diagram = QWidget()
        self.tab_flow_diagram.setObjectName(u"tab_flow_diagram")
        self.verticalLayout_13 = QVBoxLayout(self.tab_flow_diagram)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.vertical_splitter = QSplitter(self.tab_flow_diagram)
        self.vertical_splitter.setObjectName(u"vertical_splitter")
        self.vertical_splitter.setOrientation(Qt.Vertical)
        self.layoutWidget2 = QWidget(self.vertical_splitter)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.verticalLayout_5 = QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.rb_percent_after_behav = QRadioButton(self.layoutWidget2)
        self.buttonGroup_2 = QButtonGroup(MainWindow)
        self.buttonGroup_2.setObjectName(u"buttonGroup_2")
        self.buttonGroup_2.addButton(self.rb_percent_after_behav)
        self.rb_percent_after_behav.setObjectName(u"rb_percent_after_behav")
        self.rb_percent_after_behav.setChecked(True)

        self.horizontalLayout_10.addWidget(self.rb_percent_after_behav)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.sb_cutoff_transition_after_behav = QDoubleSpinBox(self.layoutWidget2)
        self.sb_cutoff_transition_after_behav.setObjectName(u"sb_cutoff_transition_after_behav")
        self.sb_cutoff_transition_after_behav.setDecimals(1)

        self.horizontalLayout_4.addWidget(self.sb_cutoff_transition_after_behav)

        self.label_11 = QLabel(self.layoutWidget2)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_4.addWidget(self.label_11)


        self.horizontalLayout_10.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_5.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.rb_percent_total_transitions = QRadioButton(self.layoutWidget2)
        self.buttonGroup_2.addButton(self.rb_percent_total_transitions)
        self.rb_percent_total_transitions.setObjectName(u"rb_percent_total_transitions")

        self.horizontalLayout_18.addWidget(self.rb_percent_total_transitions)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.sb_cutoff_total_transition = QDoubleSpinBox(self.layoutWidget2)
        self.sb_cutoff_total_transition.setObjectName(u"sb_cutoff_total_transition")
        self.sb_cutoff_total_transition.setDecimals(1)

        self.horizontalLayout_8.addWidget(self.sb_cutoff_total_transition)

        self.label_12 = QLabel(self.layoutWidget2)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_8.addWidget(self.label_12)

        self.label_18 = QLabel(self.layoutWidget2)
        self.label_18.setObjectName(u"label_18")

        self.horizontalLayout_8.addWidget(self.label_18)

        self.sb_decimals = QSpinBox(self.layoutWidget2)
        self.sb_decimals.setObjectName(u"sb_decimals")
        self.sb_decimals.setMaximum(6)
        self.sb_decimals.setValue(1)

        self.horizontalLayout_8.addWidget(self.sb_decimals)

        self.cb_plot_significativity = QCheckBox(self.layoutWidget2)
        self.cb_plot_significativity.setObjectName(u"cb_plot_significativity")

        self.horizontalLayout_8.addWidget(self.cb_plot_significativity)

        self.label_8 = QLabel(self.layoutWidget2)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_8.addWidget(self.label_8)

        self.comb_graphviz_engine = QComboBox(self.layoutWidget2)
        self.comb_graphviz_engine.addItem("")
        self.comb_graphviz_engine.addItem("")
        self.comb_graphviz_engine.addItem("")
        self.comb_graphviz_engine.setObjectName(u"comb_graphviz_engine")

        self.horizontalLayout_8.addWidget(self.comb_graphviz_engine)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_13)


        self.horizontalLayout_18.addLayout(self.horizontalLayout_8)


        self.horizontalLayout_5.addLayout(self.horizontalLayout_18)


        self.verticalLayout_5.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.pb_graphviz_script = QPushButton(self.layoutWidget2)
        self.pb_graphviz_script.setObjectName(u"pb_graphviz_script")

        self.horizontalLayout_6.addWidget(self.pb_graphviz_script)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)


        self.verticalLayout_5.addLayout(self.horizontalLayout_6)

        self.vertical_splitter.addWidget(self.layoutWidget2)
        self.layoutWidget3 = QWidget(self.vertical_splitter)
        self.layoutWidget3.setObjectName(u"layoutWidget3")
        self.verticalLayout_8 = QVBoxLayout(self.layoutWidget3)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.script_diagram_splitter = QSplitter(self.layoutWidget3)
        self.script_diagram_splitter.setObjectName(u"script_diagram_splitter")
        self.script_diagram_splitter.setOrientation(Qt.Horizontal)
        self.layoutWidget4 = QWidget(self.script_diagram_splitter)
        self.layoutWidget4.setObjectName(u"layoutWidget4")
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_14 = QLabel(self.layoutWidget4)
        self.label_14.setObjectName(u"label_14")

        self.verticalLayout_4.addWidget(self.label_14)

        self.pte_gv_nodes = QPlainTextEdit(self.layoutWidget4)
        self.pte_gv_nodes.setObjectName(u"pte_gv_nodes")

        self.verticalLayout_4.addWidget(self.pte_gv_nodes)

        self.pte_gv_edges = QPlainTextEdit(self.layoutWidget4)
        self.pte_gv_edges.setObjectName(u"pte_gv_edges")
        self.pte_gv_edges.setFont(font)

        self.verticalLayout_4.addWidget(self.pte_gv_edges)

        self.pte_gv_graph = QPlainTextEdit(self.layoutWidget4)
        self.pte_gv_graph.setObjectName(u"pte_gv_graph")

        self.verticalLayout_4.addWidget(self.pte_gv_graph)

        self.script_diagram_splitter.addWidget(self.layoutWidget4)
        self.lb_flow_chart = QLabel(self.script_diagram_splitter)
        self.lb_flow_chart.setObjectName(u"lb_flow_chart")
        self.lb_flow_chart.setMinimumSize(QSize(0, 100))
        self.script_diagram_splitter.addWidget(self.lb_flow_chart)

        self.verticalLayout_8.addWidget(self.script_diagram_splitter)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.pb_save_gv = QPushButton(self.layoutWidget3)
        self.pb_save_gv.setObjectName(u"pb_save_gv")

        self.horizontalLayout_13.addWidget(self.pb_save_gv)

        self.pb_clear_script = QPushButton(self.layoutWidget3)
        self.pb_clear_script.setObjectName(u"pb_clear_script")

        self.horizontalLayout_13.addWidget(self.pb_clear_script)

        self.pb_clear_diagram = QPushButton(self.layoutWidget3)
        self.pb_clear_diagram.setObjectName(u"pb_clear_diagram")

        self.horizontalLayout_13.addWidget(self.pb_clear_diagram)

        self.pb_save_png = QPushButton(self.layoutWidget3)
        self.pb_save_png.setObjectName(u"pb_save_png")

        self.horizontalLayout_13.addWidget(self.pb_save_png)

        self.pb_save_svg = QPushButton(self.layoutWidget3)
        self.pb_save_svg.setObjectName(u"pb_save_svg")

        self.horizontalLayout_13.addWidget(self.pb_save_svg)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_12)


        self.verticalLayout_8.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.pb_flow_diagram = QPushButton(self.layoutWidget3)
        self.pb_flow_diagram.setObjectName(u"pb_flow_diagram")

        self.horizontalLayout_25.addWidget(self.pb_flow_diagram)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_16 = QLabel(self.layoutWidget3)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_14.addWidget(self.label_16)

        self.le_dot_path = QLineEdit(self.layoutWidget3)
        self.le_dot_path.setObjectName(u"le_dot_path")
        self.le_dot_path.setReadOnly(False)

        self.horizontalLayout_14.addWidget(self.le_dot_path)

        self.pb_browse_dot_path = QPushButton(self.layoutWidget3)
        self.pb_browse_dot_path.setObjectName(u"pb_browse_dot_path")

        self.horizontalLayout_14.addWidget(self.pb_browse_dot_path)


        self.horizontalLayout_25.addLayout(self.horizontalLayout_14)


        self.verticalLayout_8.addLayout(self.horizontalLayout_25)

        self.vertical_splitter.addWidget(self.layoutWidget3)

        self.verticalLayout_13.addWidget(self.vertical_splitter)

        self.tabWidget.addTab(self.tab_flow_diagram, "")
        self.tab_randomization = QWidget()
        self.tab_randomization.setObjectName(u"tab_randomization")
        self.verticalLayout_6 = QVBoxLayout(self.tab_randomization)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

        self.label_7 = QLabel(self.tab_randomization)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_6.addWidget(self.label_7)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.pte_excluded_transitions = QPlainTextEdit(self.tab_randomization)
        self.pte_excluded_transitions.setObjectName(u"pte_excluded_transitions")
        self.pte_excluded_transitions.setFont(font)

        self.horizontalLayout_15.addWidget(self.pte_excluded_transitions)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pb_exclude_repetition = QPushButton(self.tab_randomization)
        self.pb_exclude_repetition.setObjectName(u"pb_exclude_repetition")

        self.verticalLayout.addWidget(self.pb_exclude_repetition)

        self.pb_clear_excluded_transitions = QPushButton(self.tab_randomization)
        self.pb_clear_excluded_transitions.setObjectName(u"pb_clear_excluded_transitions")

        self.verticalLayout.addWidget(self.pb_clear_excluded_transitions)

        self.cb_block_first_behavior = QCheckBox(self.tab_randomization)
        self.cb_block_first_behavior.setObjectName(u"cb_block_first_behavior")

        self.verticalLayout.addWidget(self.cb_block_first_behavior)

        self.cb_block_last_behavior = QCheckBox(self.tab_randomization)
        self.cb_block_last_behavior.setObjectName(u"cb_block_last_behavior")

        self.verticalLayout.addWidget(self.cb_block_last_behavior)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.horizontalLayout_15.addLayout(self.verticalLayout)


        self.verticalLayout_6.addLayout(self.horizontalLayout_15)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.tab_randomization)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.leNumberRandomizations = QLineEdit(self.tab_randomization)
        self.leNumberRandomizations.setObjectName(u"leNumberRandomizations")

        self.horizontalLayout_3.addWidget(self.leNumberRandomizations)

        self.label_3 = QLabel(self.tab_randomization)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.sb_nb_cores = QSpinBox(self.tab_randomization)
        self.sb_nb_cores.setObjectName(u"sb_nb_cores")
        self.sb_nb_cores.setMinimum(1)

        self.horizontalLayout_3.addWidget(self.sb_nb_cores)

        self.label_5 = QLabel(self.tab_randomization)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)


        self.verticalLayout_6.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.pb_run_permutations_test = QPushButton(self.tab_randomization)
        self.pb_run_permutations_test.setObjectName(u"pb_run_permutations_test")

        self.horizontalLayout_7.addWidget(self.pb_run_permutations_test)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_3)


        self.verticalLayout_6.addLayout(self.horizontalLayout_7)

        self.label_15 = QLabel(self.tab_randomization)
        self.label_15.setObjectName(u"label_15")

        self.verticalLayout_6.addWidget(self.label_15)

        self.tw_random = QTableWidget(self.tab_randomization)
        self.tw_random.setObjectName(u"tw_random")

        self.verticalLayout_6.addWidget(self.tw_random)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.pb_save_random = QPushButton(self.tab_randomization)
        self.pb_save_random.setObjectName(u"pb_save_random")

        self.horizontalLayout_11.addWidget(self.pb_save_random)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_10)


        self.verticalLayout_6.addLayout(self.horizontalLayout_11)

        self.tabWidget.addTab(self.tab_randomization, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_9 = QVBoxLayout(self.tab)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.pb_levenshtein = QPushButton(self.tab)
        self.pb_levenshtein.setObjectName(u"pb_levenshtein")

        self.horizontalLayout_21.addWidget(self.pb_levenshtein)

        self.pb_needleman_wunsch = QPushButton(self.tab)
        self.pb_needleman_wunsch.setObjectName(u"pb_needleman_wunsch")

        self.horizontalLayout_21.addWidget(self.pb_needleman_wunsch)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_5)


        self.verticalLayout_9.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.label_19 = QLabel(self.tab)
        self.label_19.setObjectName(u"label_19")

        self.verticalLayout_11.addWidget(self.label_19)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer)


        self.horizontalLayout_22.addLayout(self.verticalLayout_11)

        self.pte_distances_results = QPlainTextEdit(self.tab)
        self.pte_distances_results.setObjectName(u"pte_distances_results")
        self.pte_distances_results.setReadOnly(True)

        self.horizontalLayout_22.addWidget(self.pte_distances_results)


        self.verticalLayout_9.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.pb_save_distances = QPushButton(self.tab)
        self.pb_save_distances.setObjectName(u"pb_save_distances")

        self.horizontalLayout_20.addWidget(self.pb_save_distances)

        self.horizontalSpacer_14 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_14)


        self.verticalLayout_9.addLayout(self.horizontalLayout_20)

        self.tabWidget.addTab(self.tab, "")

        self.verticalLayout_2.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1969, 29))
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuHelp_2 = QMenu(self.menubar)
        self.menuHelp_2.setObjectName(u"menuHelp_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuHelp.menuAction())
        self.menubar.addAction(self.menuHelp_2.menuAction())
        self.menuHelp.addAction(self.actionLoad_behavioral_sequences)
        self.menuHelp.addAction(self.actionQuit)
        self.menuHelp_2.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Behatrix", None))
        self.actionDocumentation.setText(QCoreApplication.translate("MainWindow", u"Documentation", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.actionLoad_behavioral_sequences.setText(QCoreApplication.translate("MainWindow", u"Load sequences from file", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"<b>Behavioral sequences</b>", None))
        self.pb_clear_behavioral_strings.setText(QCoreApplication.translate("MainWindow", u"Clear sequences", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Behavior delimiter", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"N-gram", None))
        self.cb_remove_repeated_behaviors.setText(QCoreApplication.translate("MainWindow", u"Remove repeated behaviors", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">Descriptive statistics</span></p></body></html>", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:600;\">Observed transitions</span></p></body></html>", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"The behavior on the first column precedes the behavior on the first row", None))
        self.pb_save_results.setText(QCoreApplication.translate("MainWindow", u"Save results", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_strings), QCoreApplication.translate("MainWindow", u"Behavioral sequences", None))
        self.rb_percent_after_behav.setText(QCoreApplication.translate("MainWindow", u"% of transitions after behavior", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"%", None))
        self.rb_percent_total_transitions.setText(QCoreApplication.translate("MainWindow", u"% of total transitions", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"%", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Number of decimals in edge labels", None))
        self.cb_plot_significativity.setText(QCoreApplication.translate("MainWindow", u"Add significativity to edges (perform the permutations test before)", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Engine", None))
        self.comb_graphviz_engine.setItemText(0, QCoreApplication.translate("MainWindow", u"dot", None))
        self.comb_graphviz_engine.setItemText(1, QCoreApplication.translate("MainWindow", u"circo", None))
        self.comb_graphviz_engine.setItemText(2, QCoreApplication.translate("MainWindow", u"fdp", None))

        self.pb_graphviz_script.setText(QCoreApplication.translate("MainWindow", u"Generate GraphViz script", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"GraphViz script", None))
        self.lb_flow_chart.setText("")
        self.pb_save_gv.setText(QCoreApplication.translate("MainWindow", u"Save script", None))
        self.pb_clear_script.setText(QCoreApplication.translate("MainWindow", u"Clear script", None))
        self.pb_clear_diagram.setText(QCoreApplication.translate("MainWindow", u"Clear diagram", None))
        self.pb_save_png.setText(QCoreApplication.translate("MainWindow", u"Save diagram as PNG", None))
        self.pb_save_svg.setText(QCoreApplication.translate("MainWindow", u"Save diagram as SVG", None))
        self.pb_flow_diagram.setText(QCoreApplication.translate("MainWindow", u"Generate flow diagram", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Path to the <span style=\" font-weight:600;\">dot</span> program (leave empty if dot is on the path)</p></body></html>", None))
        self.pb_browse_dot_path.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_flow_diagram), QCoreApplication.translate("MainWindow", u"Flow diagram", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Excluded transitions", None))
        self.pb_exclude_repetition.setText(QCoreApplication.translate("MainWindow", u"Exclude repeated behaviors", None))
        self.pb_clear_excluded_transitions.setText(QCoreApplication.translate("MainWindow", u"Clear excluded transitions", None))
        self.cb_block_first_behavior.setText(QCoreApplication.translate("MainWindow", u"Block first behavior", None))
        self.cb_block_last_behavior.setText(QCoreApplication.translate("MainWindow", u"Block last behavior", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Number of permutations", None))
        self.leNumberRandomizations.setText(QCoreApplication.translate("MainWindow", u"100", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Number of cores to use", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u" (default: total number of cores -1)", None))
        self.pb_run_permutations_test.setText(QCoreApplication.translate("MainWindow", u"Run random permutations test", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"P-value matrix", None))
        self.pb_save_random.setText(QCoreApplication.translate("MainWindow", u"Save significativity matrix", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_randomization), QCoreApplication.translate("MainWindow", u"Random permutations test", None))
        self.pb_levenshtein.setText(QCoreApplication.translate("MainWindow", u"Levenshtein distances", None))
        self.pb_needleman_wunsch.setText(QCoreApplication.translate("MainWindow", u"Needleman-Wunsch identities", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Results", None))
        self.pb_save_distances.setText(QCoreApplication.translate("MainWindow", u"Save results", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Behavioral sequence comparision", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp_2.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

