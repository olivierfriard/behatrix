#!/usr/bin/env python3


"""
Behatrix
Behavioral Sequences Analysis (BSA).

Behavioral sequences analysis with permutations test


Copyright 2017-2020 Olivier Friard

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
import multiprocessing
import os
import pathlib
import platform
import subprocess
import sys
import tempfile
from shutil import copyfile

import numpy as np
from PyQt5 import QtSvg
from PyQt5.QtCore import QSettings, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from behatrix import behatrix_functions, behatrix_qrc, version
from behatrix.behatrix_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    permutations_finished_signal = pyqtSignal(list)

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/logo"))

        self.setWindowTitle("Behatrix - Behavioral Sequences Analysis")

        self.svg_display = QtSvg.QSvgWidget()
        self.horizontal_splitter.insertWidget(2, self.svg_display)

        # self.horizontal_splitter.removeWidget(self.lb_flow_chart)

        self.lb_flow_chart.deleteLater()
        self.lb_flow_chart = None


        self.vertical_splitter.setStretchFactor(1, 10)
        self.horizontal_splitter.setStretchFactor(1, 1)

        self.pte_statistics.setLineWrapMode(False)
        self.pte_gv.setLineWrapMode(False)
        self.pte_random.setLineWrapMode(False)

        self.pb_clear_behavioral_strings.clicked.connect(self.pte_behav_strings.clear)

        # set to behavioral sequences tab
        self.tabWidget.setCurrentIndex(0)

        # connections
        self.actionLoad_behavioral_sequences.triggered.connect(self.pbSelectStringsFilename)
        self.actionQuit.triggered.connect(QApplication.quit)
        self.actionAbout.triggered.connect(self.about)

        # behavioral sequences
        self.pb_select_behav_strings_file.clicked.connect(self.pbSelectStringsFilename)
        self.pb_statistics.clicked.connect(self.behav_strings_statistics)
        self.pb_save_stats_results.clicked.connect(self.save_stats_results)
        self.pb_save_observed_matrix.clicked.connect(self.observed_matrix)
        self.pte_behav_strings.textChanged.connect(self.behavioral_sequences_changed)

        # tab flow diagram
        self.pb_graphviz_script.clicked.connect(self.graphviz_script)
        self.pb_save_gv.clicked.connect(self.save_gv)
        self.pb_flow_diagram.clicked.connect(lambda: self.flow_diagram(action="show"))
        self.pb_clear_diagram.clicked.connect(self.clear_diagram)
        self.pb_browse_dot_path.clicked.connect(self.browse_dot_path)

        self.pb_save_png.setVisible(False)

        self.pb_save_svg.clicked.connect(lambda: self.flow_diagram(action="save"))

        # tab permutations test
        self.pb_exclude_repetition.clicked.connect(self.exclude_behavior_repetitions)
        self.pb_clear_excluded_transitions.clicked.connect(self.pte_excluded_transitions.clear)
        self.pb_run_permutations_test.clicked.connect(self.permutation_test)
        self.pb_save_random.clicked.connect(self.save_permutations_test_results)
        self.pte_behav_strings.setLineWrapMode(0)
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

        config_file_path = str(pathlib.Path(os.path.expanduser("~")) / ".behatrix")
        if os.path.isfile(config_file_path):
            settings = QSettings(config_file_path, QSettings.IniFormat)
            self.le_dot_path.setText(settings.value("dot_prog_path"))

        self.permutations_finished_signal.connect(self.get_permutations_results)


    def about(self):

        about_dialog = QMessageBox()
        about_dialog.setIconPixmap(QPixmap(":/logo"))
        about_dialog.setWindowTitle("About Behatrix")
        about_dialog.setStandardButtons(QMessageBox.Ok)
        about_dialog.setDefaultButton(QMessageBox.Ok)
        about_dialog.setEscapeButton(QMessageBox.Ok)

        about_dialog.setInformativeText(
            (f"<b>Behatrix</b> {version.__version__} - {version.__version_date__}"
             "<p>Copyright &copy; 2017-2020 Olivier Friard - Marco Gamba - Sergio Castellano<br>"
             "Department of Life Sciences and Systems Biology<br>"
             "University of Torino - Italy<br>"
             "<br>"
             'BORIS is released under the <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License v.3</a><br>'
             'See <a href="http://www.boris.unito.it/pages/behatrix">www.boris.unito.it/pages/behatrix</a> for more details.<br>'
             "<hr>"))
        _ = about_dialog.exec_()



    def closeEvent(self, event):
        settings = QSettings(str(pathlib.Path(os.path.expanduser("~")) / ".behatrix"),
                             QSettings.IniFormat)

        settings.setValue("dot_prog_path", self.le_dot_path.text())


    def behavioral_sequences_changed(self):
        """
        behavioral sequences changed by user
        test separator for behaviors
        """
        self.permutations_test_matrix = None
        self.cb_plot_significativity.setEnabled(False)
        for w in [self.pte_statistics, self.pte_gv, self.pte_random, self.pte_distances_results]:
            w.clear()
        # plot significativity
        self.cb_plot_significativity.setEnabled(False)
        self.cb_plot_significativity.setChecked(False)
        # test if | separator present
        if "|" in self.pte_behav_strings.toPlainText():
            self.le_behaviors_separator.setText("|")


    def browse_dot_path(self):
        """
        browse for dot path
        """
        filename = QFileDialog(self).getOpenFileName(self, "Select the dot program from GraphViz package", "",
                                                     "All files (*)")[0]
        if filename:

            p = subprocess.Popen('"{}" -V'.format(filename),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, error = p.communicate()

            if b"graphviz version" in error:
                self.le_dot_path.setText(filename)
            else:
                QMessageBox.critical(self, "Behatrix", "The selected <b>dot</b> program is not working.<br>")


    def pbSelectStringsFilename(self):

        filename = QFileDialog().getOpenFileName(self, "Select the file containing the behavioral sequences", "",
                                                 "All files (*)")[0]

        if filename:
            self.leStringsFileName.setText(filename)

            with open(filename) as f_in:
                behav_str = f_in.read()

            self.pte_behav_strings.setPlainText(behav_str)


    def behav_strings_statistics(self):
        """
        statistics about behavioral sequences
        """

        if self.pte_behav_strings.toPlainText():

            (return_code, sequences,
             d, nodes, starting_nodes, tot_nodes,
             tot_trans, tot_trans_after_node,
             behaviours, ngrams_freq) = behatrix_functions.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                            behaviors_separator=self.le_behaviors_separator.text(),
                                                            chunk=0,
                                                            flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked(),
                                                            ngram=self.sb_ngram.value())

            output = ""
            output += ("Number of sequences:\n================\n{}\n".format(len(sequences)))
            output += ("\nBehaviours list:\n================\n{}\n".format("\n".join(behaviours)))
            output += ("\nStatistics\n==========\n")
            output += ('Number of different behaviours: {}\n'.format(len(behaviours)))
            output += ('Total number of behaviours: {}\n'.format(tot_nodes))
            output += ('Number of different transitions: {}\n'.format(len(d)))
            output += ('Total number of transitions: {}\n'.format(tot_trans))
            output += ('\nBehaviours frequencies:\n=======================\n')

            for behaviour in sorted(behaviours):
                countBehaviour = 0
                for seq in sequences:
                    countBehaviour += seq.count(behaviour)

                output += "{behaviour}\t{freq:.3f}\t{countBehaviour} / {tot_nodes}\n".format(behaviour=behaviour,
                                                                                             freq=countBehaviour / tot_nodes,
                                                                                             countBehaviour=countBehaviour,
                                                                                             tot_nodes=tot_nodes)

            # n-grams
            if self.sb_ngram.value() > 1:
                output += f"\nFrequencies of {self.sb_ngram.value()}-grams:\n=======================\n"
                output += ngrams_freq

            self.pte_statistics.setPlainText(output)

        else:
            QMessageBox.warning(self, "Behatrix", "No behavioral sequences found!")


    def save_stats_results(self):
        if self.pte_statistics.toPlainText():
            file_name = QFileDialog(self).getSaveFileName(self, "Select the file to save the matrix",
                                                          "",
                                                          "All files (*)")[0]
            if file_name:
                try:
                    with open(file_name, "w") as f_out:
                        f_out.write(self.pte_statistics.toPlainText())
                except Exception:
                    QMessageBox.critical(self, "Behatrix", "Results not saved!")
        else:
            QMessageBox.warning(self, "Behatrix", "No results to save!")


    def observed_matrix(self):
        """
        matrix of observed transitions
        """

        (return_code, sequences,
         d, nodes, starting_nodes, tot_nodes,
         tot_trans, tot_trans_after_node,
         behaviours, _) = behatrix_functions.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                        behaviors_separator=self.le_behaviors_separator.text(),
                                                        chunk=0,
                                                        flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked())

        if sequences:

            observed_matrix = behatrix_functions.create_observed_transition_matrix(sequences, behaviours)

            # display results
            # header
            out = "\t{}\n".format("\t".join(list(behaviours)))

            for r in range(observed_matrix.shape[0]):
                out += "{}\t".format(behaviours[r])
                out += "\t".join([str(int(x)) for x in observed_matrix[r, :]]) + "\n"

            self.pte_statistics.setPlainText(out)

        else:
            QMessageBox.warning(self, "Behatrix", "No behavioral sequences found!")


    def graphviz_script(self):
        """
        generate GraphViz script
        """

        if '"' in self.pte_behav_strings.toPlainText():
            QMessageBox.critical(self, "Behatrix", 'The double quotes (") are not allowed in behaviors')
            return

        (return_code, sequences,
         unique_transitions, nodes, starting_nodes, tot_nodes,
         tot_trans, tot_trans_after_node,
         behaviors, _) = behatrix_functions.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                       behaviors_separator=self.le_behaviors_separator.text(),
                                                       chunk=0,
                                                       flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked()
                                                       )

        # type of labels
        edge_label = "percent_node"
        if self.rb_percent_after_behav.isChecked():
            edge_label = "percent_node"
        if self.rb_percent_total_transitions.isChecked():
            edge_label = "percent_total"
        '''
        if self.rb_fraction_after_behav.isChecked():
            edge_label = "fraction_node"
        '''

        # check significativity
        if self.cb_plot_significativity.isChecked() and self.permutations_test_matrix is None:
            QMessageBox.critical(self, "Behatrix",
                                 "Adding significativity to graph requires p values from permutations test")
            return


        gv_script = behatrix_functions.draw_diagram(cutoff_all=self.sb_cutoff_total_transition.value(),
                                              cutoff_behavior=self.sb_cutoff_transition_after_behav.value(),
                                              unique_transitions=unique_transitions,
                                              nodes=nodes,
                                              starting_nodes=[],
                                              tot_nodes=tot_nodes,
                                              tot_trans=tot_trans,
                                              tot_trans_after_node=tot_trans_after_node,
                                              edge_label=edge_label,
                                              decimals_number=self.sb_decimals.value(),
                                              significativity=self.permutations_test_matrix
                                                              if (self.permutations_test_matrix is not None)
                                                                 and (self.cb_plot_significativity.isChecked())
                                                              else None,
                                              behaviors=behaviors)


        self.pte_gv.setPlainText(gv_script)


    def save_gv(self):
        """
        save GV script to file
        """
        if self.pte_gv.toPlainText():

            file_name, filter_ = QFileDialog().getSaveFileName(self, "Select the file to save the GraphViz script", "",
                                                               "GV files (*.gv);;TXT files (*.txt);;All files (*)")

            if file_name:
                try:
                    with open(file_name, "w") as f_out:
                        f_out.write(self.pte_gv.toPlainText())
                except Exception:
                    QMessageBox.critical(self, "Behatrix", "Results not saved!")


    def flow_diagram(self, action: str="show") -> str:
        """
        generate flow diagram from pte_gv content in SVG format
        with:
            dot program from graphviz package
            or
            viz.js javascript and nodejs

        Args:
            action (str): "show" or "save"

        Returns:
            str: path of diagram temp file path or "" in case of error
        """

        if self.pte_gv.toPlainText():

            if self.rb_graphviz.isChecked():
                # check dot path
                if self.le_dot_path.text():
                    if not os.path.isfile(self.le_dot_path.text()):
                        QMessageBox.critical(self, "Behatrix",
                                             ("The path for <b>dot</b> program is wrong.<br>"
                                              "Indicate the full path where the <b>dot</b> program from the GraphViz package is installed"))
                        return ""
                    dot_path = self.le_dot_path.text()
                else:
                    dot_path = "dot"

                # test dot program
                p = subprocess.Popen(f"{dot_path} -V", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, error = p.communicate()

                if b"graphviz version" in error:

                    gv_script = self.pte_gv.toPlainText().replace("\n", " ").replace("'", "'\\''")

                    # > must be escaped for windows (https://ss64.com/nt/syntax-esc.html#escape)
                    if sys.platform == "win32":
                        gv_script = gv_script.replace(">", "^^^>")
                        cmd = f'''echo {gv_script} | "{dot_path}" -Tsvg '''

                    else:
                        cmd = f'''echo '{gv_script}' | "{dot_path}" -Tsvg '''

                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    out, error = p.communicate()

                    if error:
                        QMessageBox.critical(self, "Behatrix", error.decode("utf-8"))
                        return

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
                    viz_path = pathlib.Path(sys.argv[0]).parent / "misc" / "viz.js"

                '''
                print("is file", pathlib.Path(sys.path[0]).is_file())
                print("is dir", pathlib.Path(sys.path[0]).is_dir())

                if sys.path[0] == "":  # module (pip)
                    syspath = ""
                    print("pathlib.Path(sys.argv[0]).parent", pathlib.Path(sys.argv[0]).parent)
                    viz_path = pathlib.Path(sys.argv[0]).parent / pathlib.Path("misc") / pathlib.Path("viz.js")

                elif pathlib.Path(sys.path[0]).is_file():  # frozen (pyinstaller)
                    syspath = pathlib.Path(sys.path[0]).parent

                elif pathlib.Path(sys.path[0]).is_dir():  # python script
                    viz_path = pathlib.Path(sys.path[0]) / pathlib.Path("behatrix") / pathlib.Path("misc") / pathlib.Path("viz.js")
                    syspath = sys.path[0]
                #viz_path = viz_path.replace("\\", "/")
                '''

                print(f"viz.js path: {viz_path}")
                if not viz_path.is_file():
                    QMessageBox.critical(self, "Behatrix", "The viz.js file was not found!")
                    return
                viz_path = str(viz_path).replace("\\", "/")

                # node (nodejs)
                node_cmd_list = ["node", "/usr/local/bin/node"]
                node_cmd_verified = ""
                for node_cmd in node_cmd_list:
                    p = subprocess.Popen(f"{node_cmd} -v",
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         shell=True)
                    out, error = p.communicate()
                    if not error and out.decode("utf-8") and out.decode("utf-8")[0] == "v":
                        node_cmd_verified = node_cmd
                        break
                
                if not node_cmd_verified:
                    QMessageBox.critical(self, "Behatrix",
                                             ("The Node.js JavaScript runtime was not found!\n"
                                              "Please install it or switch to the Graphviz package"))
                    return
                print(f"node_cmd_verified {node_cmd_verified}")


                # escape for echo and nodejs
                gv_script_escaped = self.pte_gv.toPlainText().replace("\n", " ").replace('"', '\\"').replace("'", "'\\''")

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

            if action == "show":
                self.svg_display.load(out)

            if action == "save":
                file_name, filter_ = QFileDialog().getSaveFileName(self,
                                                                   "Select the file and format to save the flow diagram", "",
                                                                   "SVG files (*.svg);;All files (*)"
                                                                   )
                if file_name:
                    try:
                        with open(file_name, "w") as f_out:
                            f_out.write(out.decode("utf-8"))
                    except Exception:
                        QMessageBox.critical(self, "Behatrix", "Error saving the file")
                        return

                    self.svg_display.load(out)



    def clear_diagram(self):
        """
        clear diagram
        """

        self.svg_display.load(b"")


    def save_diagram(self, image_format):
        """
        save diagram
        """
        if self.pte_gv.toPlainText():
            file_name, filter_ = QFileDialog().getSaveFileName(self,
                                                               "Select the file and format to save the flow diagram", "",
                                                               "PNG files (*.png);;All files (*)" if image_format == "png" else
                                                               "SVG files (*.svg);;All files (*)"
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
        (return_code, _,
         _, _, _, _,
         _, _, behaviors, _) = behatrix_functions.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                             behaviors_separator=self.le_behaviors_separator.text(),
                                                             chunk=0)
        self.pte_excluded_transitions.insertPlainText("\n")
        for behavior in behaviors:
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

        out = "\t{}\n".format('\t'.join(list(self.behaviours)))

        self.permutations_test_matrix = permutation_results / nb_randomization_done

        for r in range(self.permutations_test_matrix.shape[0]):
            out += f"{self.behaviours[r]}\t"
            out += "\t".join(["%8.6f" % x for x in self.permutations_test_matrix[r, :]]) + "\n"

        self.pte_random.setPlainText(out)

        self.statusbar.showMessage("", 0)

        self.cb_plot_significativity.setEnabled(True)

        QMessageBox.information(self, "Behatrix",
                                ("Permutations test finished<br>"
                                 f"{nb_randomization_done} permutations done<br><br>"))


    def permutations_test_finished(self, results):
        """
        permutations test finished
        """
        self.permutations_finished_signal.emit(results)


    def permutation_test(self):

        if self.pte_behav_strings.toPlainText():
            self.pte_random.clear()

            (return_code, sequences,
             d, nodes, starting_nodes, tot_nodes,
             tot_trans, tot_trans_after_node,
             self.behaviours, _) = behatrix_functions.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                            behaviors_separator=self.le_behaviors_separator.text(),
                                                            chunk=0,
                                                            flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked()
                                                            )

            # check exclusion list
            if self.pte_excluded_transitions.toPlainText():
                result = behatrix_functions.check_exclusion_list(self.pte_excluded_transitions.toPlainText(), sequences)

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

                observed_matrix = behatrix_functions.create_observed_transition_matrix(sequences, self.behaviours)

                self.pb_run_permutations_test.setEnabled(False)
                self.nb_randomization_done = 0
                pool = multiprocessing.Pool(processes = multiprocessing.cpu_count())

                n_random_by_proc = round(self.nrandom / num_proc + 1)

                pool.starmap_async(behatrix_functions.permutations_test,
                                    [(n_random_by_proc,
                                    sequences, self.behaviours,
                                    exclusion_list,
                                    self.cb_block_first_behavior.isChecked(),
                                    self.cb_block_last_behavior.isChecked(),
                                    observed_matrix)
                                    ] * num_proc,
                                    callback=self.permutations_test_finished)

            else:
                QMessageBox.warning(self, "Behatrix", "Select the number of permutations to execute")

        else:
            QMessageBox.warning(self, "Behatrix", "No behavioral sequences found!")


    def save_permutations_test_results(self):
        """
        Save permutations test matrix
        """
        if self.pte_random.toPlainText():

            file_name, filter_ = QFileDialog().getSaveFileName(self, "Select the file to save the results", "",
                                                               "TSV files (*.tsv);;TXT files (*.txt);;All files (*)")

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

        seq_list = [x.strip() for x in self.pte_behav_strings.toPlainText().split("\n") if x.strip()]

        if self.le_behaviors_separator.text():
            seq_list = [x.split(self.le_behaviors_separator.text()) for x in seq_list]

        results = behatrix_functions.levenshtein_distance_seq_list(seq_list)

        # display results
        out = "Levenshtein distances:\n"
        # header
        out += "\t{}\n".format("\t".join([f"seq #{x + 1}" for x, _ in enumerate(seq_list)]))
        for r in range(results.shape[0]):
            out += f"seq #{r + 1}\t"
            out += "\t".join([f"{int(x)}" for x in results[r, :]]) + "\n"

        self.pte_distances_results.setPlainText(out)


    def needleman_wunsch_identity(self):
        """
        Needleman-Wunsch identities between behavioral sequences
        """

        seq_list = [x.strip() for x in self.pte_behav_strings.toPlainText().split("\n") if x.strip()]

        if self.le_behaviors_separator.text():
            seq_list = [x.split(self.le_behaviors_separator.text()) for x in seq_list]

        results = behatrix_functions.needleman_wunsch_identity_seq_list(seq_list)

        # display results
        out = "Needleman-Wunsch identities:\n"
        # header
        out += "\t{}\n".format("\t".join([f"seq #{x + 1}" for x, _ in enumerate(seq_list)]))
        for r in range(results.shape[0]):
            out += f"seq #{r + 1}\t"
            out += "\t".join([f"{x:.2f}" for x in results[r, :]]) + "\n"

        self.pte_distances_results.setPlainText(out)


    def save_distances_results(self):
        """
        Save distances matrix
        """
        if self.pte_distances_results.toPlainText():

            file_name, filter_ = QFileDialog().getSaveFileName(self, "Select the file to save the results", "",
                                                               "TSV files (*.tsv);;TXT files (*.txt);;All files (*)")

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
    parser = argparse.ArgumentParser(prog="Behatrix",
                                     usage="\npython3 -m behatrix [options]",
                                     description="Behatrix command line utility",
                                     epilog="See http://www.boris.unito.it/pages/behatrix for details :-)")
    parser.add_argument("-v", "--version", action="store_true", dest="version", help="Behatrix version")
    parser.add_argument("-s", "--sequences", action="store", dest="sequences", help="Path of file containing behavioral sequences")
    parser.add_argument("--separator", action="store", dest="separator", default="", help="Separator of behaviors")
    parser.add_argument("-o", "--output", action="store", dest="output", help="Path of output files")
    parser.add_argument("--exclusions", action="store", dest="exclusions", help="Path of file containing exclusions")
    parser.add_argument("--n-random", action="store", dest='nrandom', help="Number of permutations", type=int, default=0)
    parser.add_argument("--n-cpu", action="store", dest='n_cpu', help="Number of CPU to use for permutations test", type=int, default=0)
    parser.add_argument("--block-first", action="store_true", dest='block_first', help="block first behavior during permutations test")
    parser.add_argument("--block-last", action="store_true", dest="block_last", help="block last behavior during permutations test")
    parser.add_argument("--no-repetition", action="store_true", dest="no_repetition", help="exclude repetitions during permutations test")
    parser.add_argument("--n-gram", action="store", default=1, dest="ngram", help="n-gram value", type=int)

    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", default=False, help="Do not print results on terminal")

    args = parser.parse_args()

    if args.version:
        print("Copyright (C) 2017-2020 Olivier Friard - Marco Gamba - Sergio Castellano")
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

    (return_code, sequences, unique_transitions, nodes, starting_nodes, tot_nodes, tot_trans,
     tot_trans_after_node, behaviours, ngrams_freq) = behatrix_functions.behav_strings_stats(
         behav_str, behaviors_separator=args.separator, chunk=0, ngram=args.ngram)

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

        result = behatrix_functions.check_exclusion_list(exclusion_str, sequences)
        if not result["error_code"]:
            exclusion_list = result["exclusion_list"]
        else:
            print(result["message"])
            return

        block_first = 1 if args.block_first else 0
        block_last = 1 if args.block_last else 0


    if not args.quiet:
        sep = "\n"
        print(f"\nNumber of sequences: {len(sequences)}")

        print(f"\nBehaviours list:\n================\n{sep.join(behaviours)}\n")

        print("Statistics\n==========")
        print(f'Number of different behaviours: {len(behaviours)}')
        print(f'Total number of behaviours: {tot_nodes}')
        print(f'Number of different transitions: {len(unique_transitions)}')
        print(f'Total number of transitions: {tot_trans}')

        print('\nFrequencies of behaviors:\n=======================')

        for behaviour in sorted(behaviours):
            countBehaviour = 0
            for seq in sequences:
                countBehaviour += seq.count(behaviour)

            print(f"{behaviour}\t{countBehaviour / tot_nodes:.3f}\t{countBehaviour} / {tot_nodes}")

        # n-grams
        if args.ngram > 1:
            print(f"\nFrequencies of {args.ngram}-grams:\n=======================")
            print(ngrams_freq)

    observed_matrix = behatrix_functions.create_observed_transition_matrix(sequences, behaviours)

    if not args.quiet:
        print("\nObserved transition matrix:\n===========================\n{}".format(observed_matrix))

    if args.output:
        file_name = f'{args.output}.observed_transitions.tsv'
    else:
        file_name = f'{args.sequences}.observed_transitions.tsv'

    np.savetxt(file_name, observed_matrix, fmt='%d', delimiter='\t')

    with open(file_name, mode="r", encoding="utf-8") as f_in:
        rows = f_in.readlines()

    with open(file_name, mode="w", encoding="utf-8") as f_out:
        f_out.write('\t' + '\t'.join(behaviours) + '\n')
        c = 0
        for row in rows:
            f_out.write((behaviours)[c] + '\t' + row)
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

        results = np.zeros((len(behaviours), len(behaviours)))
        with concurrent.futures.ProcessPoolExecutor() as executor:
            lst = []
            n_required_randomizations = 0
            for i in range(num_proc):

                if i < num_proc - 1:
                    n_random_by_proc = nrandom // num_proc
                else:
                    n_random_by_proc = nrandom - n_required_randomizations

                lst.append(executor.submit(behatrix_functions.permutations_test,
                                           n_random_by_proc,
                                           sequences, behaviours,
                                           exclusion_list,
                                           block_first,
                                           block_last,
                                           observed_matrix,
                                           args.no_repetition))

                n_required_randomizations += n_random_by_proc

            print("\nnumber of required permutations: ", n_required_randomizations)

            nb_randomization_done = 0

            for l in lst:
                nb_randomization_done += l.result()[0]
                results += l.result()[1]

        print(f"Number of permutations done: {nb_randomization_done}")

        if not args.quiet:
            print(f"\nP-values matrix:\n===========================\n{results / nrandom}")

        if args.output:
            file_name = f"{args.output}.p-values.{nrandom}.tsv"
        else:
            file_name = f"{args.sequences}.p-values.{nrandom}.tsv"

        np.savetxt(file_name, results / nrandom, fmt='%f', delimiter='\t')

        try:
            with open(file_name, mode="r", encoding="utf-8") as f:
                rows = f.readlines()
            with open(file_name, mode='w', encoding="utf-8") as f:
                f.write("\t" + "\t".join(list(behaviours)) + "\n")
                c = 0
                for row in rows:
                    f.write((behaviours)[c] + "\t" + row)
                    c += 1
        except Exception:
            print(f"Error during creation of file: {file_name}")


if __name__ == "__main__":
    main()
