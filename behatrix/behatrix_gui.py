#!/usr/bin/env python3


"""
Behatrix
Behavioural Strings Analysis (BSA).

Behavioral strings analysis with randomization test


Copyright 2017-2019 Olivier Friard

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

import os
import sys
import numpy as np
import subprocess
import concurrent.futures
import tempfile
import pathlib
import platform
from shutil import copyfile

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
#from PyQt5 import QtSvg
from behatrix import behatrix_qrc
from behatrix.behatrix_ui import Ui_MainWindow

from behatrix import behatrix_functions
from behatrix import version

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/logo"))

        #self.setWindowIcon(QIcon(os.path.dirname(os.path.realpath(__file__)) + "/behatrix_128px.png"))
        self.setWindowTitle("Behatrix - Behavioral Sequences Analysis")

        #self.verticalLayout_4.insertWidget(2, QLabel("TEST"))
        #self.horizontal_splitter.insertWidget(2, QLabel("TEST"))

        '''
        self.svg_display = QtSvg.QSvgWidget()
        self.horizontal_splitter.insertWidget(2, self.svg_display)
        '''

        #svgWidget = QtSvg.QSvgWidget('Zeichen_123.svg')

        #self.horizontal_splitter.removeWidget(self.lb_flow_chart)

        '''
        self.lb_flow_chart.deleteLater()
        self.lb_flow_chart = None
        '''

        self.vertical_splitter.setStretchFactor(1, 10)
        self.horizontal_splitter.setStretchFactor(1, 1)

        self.pte_statistics.setLineWrapMode(False)
        self.pte_gv.setLineWrapMode(False)
        self.pte_random.setLineWrapMode(False)

        self.pb_clear_behavioral_strings.clicked.connect(self.pte_behav_strings.clear)

        # set to tab strings
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
        self.pte_behav_strings.textChanged.connect(self.behavioral_strings_changed)

        # tab flow diagram
        self.pb_graphviz_script.clicked.connect(self.graphviz_script)
        self.pb_save_gv.clicked.connect(self.save_gv)
        self.pb_flow_diagram.clicked.connect(lambda: self.flow_diagram("png"))
        self.pb_clear_diagram.clicked.connect(self.clear_diagram)
        self.pb_browse_dot_path.clicked.connect(self.browse_dot_path)
        # self.pte_gv.textChanged.connect(self.flow_diagram)
        self.pb_save_png.clicked.connect(lambda: self.save_diagram("png"))
        self.pb_save_svg.clicked.connect(lambda: self.save_diagram("svg"))

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


    def about(self):

        about_dialog = QMessageBox()
        about_dialog.setIconPixmap(QPixmap(":/logo"))
        about_dialog.setWindowTitle("About Behatrix")
        about_dialog.setStandardButtons(QMessageBox.Ok)
        about_dialog.setDefaultButton(QMessageBox.Ok)
        about_dialog.setEscapeButton(QMessageBox.Ok)

        about_dialog.setInformativeText(
            (f"<b>Behatirx</b> {version.__version__} - {version.__version_date__}"
             "<p>Copyright &copy; 2017-2019 Olivier Friard - Marco Gamba - Sergio Castellano<br>"
             "Department of Life Sciences and Systems Biology<br>"
             "University of Torino - Italy<br>"
             "<br>"
             """BORIS is released under the <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License v.3</a><br>"""
             """See <a href="http://www.boris.unito.it/pages/behatrix">www.boris.unito.it/pages/behatrix</a> for more details.<br>"""
             "<hr>"))
        _ = about_dialog.exec_()


    def closeEvent(self, event):
        settings = QSettings(str(pathlib.Path(os.path.expanduser("~")) / ".behatrix"),
                             QSettings.IniFormat)

        settings.setValue("dot_prog_path", self.le_dot_path.text())


    def behavioral_strings_changed(self):
        """
        behavioral string changed by user
        test separator for behaviors
        """
        self.permutations_test_matrix = None
        self.cb_plot_significativity.setEnabled(False)
        for w in [self.pte_statistics, self.pte_gv, self.pte_random, self.pte_distances_results]:
            w.clear()
        # test if | separator present
        if "|" in self.pte_behav_strings.toPlainText():
            self.le_behaviors_separator.setText("|")


    def browse_dot_path(self):
        """
        browse for dot path
        """
        filename = QFileDialog(self).getOpenFileName(self, "Select the dot program from GraphViz package", "", "All files (*)")[0]
        if filename:

            p = subprocess.Popen('"{}" -V'.format(filename),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, error = p.communicate()

            if b"graphviz version" in error:
                self.le_dot_path.setText(filename)
            else:
                QMessageBox.critical(self, "Behatrix", "The selected <b>dot</b> program is not working.<br>")


    def pbSelectStringsFilename(self):

        filename = QFileDialog().getOpenFileName(self, "Select the file containing the behavioral sequences", "", "All files (*)")[0]

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
            QMessageBox.warning(self, "Behatrix", "No behavioral strings found!")


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
            QMessageBox.warning(self, "Behatrix", "No behavioral strings found!")


    def graphviz_script(self):
        """
        generate GraphViz script
        """

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
            QMessageBox.critical(self, "Behatrix", "Adding significativity to graph requires p values from permutations test")
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


    def flow_diagram(self, image_format:str="png") -> str:
        """
        generate flow diagram from pte_gv content
        in PNG or SVG format
        with dot program from graphviz package

        Args:
            image_format (str): format of image: png or svg

        Returns:
            str: path of diagram temp file path or "" in case of error
        """

        if self.pte_gv.toPlainText():


            gv_script = self.pte_gv.toPlainText()

            tmp_gv_path = str(pathlib.Path(tempfile.gettempdir()) / pathlib.Path("gv_temp.gv"))
            try:
                with open(tmp_gv_path, "w") as tmp_gv_file:
                    tmp_gv_file.write(gv_script)
            except Exception:
                QMessageBox.critical(self, "Behatrix", "Error during flow diagram generation!")
                return

            tmp_image_path = str(pathlib.Path(tempfile.gettempdir()) / pathlib.Path("temp_flow_diagram." + image_format))

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
            # remove previous file
            if os.path.isfile(tmp_image_path):
                os.remove(tmp_image_path)

            cmd = f'"{dot_path}" -T{image_format} "{tmp_gv_path}" -o "{tmp_image_path}"'

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, error = p.communicate()

            if error:
                QMessageBox.warning(self, "Behatrix", error.decode("utf-8"))

            if not os.path.isfile(tmp_image_path):
                QMessageBox.critical(self, "Behatrix",
                                     "Error during the graph creation.")
                return ""

            if image_format == "svg":
                self.svg_display.load(tmp_image_path)

            if image_format == "png":
                myPixmap = QPixmap(tmp_image_path)
                scaled_pixmap = myPixmap.scaled(self.lb_flow_chart.size(), Qt.KeepAspectRatio)
                self.lb_flow_chart.setPixmap(scaled_pixmap)

            return tmp_image_path



    def clear_diagram(self):
        """
        clear diagram
        """
        self.lb_flow_chart.clear()




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


    def permutation_test(self):

        if self.pte_behav_strings.toPlainText():

            (return_code, sequences,
             d, nodes, starting_nodes, tot_nodes,
             tot_trans, tot_trans_after_node,
             behaviours, _) = behatrix_functions.behav_strings_stats(self.pte_behav_strings.toPlainText(),
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
                    nrandom = int(self.leNumberRandomizations.text())
                except Exception:
                    nrandom = 0
                    QMessageBox.warning(self, "Behatrix", "The number of Permutations is not valid")
                    return

            if nrandom:

                self.statusbar.showMessage("Permutations test running... Be patient", 0)
                QApplication.processEvents()

                num_proc = self.sb_nb_cores.value()

                if num_proc > nrandom:
                    num_proc = nrandom

                observed_matrix = behatrix_functions.create_observed_transition_matrix(sequences, behaviours)

                results = np.zeros((len(behaviours), len(behaviours)))

                # frozen script by pyinstaller does not allow to use multiprocessing
                if sys.platform.startswith("win") and getattr(sys, "frozen", False):
                    n_random_by_proc = nrandom
                    nb_randomization_done, results = behatrix_functions.permutations_test(n_random_by_proc,
                                                                                    sequences, behaviours,
                                                                                    exclusion_list,
                                                                                    self.cb_block_first_behavior.isChecked(),
                                                                                    self.cb_block_last_behavior.isChecked(),
                                                                                    observed_matrix)
                else:

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
                                                       self.cb_block_first_behavior.isChecked(),
                                                       self.cb_block_last_behavior.isChecked(),
                                                       observed_matrix))

                            n_required_randomizations += n_random_by_proc

                        nb_randomization_done = 0

                        for l in lst:
                            nb_randomization_done += l.result()[0]
                            results += l.result()[1]

                # display results
                # header
                out = "\t{}\n".format("\t".join(list(behaviours)))

                self.permutations_test_matrix = results / nrandom

                for r in range(self.permutations_test_matrix.shape[0]):
                    out += "{}\t".format(behaviours[r])
                    out += "\t".join(["%8.6f" % x for x in self.permutations_test_matrix[r, :]]) + "\n"

                self.pte_random.setPlainText(out)

                self.statusbar.showMessage("", 0)

                self.cb_plot_significativity.setEnabled(True)

                QMessageBox.information(self, "Behatrix",
                                        ("Permutations test finished<br>"
                                         f"{nb_randomization_done} permutations done<br><br>"))

            else:
                QMessageBox.warning(self, "Behatrix", "Select the number of permutations to execute")

        else:
            QMessageBox.warning(self, "Behatrix", "No behavioral strings found!")


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
            seq_list = [x.split(self.le_behaviors_separator.text()) for x in seq_list]  # seq1.split(self.le_behaviors_separator_distance.text())

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
            seq_list = [x.split(self.le_behaviors_separator.text()) for x in seq_list]  # seq1.split(self.le_behaviors_separator_distance.text())

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
                                     description="Behatrix command line utility")
    parser.add_argument("-v", action="store_true", dest="version", help="Behatrix version")
    parser.add_argument("--sequences", action="store", dest="sequences", help="Path of file containing behavioral sequences")
    parser.add_argument("--separator", action="store", dest="separator", default="", help="Separator of behaviors")
    parser.add_argument("--output", action="store", dest="output", help="Path of output files")
    parser.add_argument("--exclusions", action="store", dest='exclusions', help='Path of file containing exclusions')
    parser.add_argument("--n_random", action="store", dest='nrandom', help='Number of permutations', type=int, default=0)
    parser.add_argument("--n_cpu", action="store", dest='n_cpu', help='Number of CPU to use for permutations test', type=int, default=0)
    parser.add_argument("--block_first", action="store_true", dest='block_first', help='block first behavior during permutations test')
    parser.add_argument("--block_last", action="store_true", dest='block_last', help='block last behavior during permutations test')
    parser.add_argument("--no_repetition", action="store_true", dest='no_repetition', help='exclude repetitions during permutations test')
    parser.add_argument("--n-gram", action="store", default=1, dest='ngram', help='n-gram value', type=int)

    parser.add_argument("--quiet", action="store_true", dest='quiet', default=False, help='Do not print results on terminal')

    args = parser.parse_args()

    if args.version:
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

    (return_code, sequences,
     unique_transitions, nodes, starting_nodes, tot_nodes,
     tot_trans, tot_trans_after_node, behaviours, ngrams_freq) = behatrix_functions.behav_strings_stats(behav_str,
                                                                                     behaviors_separator=args.separator,
                                                                                     chunk=0,
                                                                                     ngram=args.ngram)


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

        print("\nBehaviours list:\n================\n{}\n".format("\n".join(behaviours)))

        print("Statistics\n==========")
        print(f'Number of different behaviours: {len(behaviours)}')
        print(f'Total number of behaviours: {tot_nodes}')
        print(f'Number of different transitions: {len(unique_transitions)}')
        print(f'Total number of transitions: {tot_trans}')

        print('\nBehaviours frequencies:\n=======================')

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
