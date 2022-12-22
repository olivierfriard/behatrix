"""
Behatrix
Behavioral sequences analysis with permutations test

Copyright 2017-2022 Olivier Friard

This file is part of Behatrix.

  Behatrix is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  any later version.

  Behatrix is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not see <http://www.gnu.org/licenses/>.

"""

import concurrent.futures
import math
import multiprocessing
import os
import pathlib as pl
import platform
import subprocess
import sys
import tempfile
from shutil import copyfile
import traceback
import logging
import datetime as dt

import numpy as np
from PyQt5 import QtSvg
from PyQt5.QtCore import QSettings, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QMenu

from . import behatrix_functions
from . import behatrix_qrc
from . import version
from .behatrix_ui import Ui_MainWindow

# set logging
logging.basicConfig(
    format="%(asctime)s,%(msecs)d  %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)


class MainWindow(QMainWindow, Ui_MainWindow):

    permutations_finished_signal = pyqtSignal(list)

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        sys.excepthook = self.excepthook

        self.setWindowIcon(QIcon(":/logo"))

        self.setWindowTitle("Behatrix - Behavioral Sequences Analysis")

        self.svg_display = QtSvg.QSvgWidget()
        self.script_diagram_splitter.insertWidget(2, self.svg_display)

        self.lb_flow_chart.deleteLater()
        self.lb_flow_chart = None

        # self.vertical_splitter.setStretchFactor(1, 10)
        self.script_diagram_splitter.setStretchFactor(1, 1)

        self.pte_statistics.setLineWrapMode(False)
        self.pte_gv_edges.setLineWrapMode(False)
        self.pte_random.setLineWrapMode(False)

        self.pb_clear_behavioral_strings.clicked.connect(self.clear_sequences)

        # set to behavioral sequences tab
        self.tabWidget.setCurrentIndex(0)

        # connections

        self.actionLoad_behavioral_sequences.triggered.connect(self.load_file_content)
        self.actionQuit.triggered.connect(QApplication.quit)
        self.actionAbout.triggered.connect(self.about)

        # behavioral sequences

        # add menu to save results button
        save_results_menu_items = [
            "Save the descriptive statistics|Descriptive statistics",
            "Save the observed transitions|Observed transitions",
        ]

        menu_data = QMenu()
        menu_data.triggered.connect(lambda x: self.save_results(mode=x.statusTip()))
        self.add_button_menu(save_results_menu_items, menu_data)
        self.pb_save_results.setMenu(menu_data)

        # self.pb_save_results.clicked.connect(self.save_results)
        self.pb_save_results.setVisible(False)
        self.pte_behav_seq.textChanged.connect(self.behavioral_sequences_changed)
        self.sb_ngram.valueChanged.connect(self.behavioral_sequences_changed)
        self.le_behaviors_separator.textChanged.connect(self.behavioral_sequences_changed)
        self.cb_remove_repeated_behaviors.stateChanged.connect(self.behavioral_sequences_changed)

        # tab flow diagram
        self.rb_percent_after_behav.toggled.connect(self.flow_diagram_parameters_changed)
        self.sb_cutoff_transition_after_behav.valueChanged.connect(self.flow_diagram_parameters_changed)
        self.rb_percent_total_transitions.toggled.connect(self.flow_diagram_parameters_changed)
        self.sb_cutoff_total_transition.valueChanged.connect(self.flow_diagram_parameters_changed)
        self.sb_decimals.valueChanged.connect(self.flow_diagram_parameters_changed)
        self.comb_graphviz_engine.currentIndexChanged.connect(self.flow_diagram_parameters_changed)
        self.pb_graphviz_script.clicked.connect(self.flow_diagram_parameters_changed)
        self.pb_save_gv.clicked.connect(self.save_gv)
        self.pb_flow_diagram.clicked.connect(lambda: self.flow_diagram(action="show"))
        self.pb_clear_script.clicked.connect(self.clear_script)
        self.pb_clear_diagram.clicked.connect(self.clear_diagram)
        self.pb_browse_dot_path.clicked.connect(self.browse_dot_path)

        self.pb_save_png.setVisible(False)

        self.pb_save_svg.clicked.connect(lambda: self.flow_diagram(action="save"))

        # tab permutations test
        self.pb_exclude_repetition.clicked.connect(self.exclude_behavior_repetitions)
        self.pb_clear_excluded_transitions.clicked.connect(self.pte_excluded_transitions.clear)
        self.pb_run_permutations_test.clicked.connect(self.permutation_test)
        self.pb_save_random.clicked.connect(self.save_permutations_test_results)
        self.pte_behav_seq.setLineWrapMode(0)
        num_available_proc = os.cpu_count()
        self.sb_nb_cores.setMinimum(1)
        self.sb_nb_cores.setMaximum(num_available_proc)
        if num_available_proc <= 2:
            self.sb_nb_cores.setValue(1)
        else:
            self.sb_nb_cores.setValue(num_available_proc - 1)

        # tab distances
        self.pb_levenshtein.clicked.connect(self.levenshtein_distance)
        self.pb_needleman_wunsch.clicked.connect(self.needleman_wunsch_identity)
        self.pb_save_distances.clicked.connect(self.save_distances_results)
        self.pte_distances_results.setLineWrapMode(0)

        self.permutations_test_matrix = None

        self.cb_plot_significativity.setEnabled(False)

        self.le_dot_path.setReadOnly(True)

        config_file_path = str(pl.Path(os.path.expanduser("~")) / ".behatrix")
        if pl.Path(config_file_path).is_file():
            settings = QSettings(config_file_path, QSettings.IniFormat)
            if settings.value("dot_prog_path"):
                # test dot program from settings
                if self.test_dot_program(settings.value("dot_prog_path")):
                    self.le_dot_path.setText(settings.value("dot_prog_path"))
                else:
                    QMessageBox.critical(
                        self,
                        "Behatrix",
                        f"The <b>dot</b> program is not working. Check <b>{settings.value('dot_prog_path')}</b>.<br>",
                    )
            else:
                self.check_dot_path()
        else:
            self.check_dot_path()

        self.permutations_finished_signal.connect(self.get_permutations_results)
        self.mem_behaviours = ""

        self.sb_cutoff_transition_after_behav.setEnabled(self.rb_percent_after_behav.isChecked())
        self.sb_cutoff_total_transition.setEnabled(self.rb_percent_total_transitions.isChecked())


    def excepthook(self, exception_type, exception_value, traceback_object):
        """
        global error management
        """

        error_text: str = (
            f"Behatrix version: {version.__version__}\n"
            f"OS: {platform.uname().system} {platform.uname().release} {platform.uname().version}\n"
            f"CPU: {platform.uname().machine} {platform.uname().processor}\n"
            f"Python {platform.python_version()} ({'64-bit' if sys.maxsize > 2**32 else '32-bit'})\n"
            # f"Qt {QT_VERSION_STR} - PyQt {PYQT_VERSION_STR}\n"
            f"{dt.datetime.now():%Y-%m-%d %H:%M}\n\n"
        )
        error_text += "".join(traceback.format_exception(exception_type, exception_value, traceback_object))

        logging.critical(error_text)

        # append to behatrix.log file
        with open(pl.Path("~").expanduser() / "behatrix.log", "a") as f_out:
            f_out.write(error_text + "\n")
            f_out.write("-" * 80 + "\n")

        # copy to clipboard
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(error_text, mode=cb.Clipboard)

        error_text: str = error_text.replace("\r\n", "\n").replace("\n", "<br>")

        text: str = (
            f"<b>An error has occured</b>:<br><br>"
            f"{error_text}<br>"
            "to improve the software please report this problem at:<br>"
            '<a href="https://github.com/olivierfriard/behatrix/issues">'
            "https://github.com/olivierfriard/behatrix/issues</a><br>"
            "Please no screenshot (the error message was copied to the clipboard).<br><br>"
            "Thank you for your collaboration!"
        )

        errorbox = QMessageBox()
        errorbox.setWindowTitle("Behatrix error occured")
        errorbox.setText(text)
        errorbox.setTextFormat(Qt.RichText)
        errorbox.setStandardButtons(QMessageBox.Abort)

        _ = errorbox.addButton("Ignore and try to continue", QMessageBox.RejectRole)

        ret = errorbox.exec_()

        if ret == QMessageBox.Abort:
            sys.exit(1)

    def add_button_menu(self, data, menu_obj):
        """
        add menu option from dictionary
        """
        if isinstance(data, dict):
            for k, v in data.items():
                sub_menu = QMenu(k, menu_obj)
                menu_obj.addMenu(sub_menu)
                self.add_button_menu(v, sub_menu)
        elif isinstance(data, list):
            for element in data:
                self.add_button_menu(element, menu_obj)
        else:
            action = menu_obj.addAction(data.split("|")[1])
            # tips are used to discriminate the menu option
            action.setStatusTip(data.split("|")[0])
            action.setIconVisibleInMenu(False)

    def about(self):
        """
        Display the about dialog
        """

        about_dialog = QMessageBox()
        about_dialog.setIconPixmap(QPixmap(":/behatrix_unito_logo"))
        about_dialog.setWindowTitle("About Behatrix")
        about_dialog.setStandardButtons(QMessageBox.Ok)
        about_dialog.setDefaultButton(QMessageBox.Ok)
        about_dialog.setEscapeButton(QMessageBox.Ok)

        about_dialog.setInformativeText(
            (
                f"<b>Behatrix</b> {version.__version__} - {version.__version_date__}"
                "<p>Copyright &copy; 2017-2022 Olivier Friard - Marco Gamba - Sergio Castellano<br>"
                "Department of Life Sciences and Systems Biology<br>"
                "University of Torino - Italy<br>"
                "<br>"
                'Behatrix is released under the <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License v.3</a><br>'
                'See <a href="http://www.boris.unito.it/pages/behatrix">www.boris.unito.it/pages/behatrix</a> for more details.<br>'
                "<hr>"
            )
        )
        _ = about_dialog.exec_()

    def check_dot_path(self) -> bool:
        """
        check if dot program is available on path
        if available set the self.le_dot_path widget with the path

        Returns:
            bool: True if dot found on the path
        """

        if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
            process = subprocess.Popen("which dot", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        elif sys.platform.startswith("win"):
            process = subprocess.Popen("where dot", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
            self.le_dot_path.setText(f"Platform {sys.platform} NOT found")
            return False
        output, _ = process.communicate()

        if output.decode("utf-8").strip():
            if self.test_dot_program(output.decode("utf-8").strip()):
                self.le_dot_path.setText(output.decode("utf-8").strip())
                return True
            else:
                self.le_dot_path.setText("")
                self.le_dot_path.setStyleSheet("background-color: red")
                return False
        else:
            self.le_dot_path.setText("")
            self.le_dot_path.setStyleSheet("background-color: red")

            return False

    def closeEvent(self, event):
        settings = QSettings(str(pl.Path(os.path.expanduser("~")) / ".behatrix"), QSettings.IniFormat)
        settings.setValue("dot_prog_path", self.le_dot_path.text())

    def clear_sequences(self):
        """
        delete all behavioral sequences
        """
        self.pte_behav_seq.clear()
        self.pte_statistics.clear()
        self.pte_observed_transitions.clear()
        self.pb_save_results.setVisible(False)

    def behavioral_sequences_changed(self):
        """
        behavioral sequences changed by user

        update statistic, onserved matrix, graphviz script and flow diagram
        """

        self.permutations_test_matrix = None
        self.cb_plot_significativity.setEnabled(False)
        for w in [self.pte_statistics, self.pte_gv_edges, self.pte_random, self.pte_distances_results]:
            w.clear()
        # plot significativity
        self.cb_plot_significativity.setEnabled(False)
        self.cb_plot_significativity.setChecked(False)
        # test if | separator present

        """
        if "|" in self.pte_behav_seq.toPlainText():
            self.le_behaviors_separator.setText("|")
        """

        self.behav_seq_statistics()

        self.observed_matrix()

        self.graphviz_script()

        self.flow_diagram()

    def flow_diagram_parameters_changed(self):
        """
        update flow diagram
        """

        self.sb_cutoff_transition_after_behav.setEnabled(self.rb_percent_after_behav.isChecked())
        self.sb_cutoff_total_transition.setEnabled(self.rb_percent_total_transitions.isChecked())

        self.graphviz_script()

        self.flow_diagram()

    def test_dot_program(self, dot_path: str) -> bool:
        """
        test if dot program is working
        """
        p = subprocess.Popen(f'"{dot_path}" -V', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        _, error = p.communicate()

        return b"graphviz version" in error

    def browse_dot_path(self):
        """
        browse for dot program path
        """
        filename = QFileDialog(self).getOpenFileName(
            self, "Select the dot program from GraphViz package", "", "All files (*)"
        )[0]
        if filename:
            if self.test_dot_program(filename):
                self.le_dot_path.setText(filename)
                self.le_dot_path.setStyleSheet("")
                self.statusbar.showMessage(f"", 0)
                self.flow_diagram()

            else:
                QMessageBox.critical(
                    self, "Behatrix", f"The selected <b>dot</b> program is not working.<br>Check <b>{filename}</b>"
                )

    def load_file_content(self):
        """
        Load file content as sequences
        """

        filename = QFileDialog().getOpenFileName(
            self, "Select the file containing the behavioral sequences", "", "All files (*)"
        )[0]

        if filename:
            try:
                with open(filename) as f_in:
                    behav_str = f_in.read()
            except Exception:
                QMessageBox.critical(self, "Behatrix", "The selected file is not available.<br>")
                return

            self.pte_behav_seq.setPlainText(behav_str)

    def behav_seq_statistics(self):
        """
        statistics about behavioral sequences
        """

        if self.pte_behav_seq.toPlainText():

            results = behatrix_functions.behavioral_sequence_analysis(
                self.pte_behav_seq.toPlainText(),
                behaviors_separator=self.le_behaviors_separator.text(),
                chunk=0,
                flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked(),
                ngram=self.sb_ngram.value(),
            )

            output = ""
            output += f"Number of sequences: {len(results['sequences'])}\n\n"

            output += "\nStatistics\n==========\n"
            output += f"Number of different behaviours: {len(results['behaviours'])}\n"
            output += f"Total number of behaviours: {results['tot_nodes']}\n"
            output += f"Number of different transitions: {len(results['transitions'])}\n"
            output += f"Total number of transitions: {results['tot_trans']}\n"
            output += "\nBehaviours list:\n================\n{}\n".format("\n".join(results["behaviours"]))
            output += "\nBehaviours frequencies:\n=======================\n"

            for behaviour in sorted(results["behaviours"]):
                countBehaviour = 0
                for seq in results["sequences"]:
                    countBehaviour += seq.count(behaviour)

                output += f"{behaviour}\t{countBehaviour / results['tot_nodes']:.3f}\t{countBehaviour} / {results['tot_nodes']}\n"

            # n-grams
            if self.sb_ngram.value() > 1:
                output += f"\nFrequencies of {self.sb_ngram.value()}-grams:\n=======================\n"
                output += results["out_ngrams"]

            self.pte_statistics.setPlainText(output)

            # self.pb_save_results.setText("Save statistics")
            self.pb_save_results.setVisible(True)

    def save_results(self, mode):
        """
        save results on file (statistic and observed transitions matrix)
        """
        print(mode)
        if self.pte_statistics.toPlainText() == "" and self.pte_observed_transitions.toPlainText() == "":
            QMessageBox.warning(self, "Behatrix", "No results to save!")
            return

        file_name = QFileDialog(self).getSaveFileName(self, "Select the file to save the results", "", "All files (*)")[
            0
        ]
        if file_name:
            if mode == "Save the descriptive statistics":
                try:
                    with open(file_name, "w") as f_out:
                        f_out.write(self.pte_statistics.toPlainText())
                except Exception:
                    QMessageBox.critical(self, "Behatrix", "Descriptive statistics not saved!")

            if mode == "Save the observed transitions":
                try:
                    with open(file_name, "w") as f_out:
                        f_out.write(self.pte_observed_transitions.toPlainText())
                except Exception:
                    QMessageBox.critical(self, "Behatrix", "Observed transitions not saved!")

    def observed_matrix(self):
        """
        matrix of observed transitions
        """

        if self.pte_behav_seq.toPlainText():
            results = behatrix_functions.behavioral_sequence_analysis(
                self.pte_behav_seq.toPlainText(),
                behaviors_separator=self.le_behaviors_separator.text(),
                chunk=0,
                flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked(),
            )

            observed_matrix = behatrix_functions.create_observed_transition_matrix(
                results["sequences"], results["behaviours"]
            )

            # display results
            # header
            behaviours_str = "\t".join(list(results["behaviours"]))
            out = f"\t{behaviours_str}\n"

            for r in range(observed_matrix.shape[0]):
                out += f"{results['behaviours'][r]}\t"
                out += "\t".join([str(int(x)) for x in observed_matrix[r, :]]) + "\n"

            self.pte_observed_transitions.setPlainText(out)

            # self.pb_save_results.setText("Save transition matrix")
            self.pb_save_results.setVisible(True)

    def graphviz_script(self):
        """
        generate GraphViz script
        """

        if not self.pte_behav_seq.toPlainText():
            return

        if '"' in self.pte_behav_seq.toPlainText():
            QMessageBox.critical(self, "Behatrix", 'The double quotes (") are not allowed in behaviors')
            return

        results = behatrix_functions.behavioral_sequence_analysis(
            self.pte_behav_seq.toPlainText(),
            behaviors_separator=self.le_behaviors_separator.text(),
            chunk=0,
            flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked(),
        )

        # type of labels
        edge_label = "percent_node"
        if self.rb_percent_after_behav.isChecked():
            edge_label = "percent_node"
        if self.rb_percent_total_transitions.isChecked():
            edge_label = "percent_total"
        """
        if self.rb_fraction_after_behav.isChecked():
            edge_label = "fraction_node"
        """

        # check significativity
        if self.cb_plot_significativity.isChecked() and self.permutations_test_matrix is None:
            QMessageBox.critical(
                self, "Behatrix", "Adding significativity to graph requires p values from permutations test"
            )
            return

        (header_out, nodes_out, edges_out, graph_out, footer_out, nodes_list) = behatrix_functions.draw_diagram(
            cutoff_all=self.sb_cutoff_total_transition.value() if self.rb_percent_total_transitions.isChecked() else None,
            cutoff_behavior=self.sb_cutoff_transition_after_behav.value() if self.rb_percent_after_behav.isChecked() else None,
            unique_transitions=results["transitions"],
            nodes=results["nodes"],
            starting_nodes=[],
            tot_nodes=results["tot_nodes"],
            tot_trans=results["tot_trans"],
            tot_trans_after_node=results["tot_trans_after_node"],
            edge_label=edge_label,
            decimals_number=self.sb_decimals.value(),
            significativity=self.permutations_test_matrix
            if (self.permutations_test_matrix is not None) and (self.cb_plot_significativity.isChecked())
            else None,
            behaviors=results["behaviours"],
        )

        if nodes_list != self.mem_behaviours:
            self.pte_gv_nodes.setPlainText(nodes_out)

        self.pte_gv_edges.setPlainText(edges_out)

        if self.pte_gv_graph.toPlainText() == "":
            self.pte_gv_graph.setPlainText(graph_out)

        self.mem_behaviours = nodes_list

    def save_gv(self):
        """
        save GV script to file
        """
        if self.pte_gv_edges.toPlainText():

            file_name, filter_ = QFileDialog().getSaveFileName(
                self,
                "Select the file to save the GraphViz script",
                "",
                "GV files (*.gv);;TXT files (*.txt);;All files (*)",
            )

            if file_name:
                try:
                    with open(file_name, "w") as f_out:
                        f_out.write('digraph G {\n')
                        f_out.write(self.pte_gv_nodes.toPlainText() + '\n')
                        f_out.write(self.pte_gv_edges.toPlainText()+ '\n')
                        f_out.write(self.pte_gv_graph.toPlainText()+ '\n')
                        f_out.write('}\n')
                except Exception:
                    QMessageBox.critical(self, "Behatrix", "Results not saved!")

    def flow_diagram(self, action: str = "show") -> str:
        """
        generate flow diagram from pte_gv_nodes, pte_gv_edges and pte_gv_graph contents in SVG format
        with:
            dot program from graphviz package
            or
            viz.js javascript and nodejs

        Args:
            action (str): "show" or "save"

        Returns:
            str: path of diagram temp file path or "" in case of error
        """

        if not self.pte_gv_edges.toPlainText() and not self.pte_gv_nodes.toPlainText():
            return

        # check dot path
        # self.check_dot_path()
        if not self.le_dot_path.text():
            if not self.check_dot_path():
                self.statusbar.showMessage(f"dot program not found", 0)
                return ""

        elif not self.test_dot_program(self.le_dot_path.text()):
            self.statusbar.showMessage(f"{self.le_dot_path.text()} is not working", 0)
            return ""
        dot_path = self.le_dot_path.text()

        # test dot program
        p = subprocess.Popen(f'"{dot_path}" -V', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, error = p.communicate()

        if b"graphviz version" in error:

            if sys.platform.startswith("win"):

                gv_script_temp_file = pl.Path(tempfile.gettempdir()) / pl.Path("gv_script.gv")
                output_temp_file = pl.Path(tempfile.gettempdir()) / pl.Path("flow_diagram.svg")
                try:
                    with gv_script_temp_file.open("w", encoding="utf-8") as f:
                        f.write(
                            (
                                "digraph G {"
                                f"{self.pte_gv_nodes.toPlainText()}"
                                f"{self.pte_gv_edges.toPlainText()}"
                                f"{self.pte_gv_graph.toPlainText()}"
                                "}"
                            )
                        )
                except:
                    QMessageBox.critical(self, "Behatrix", "Error during flow diagram generation!")
                    return

                graphviz_engine = str(pl.Path(dot_path).parent / pl.Path(self.comb_graphviz_engine.currentText()))

                cmd = f'"{graphviz_engine}" -Tsvg "{gv_script_temp_file}" -o "{output_temp_file}"'
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                _, error = p.communicate()
                if error:
                    QMessageBox.critical(self, "Behatrix", error.decode("utf-8"))
                    return
                out = output_temp_file.read_bytes()
            else:
                gv_script = (
                    "digraph G {"
                    + self.pte_gv_nodes.toPlainText().replace("\n", " ").replace("'", "'\\''")
                    + self.pte_gv_edges.toPlainText().replace("\n", " ").replace("'", "'\\''")
                    + self.pte_gv_graph.toPlainText().replace("\n", " ").replace("'", "'\\''")
                    + "}"
                )

                print(pl.Path(dot_path).parent)
                if self.comb_graphviz_engine.currentText() == 'dot':
                    graphviz_engine = dot_path
                else:
                    graphviz_engine = str(pl.Path(dot_path).parent / pl.Path(self.comb_graphviz_engine.currentText()))

                cmd = f"""echo '{gv_script}' | "{graphviz_engine}" -Tsvg """

                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, error = p.communicate()

                if error:
                    QMessageBox.critical(self, "Behatrix", error.decode("utf-8"))
                    return

        else:
            QMessageBox.critical(self, "Behatrix", error.decode("utf-8"))
            return

        """
        if self.rb_vizjs.isChecked():

            # test if viz.js and nodejs found
            # script directory
            print("sys.argv[0]", sys.argv[0])
            print("sys.argv[0].resolve()", pathlib.Path(sys.argv[0]).resolve())
            # print("sys.path", sys.path)

            viz_path = pathlib.Path("")
            if sys.argv[0].endswith("start_behatrix.py"):
                viz_path = pathlib.Path(sys.argv[0]).resolve().parent / "behatrix" / "misc" / "viz.js"

            if sys.argv[0].endswith("__main__.py"):
                viz_path = pathlib.Path(sys.argv[0]).resolve().parent / "misc" / "viz.js"

            print(f"viz.js path: {viz_path}")
            if not viz_path.is_file():
                QMessageBox.critical(self, "Behatrix", "The viz.js file was not found!")
                return
            viz_path = str(viz_path).replace("\\", "/")

            # node (nodejs)
            node_cmd_list = []
            # embedded nodejs version (packages)
            if sys.argv[0].endswith("__main__.py"):
                if sys.platform == "win32":
                    node_cmd_list.append(str(pathlib.Path(sys.argv[0]).parent / "misc" / "node.exe"))
                if sys.platform in ["darwin", "linux"]:
                    node_cmd_list.append(str(pathlib.Path(sys.argv[0]).parent / "misc" / "node"))

            if sys.argv[0].endswith("start_behatrix.py"):
                if sys.platform == "win32":
                    node_cmd_list.append(
                        str(pathlib.Path(sys.argv[0]).resolve().parent / "behatrix" / "misc" / "node.exe")
                    )
                if sys.platform in ["darwin", "linux"]:
                    node_cmd_list.append(str(pathlib.Path(sys.argv[0]).resolve().parent / "behatrix" / "misc" / "node"))

            # global installation of nodeJS
            node_cmd_list.extend(["node", "/usr/local/bin/node"])
            node_cmd_verified = ""
            for node_cmd in node_cmd_list:
                p = subprocess.Popen(f"{node_cmd} -v", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, error = p.communicate()
                if not error and out.decode("utf-8") and out.decode("utf-8")[0] == "v":
                    node_cmd_verified = node_cmd
                    break

            if not node_cmd_verified:
                QMessageBox.critical(
                    self,
                    "Behatrix",
                    (
                        "The Node.js JavaScript runtime was not found!\n"
                        "Please install it or switch to the Graphviz package"
                    ),
                )
                return

            print(f"node_cmd_verified {node_cmd_verified}")

            # escape for echo and nodejs
            gv_script_escaped = (
                self.pte_gv_edges.toPlainText().replace("\n", " ").replace('"', '\\"').replace("'", "'\\''")
            )

            js = f'var data = "{gv_script_escaped}"; var viz = require("{viz_path}"); var svg = viz.Viz(data, "svg"); console.log(svg);'

            print(tempfile.gettempdir())
            js_script_path = pathlib.Path(tempfile.gettempdir()) / pathlib.Path("behatrix_flow_diagram_script.js")
            open(js_script_path, "w").write(js)

            cmd = f"{node_cmd_verified} {js_script_path}"
            print(f"cmd: {cmd}")

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            out, error = p.communicate()

            if error:
                QMessageBox.critical(self, "Behatrix", error.decode("utf-8"))
                return
            else:
                self.svg_display.load(out)
        """

        if action == "show":
            self.svg_display.load(out)

        if action == "save":
            file_name, filter_ = QFileDialog().getSaveFileName(
                self, "Select the file and format to save the flow diagram", "", "SVG files (*.svg);;All files (*)"
            )
            if file_name:
                try:
                    with open(file_name, "w") as f_out:
                        f_out.write(out.decode("utf-8"))
                except Exception:
                    QMessageBox.critical(self, "Behatrix", "Error saving the file")
                    return

                self.svg_display.load(out)

    def clear_script(self):
        """
        clear script window
        """

        self.pte_gv_edges.clear()
        self.svg_display.load(b"")

    def clear_diagram(self):
        """
        clear diagram
        """

        self.svg_display.load(b"")

    def save_diagram(self, image_format):
        """
        save diagram
        """
        if self.pte_gv_edges.toPlainText():
            file_name, filter_ = QFileDialog().getSaveFileName(
                self,
                "Select the file and format to save the flow diagram",
                "",
                "PNG files (*.png);;All files (*)" if image_format == "png" else "SVG files (*.svg);;All files (*)",
            )
            diagram_tmp_file_path = self.flow_diagram(image_format=image_format)
            if diagram_tmp_file_path and file_name:
                copyfile(diagram_tmp_file_path, file_name)
        else:
            QMessageBox.warning(self, "Behatrix", "No GV script found. Generate the GraphViz script first.")

    def exclude_behavior_repetitions(self):
        """
        insert repetition of same behavior in exclusions list
        """
        results = behatrix_functions.behavioral_sequence_analysis(
            self.pte_behav_seq.toPlainText(), behaviors_separator=self.le_behaviors_separator.text(), chunk=0
        )
        self.pte_excluded_transitions.insertPlainText("\n")
        for behavior in results["behaviours"]:
            self.pte_excluded_transitions.insertPlainText(f"{behavior}:{behavior}\n")

    def get_permutations_results(self, results):
        """
        handle results of permutations test
        """

        self.pb_run_permutations_test.setEnabled(True)
        nb_randomization_done = 0
        permutation_results = np.zeros((len(self.behaviours), len(self.behaviours)))
        for n_permut, result in results:
            nb_randomization_done += n_permut
            permutation_results += result

        out = "\t{}\n".format("\t".join(list(self.behaviours)))

        self.permutations_test_matrix = permutation_results / nb_randomization_done

        for r in range(self.permutations_test_matrix.shape[0]):
            out += f"{self.behaviours[r]}\t"
            out += "\t".join(["%8.6f" % x for x in self.permutations_test_matrix[r, :]]) + "\n"

        self.pte_random.setPlainText(out)

        self.statusbar.showMessage("", 0)

        self.cb_plot_significativity.setEnabled(True)

        QMessageBox.information(
            self, "Behatrix", ("Permutations test finished<br>" f"{nb_randomization_done} permutations done<br><br>")
        )

    def permutations_test_finished(self, results):
        """
        permutations test finished
        """
        self.permutations_finished_signal.emit(results)

    def permutation_test(self):
        """
        execute permutations test
        """

        if self.pte_behav_seq.toPlainText():
            self.pte_random.clear()

            results = behatrix_functions.behavioral_sequence_analysis(
                self.pte_behav_seq.toPlainText(),
                behaviors_separator=self.le_behaviors_separator.text(),
                chunk=0,
                flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked(),
            )

            self.behaviours = results["behaviours"]

            # check exclusion list
            if self.pte_excluded_transitions.toPlainText():
                result = behatrix_functions.check_exclusion_list(
                    self.pte_excluded_transitions.toPlainText(), results["sequences"]
                )

                if not result["error_code"]:
                    exclusion_list = result["exclusion_list"]
                else:
                    QMessageBox.warning(self, "Behatrix", result["message"])
                    return
            else:
                exclusion_list = {}

            if self.leNumberRandomizations.text():
                try:
                    self.nrandom = int(self.leNumberRandomizations.text())
                except Exception:
                    self.nrandom = 0
                    QMessageBox.warning(self, "Behatrix", "The number of permutations is not valid")
                    return

            if self.nrandom:

                self.statusbar.showMessage("Permutations test running... Be patient", 0)

                num_proc = self.sb_nb_cores.value()

                if num_proc > self.nrandom:
                    num_proc = self.nrandom

                observed_matrix = behatrix_functions.create_observed_transition_matrix(
                    results["sequences"], self.behaviours
                )

                self.pb_run_permutations_test.setEnabled(False)
                self.nb_randomization_done = 0
                pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

                n_random_by_proc = round(self.nrandom / num_proc + 1)

                pool.starmap_async(
                    behatrix_functions.permutations_test,
                    [
                        (
                            n_random_by_proc,
                            results["sequences"],
                            self.behaviours,
                            exclusion_list,
                            self.cb_block_first_behavior.isChecked(),
                            self.cb_block_last_behavior.isChecked(),
                            observed_matrix,
                        )
                    ]
                    * num_proc,
                    callback=self.permutations_test_finished,
                )

            else:
                QMessageBox.warning(self, "Behatrix", "Select the number of permutations to execute")

        else:
            QMessageBox.warning(self, "Behatrix", "No behavioral sequences found!")

    def save_permutations_test_results(self):
        """
        Save permutations test matrix
        """
        if self.pte_random.toPlainText():

            file_name, filter_ = QFileDialog().getSaveFileName(
                self, "Select the file to save the results", "", "TSV files (*.tsv);;TXT files (*.txt);;All files (*)"
            )

            if file_name:
                try:
                    with open(file_name, "w") as f_out:
                        f_out.write(self.pte_random.toPlainText())
                except Exception:
                    QMessageBox.critical(self, "Behatrix", "Results not saved!")

    def levenshtein_distance(self):
        """
        Levenshtein distances between behavioral sequences
        """

        seq_list = [x.strip() for x in self.pte_behav_seq.toPlainText().split("\n") if x.strip()]
        n_pad = int(math.log10(len(seq_list))) + 1

        if self.le_behaviors_separator.text():
            seq_list = [x.split(self.le_behaviors_separator.text()) for x in seq_list]

        results = behatrix_functions.levenshtein_distance_seq_list(seq_list)

        # display results
        out = "Levenshtein distances:\n"
        # header
        out += "\t{}\n".format("\t".join([f"seq{x + 1:0{n_pad}}" for x, _ in enumerate(seq_list)]))
        for r in range(results.shape[0]):
            out += f"seq{r + 1:0{n_pad}}\t"
            out += "\t".join([f"{int(x)}" for x in results[r, :]]) + "\n"

        self.pte_distances_results.setPlainText(out)

    def needleman_wunsch_identity(self):
        """
        Needleman-Wunsch identities between behavioral sequences
        """

        seq_list = [x.strip() for x in self.pte_behav_seq.toPlainText().split("\n") if x.strip()]
        n_pad = int(math.log10(len(seq_list))) + 1

        if self.le_behaviors_separator.text():
            seq_list = [x.split(self.le_behaviors_separator.text()) for x in seq_list]

        results = behatrix_functions.needleman_wunsch_identity_seq_list(seq_list)

        # display results
        out = "Needleman-Wunsch identities:\n"
        # header
        out += "\t{}\n".format("\t".join([f"seq{x + 1:0{n_pad}}" for x, _ in enumerate(seq_list)]))
        for r in range(results.shape[0]):
            out += f"seq{r + 1:0{n_pad}}\t"
            out += "\t".join([f"{x:.2f}" for x in results[r, :]]) + "\n"

        self.pte_distances_results.setPlainText(out)

    def save_distances_results(self):
        """
        Save distances matrix
        """
        if self.pte_distances_results.toPlainText():

            file_name, filter_ = QFileDialog().getSaveFileName(
                self, "Select the file to save the results", "", "TSV files (*.tsv);;TXT files (*.txt);;All files (*)"
            )

            if file_name:
                try:
                    with open(file_name, "w") as f_out:
                        f_out.write(self.pte_distances_results.toPlainText())
                except Exception:
                    QMessageBox.critical(self, "Behatrix", "Results not saved!")


def main():

    app = QApplication(sys.argv)
    app.setApplicationName("Behatrix")
    mainWindow = MainWindow()
    mainWindow.show()
    mainWindow.raise_()
    sys.exit(app.exec_())


def cli():

    import argparse

    parser = argparse.ArgumentParser(
        prog="Behatrix",
        usage="\npython3 -m behatrix [options]",
        description="Behatrix command line utility",
        epilog="See http://www.boris.unito.it/pages/behatrix for details :-)",
    )
    parser.add_argument("-v", "--version", action="store_true", dest="version", help="Behatrix version")
    parser.add_argument(
        "-s", "--sequences", action="store", dest="sequences", help="Path of file containing behavioral sequences"
    )
    parser.add_argument("--separator", action="store", dest="separator", default="", help="Separator of behaviors")
    parser.add_argument("-o", "--output", action="store", dest="output", help="Path of output files")
    parser.add_argument("--exclusions", action="store", dest="exclusions", help="Path of file containing exclusions")
    parser.add_argument(
        "--n-random", action="store", dest="nrandom", help="Number of permutations", type=int, default=0
    )
    parser.add_argument(
        "--n-cpu", action="store", dest="n_cpu", help="Number of CPU to use for permutations test", type=int, default=0
    )
    parser.add_argument(
        "--block-first", action="store_true", dest="block_first", help="block first behavior during permutations test"
    )
    parser.add_argument(
        "--block-last", action="store_true", dest="block_last", help="block last behavior during permutations test"
    )
    parser.add_argument(
        "--no-repetition",
        action="store_true",
        dest="no_repetition",
        help="exclude repetitions during permutations test",
    )
    parser.add_argument("--n-gram", action="store", default=1, dest="ngram", help="n-gram value", type=int)

    parser.add_argument(
        "-q", "--quiet", action="store_true", dest="quiet", default=False, help="Do not print results on terminal"
    )

    args = parser.parse_args()

    if args.version:
        print("Copyright (C) 2017-2022 Olivier Friard")
        print(f"version {version.__version__} - {version.__version_date__}")
        sys.exit()

    if not args.sequences:
        print("The 'sequences' argument is required\n")
        parser.print_usage()
        print()
        sys.exit()
    else:
        if not os.path.isfile(args.sequences):
            print(f"{args.sequences} is not a file\n")
            sys.exit()

    with open(args.sequences) as f_in:
        behav_str = f_in.read()

        results = behatrix_functions.behavioral_sequence_analysis(
            behav_str, behaviors_separator=args.separator, chunk=0, ngram=args.ngram
        )

    if args.nrandom:
        nrandom = args.nrandom
    else:
        nrandom = 0

    if nrandom:

        if args.exclusions:
            if not os.path.isfile(args.exclusions):
                print(f"{args.exclusions} is not a file\n")
                sys.exit()
            else:
                with open(args.exclusions) as f_in:
                    exclusion_str = f_in.read()
        else:
            exclusion_str = ""

        result = behatrix_functions.check_exclusion_list(exclusion_str, results["sequences"])
        if result["error_code"]:
            print(result["message"])
            return

        exclusion_list = result["exclusion_list"]

        block_first = 1 if args.block_first else 0
        block_last = 1 if args.block_last else 0

    if not args.quiet:
        sep = "\n"
        print(f"\nNumber of sequences: {len(results['sequences'])}")

        print(("\nBehaviours list\n" "===============\n" f"{sep.join(results['behaviours'])}\n"))

        print("Statistics\n==========")
        print(f"Number of different behaviours: {len(results['behaviours'])}")
        print(f"Total number of behaviours: {results['tot_nodes']}")
        print(f"Number of different transitions: {len(results['transitions'])}")
        print(f"Total number of transitions: {results['tot_trans']}")

        print("\nFrequencies of behaviors\n========================")

        for behaviour in sorted(results["behaviours"]):
            countBehaviour = 0
            for seq in results["sequences"]:
                countBehaviour += seq.count(behaviour)

            print(
                f"{behaviour}\t{countBehaviour / results['tot_nodes']:.3f}\t{countBehaviour} / {results['tot_nodes']}"
            )

        # n-grams
        if args.ngram > 1:
            print(f"\nFrequencies of {args.ngram}-grams\n======================")
            print(results["out_ngrams"])

    observed_matrix = behatrix_functions.create_observed_transition_matrix(results["sequences"], results["behaviours"])

    if not args.quiet:

        behaviours_str = "\t".join(list(results["behaviours"]))
        out = f"\t{behaviours_str}\n"
        for r in range(observed_matrix.shape[0]):
            out += f"{results['behaviours'][r]}\t"
            out += "\t".join([str(int(x)) for x in observed_matrix[r, :]]) + "\n"

        print(
            (
                "\nObserved transition matrix\n"
                "==========================\n"
                "(The bevahior in 1st column precedes the behavior in the 1st row)\n"
                f"{out}"
            )
        )

    if args.output:
        file_name = f"{args.output}.observed_transitions.tsv"
    else:
        file_name = f"{args.sequences}.observed_transitions.tsv"

    np.savetxt(file_name, observed_matrix, fmt="%d", delimiter="\t")

    with open(file_name, mode="r", encoding="utf-8") as f_in:
        rows = f_in.readlines()

    with open(file_name, mode="w", encoding="utf-8") as f_out:
        f_out.write("\t" + "\t".join(results["behaviours"]) + "\n")
        c = 0
        for row in rows:
            f_out.write((results["behaviours"])[c] + "\t" + row)
            c += 1

    # check if permutations test required
    if nrandom:

        if args.n_cpu:
            num_proc = args.n_cpu
        else:
            num_available_proc = os.cpu_count()
            if num_available_proc <= 2:
                num_proc = 1
            else:
                num_proc = num_available_proc - 1

        permutations_results = np.zeros((len(results["behaviours"]), len(results["behaviours"])))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            lst = []
            n_required_randomizations = 0
            for i in range(num_proc):

                if i < num_proc - 1:
                    n_random_by_proc = nrandom // num_proc
                else:
                    n_random_by_proc = nrandom - n_required_randomizations

                lst.append(
                    executor.submit(
                        behatrix_functions.permutations_test,
                        n_random_by_proc,
                        results["sequences"],
                        results["behaviours"],
                        exclusion_list,
                        block_first,
                        block_last,
                        observed_matrix,
                        args.no_repetition,
                    )
                )

                n_required_randomizations += n_random_by_proc

            if not args.quiet:
                print("\nPermutations test")
                print("=================")

                print(f"\nNumber of required permutations: {n_required_randomizations}")

            nb_randomization_done = 0

            for l in lst:
                nb_randomization_done += l.result()[0]
                permutations_results += l.result()[1]

        if not args.quiet:
            print(f"Number of permutations done: {nb_randomization_done}")

        matrix = permutations_results / nrandom

        if not args.quiet:
            print("\nP-value matrix")
            print("--------------\n")
            behaviours_str = "\t".join(list(results["behaviours"]))
            out = f"\t{behaviours_str}\n"
            for r in range(matrix.shape[0]):
                out += f"{results['behaviours'][r]}\t"
                out += "\t".join([f"{x:.3f}" for x in matrix[r, :]]) + "\n"

            print(out)

        if args.output:
            file_name = f"{args.output}.p-values.{nrandom}.tsv"
        else:
            file_name = f"{args.sequences}.p-values.{nrandom}.tsv"

        np.savetxt(file_name, permutations_results / nrandom, fmt="%f", delimiter="\t")

        try:
            with open(file_name, mode="r", encoding="utf-8") as f:
                rows = f.readlines()
            with open(file_name, mode="w", encoding="utf-8") as f:
                f.write("\t" + "\t".join(list(results["behaviours"])) + "\n")
                c = 0
                for row in rows:
                    f.write((results["behaviours"])[c] + "\t" + row)
                    c += 1
        except Exception:
            print(f"Error during creation of file: {file_name}")


if __name__ == "__main__":
    main()
