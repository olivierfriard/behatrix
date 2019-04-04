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
import numpy
import subprocess
import concurrent.futures
import tempfile
import pathlib
import platform
import version
from shutil import copyfile

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from behatrix_ui import Ui_MainWindow
import behatrix_cli


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.setWindowIcon(QIcon(os.path.dirname(os.path.realpath(__file__)) + "/behatrix_128px.png"))
        self.setWindowTitle("Behatrix - Behavioral Strings Analysis")

        self.vertical_splitter.setStretchFactor(1, 10)
        self.horizontal_splitter.setStretchFactor(1, 1)

        self.pte_statistics.setLineWrapMode(False)
        self.pte_gv.setLineWrapMode(False)
        self.pte_random.setLineWrapMode(False)

        self.pb_clear_behavioral_strings.clicked.connect(self.pte_behav_strings.clear)

        # set to tab strings
        self.tabWidget.setCurrentIndex(0)

        # connections
        self.actionAbout.triggered.connect(self.about)
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
        
        # tab Levenshtein
        self.pte_seq1.textChanged.connect(self.behavioral_seq_distances_changed)
        self.pte_seq2.textChanged.connect(self.behavioral_seq_distances_changed)
        self.pb_levenshtein.clicked.connect(self.levenshtein_distance)
        self.pb_needleman_wunsch.clicked.connect(self.needleman_wunsch_identity)

        self.permutations_test_matrix = None

        self.cb_plot_significativity.setEnabled(False)

        config_file_path = str(pathlib.Path(os.path.expanduser("~")) / ".behatrix")
        if os.path.isfile(config_file_path):
            settings = QSettings(config_file_path, QSettings.IniFormat)
            self.le_dot_path.setText(settings.value("dot_prog_path"))


    def about(self):

        about_dialog = QMessageBox()
        about_dialog.setIconPixmap(QPixmap(os.path.dirname(os.path.realpath(__file__)) + "/behatrix_128px.png"))
        about_dialog.setWindowTitle("About Behatrix")
        about_dialog.setStandardButtons(QMessageBox.Ok)
        about_dialog.setDefaultButton(QMessageBox.Ok)
        about_dialog.setEscapeButton(QMessageBox.Ok)

        about_dialog.setInformativeText(
            ("<b>{prog_name}</b> {ver} - {date}"
             "<p>Copyright &copy; 2017-2019 Olivier Friard - Marco Gamba - Sergio Castellano<br>"
             "Department of Life Sciences and Systems Biology<br>"
             "University of Torino - Italy<br>"
             "<br>"
             """BORIS is released under the <a href="http://www.gnu.org/copyleft/gpl.html">GNU General Public License</a><br>"""
             """See <a href="http://www.boris.unito.it/behatrix">www.boris.unito.it/behatrix</a> for more details.<br>"""
             "<hr>").format(prog_name="Behatrix",
                            ver=version.__version__,
                            date=version.__version_date__,
                            python_ver=platform.python_version()))
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
        for w in [self.pte_statistics, self.pte_gv, self.pte_random]:
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

        filename = QFileDialog(self).getOpenFileName(self, "Select the file containing the behavioral strings", "", "All files (*)")[0]

        if filename:
            self.leStringsFileName.setText(filename)

            with open(filename) as f_in:
                behav_str = f_in.read()

            self.pte_behav_strings.setPlainText(behav_str)


    def behav_strings_statistics(self):
        """
        statistics about behavioral strings
        """

        if self.pte_behav_strings.toPlainText():

            (return_code, sequences,
             d, nodes, starting_nodes, tot_nodes,
             tot_trans, tot_trans_after_node,
             behaviours) = behatrix_cli.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                            behaviors_separator=self.le_behaviors_separator.text(),
                                                            chunk=0,
                                                            flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked())

            output = ""
            output += ("Behaviours list:\n================\n{}\n".format("\n".join(behaviours)))
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

            self.pte_statistics.setPlainText(output)

        else:
            QMessageBox.warning(self, "Behatrix", "No behavioral strings found!")


    def save_stats_results(self):
        if self.pte_statistics.toPlainText():
            file_name = QFileDialog(self).getSaveFileName(self, "Select the file to save the matrix",
                                                          "",
                                                          "All files (*)")[0]
            if file_name:
                with open(file_name, "w") as f_out:
                    f_out.write(self.pte_statistics.toPlainText())
        else:
            QMessageBox.warning(self, "Behatrix", "No results to save!")


    def observed_matrix(self):
        """
        matrix of observed transitions
        """

        (return_code, sequences,
         d, nodes, starting_nodes, tot_nodes,
         tot_trans, tot_trans_after_node,
         behaviours) = behatrix_cli.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                        behaviors_separator=self.le_behaviors_separator.text(),
                                                        chunk=0,
                                                        flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked())

        if sequences:

            observed_matrix = behatrix_cli.create_observed_transition_matrix(sequences, behaviours)

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
         behaviors) = behatrix_cli.behav_strings_stats(self.pte_behav_strings.toPlainText(),
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
        if self.rb_fraction_after_behav.isChecked():
            edge_label = "fraction_node"


        # check significativity
        if self.cb_plot_significativity.isChecked() and self.permutations_test_matrix is None:
            QMessageBox.critical(self, "Behatrix", "Adding significativity to graph requires p values from permutations test")
            return


        gv_script = behatrix_cli.draw_diagram(cutoff_all=self.sb_cutoff_total_transition.value(),
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
                with open(file_name, "w") as f_out:
                    f_out.write(self.pte_gv.toPlainText())


    def flow_diagram(self, image_format:str="png")->str:
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
            with open(tmp_gv_path, "w") as tmp_gv_file:
                tmp_gv_file.write(gv_script)

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

            if image_format == "png":
                myPixmap = QPixmap(tmp_image_path)
                myScaledPixmap = myPixmap.scaled(self.lb_flow_chart.size(), Qt.KeepAspectRatio)
                self.lb_flow_chart.setPixmap(myScaledPixmap)

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
         _, _, behaviors) = behatrix_cli.behav_strings_stats(self.pte_behav_strings.toPlainText(),
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
             behaviours) = behatrix_cli.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                            behaviors_separator=self.le_behaviors_separator.text(),
                                                            chunk=0,
                                                            flag_remove_repetitions=self.cb_remove_repeated_behaviors.isChecked()
                                                            )

            # check exclusion list
            if self.pte_excluded_transitions.toPlainText():
                result = behatrix_cli.check_exclusion_list(self.pte_excluded_transitions.toPlainText(), sequences)

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
                app.processEvents()

                num_proc = self.sb_nb_cores.value()

                if num_proc > nrandom:
                    num_proc = nrandom

                observed_matrix = behatrix_cli.create_observed_transition_matrix(sequences, behaviours)

                results = numpy.zeros((len(behaviours), len(behaviours)))

                # frozen script by pyinstaller does not allow to use multiprocessing
                if sys.platform.startswith("win") and getattr(sys, "frozen", False):
                    n_random_by_proc = nrandom
                    nb_randomization_done, results = behatrix_cli.permutations_test(n_random_by_proc,
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

                            lst.append(executor.submit(behatrix_cli.permutations_test,
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
                with open(file_name, "w") as f_out:
                    f_out.write(self.pte_random.toPlainText())

    def behavioral_seq_distances_changed(self):
        """
        behavioral sequences changed by user
        test separator for behaviors
        """
        self.pte_distances_results.clear()

        # test if | separator present
        for w in [self.pte_seq1, self.pte_seq2]:
            if "|" in w.toPlainText():
                self.le_behaviors_separator_distance.setText("|")


    def levenshtein_distance(self):
        """
        Levenshtein distance between 2 behavioral sequences
        """
        seq1 = self.pte_seq1.toPlainText()
        seq2 = self.pte_seq2.toPlainText()
        if self.le_behaviors_separator_distance.text():
            seq1 = seq1.split(self.le_behaviors_separator_distance.text())
            seq2 = seq2.split(self.le_behaviors_separator_distance.text())
        results = round(behatrix_cli.levenshtein(seq1, seq2))
        self.pte_distances_results.clear()
        self.pte_distances_results.insertPlainText(f"Levenshtein distance: {results}")


    def needleman_wunsch_identity(self):
        """
        Needleman-Wunsch identity
        """
        seq1 = self.pte_seq1.toPlainText()
        seq2 = self.pte_seq2.toPlainText()
        if self.le_behaviors_separator_distance.text():
            seq1 = seq1.split(self.le_behaviors_separator_distance.text())
            seq2 = seq2.split(self.le_behaviors_separator_distance.text())
        results = behatrix_cli.needleman_wunsch(seq1, seq2)
        self.pte_distances_results.clear()
        self.pte_distances_results.insertPlainText(f"Needleman-Wunsch identity: {results['identity']:.2f} %")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.show()
    mainWindow.raise_()
    sys.exit(app.exec_())
