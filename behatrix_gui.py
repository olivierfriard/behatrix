#!/usr/bin/env python3


"""
Behatrix
Behavioural Strings Analysis (BSA).

Behavioral strings analysis with randomization test


Copyright 2017-2018 Olivier Friard

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

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from behatrix_ui import Ui_MainWindow
import behatrix_cli


class MainWindow(QMainWindow, Ui_MainWindow):


    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("Behatrix - Behavioral Strings Analysis")

        self.pte_statistics.setLineWrapMode(False)
        self.pte_gv.setLineWrapMode(False)
        self.pte_random.setLineWrapMode(False)

        # set to tab strings
        self.tabWidget.setCurrentIndex(0)

        # connections
        self.actionAbout.triggered.connect(self.about)

        self.pb_select_behav_strings_file.clicked.connect(self.pbSelectStringsFilename)

        self.pb_statistics.clicked.connect(self.behav_strings_statistics)

        self.pb_save_stats_results.clicked.connect(self.save_stats_results)

        self.pb_save_observed_matrix.clicked.connect(self.observed_matrix)

        # tab flow diagram
        self.pb_graphviz_script.clicked.connect(self.graphviz_script)
        self.pb_save_gv.clicked.connect(self.save_gv)
        self.pb_flow_diagram.clicked.connect(self.flow_diagram)
        self.pb_browse_dot_path.clicked.connect(self.browse_dot_path)

        # tab permutations test
        self.pb_exclude_repetition.clicked.connect(self.exclude_behavior_repetitions)
        self.pb_clear_excluded_transitions.clicked.connect(self.pte_excluded_transitions.clear)
        self.pb_run_randomization_test.clicked.connect(self.permutation_test)
        self.pb_save_random.clicked.connect(self.save_random)

        self.pb_flow_chart_significant.clicked.connect(self.flow_chart_significant)

        self.pte_behav_strings.setLineWrapMode(0)

        num_available_proc = os.cpu_count()

        self.sb_nb_cores.setMinimum(1)
        self.sb_nb_cores.setMaximum(num_available_proc)

        if num_available_proc <= 2:
            self.sb_nb_cores.setValue(1)
        else:
            self.sb_nb_cores.setValue(num_available_proc - 1)

        self.permutations_test_matrix = None


    def about(self):

        about_dialog = QMessageBox()
        # about_dialog.setIconPixmap(QPixmap(os.path.dirname(os.path.realpath(__file__)) + "/logo_eye.128px.png"))
        about_dialog.setWindowTitle("About Behatrix")
        about_dialog.setStandardButtons(QMessageBox.Ok)
        about_dialog.setDefaultButton(QMessageBox.Ok)
        about_dialog.setEscapeButton(QMessageBox.Ok)

        about_dialog.setInformativeText(
            ("<b>{prog_name}</b> {ver} - {date}"
             "<p>Copyright &copy; 2017-2018 Olivier Friard - Marco Gamba - Sergio Castellano<br>"
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
                                                            chunk=0)

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
                                                        chunk=0)

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
         behaviours) = behatrix_cli.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                        behaviors_separator=self.le_behaviors_separator.text(),
                                                        chunk=0)

        edge_label = "percent_node"
        if self.rb_percent_after_behav.isChecked():
            edge_label = "percent_node"
        if self.rb_percent_total_transitions.isChecked():
            edge_label = "percent_total"
        if self.rb_fraction_after_behav.isChecked():
            edge_label = "fraction_node"

        try:
            cutoff_all = float(self.le_cutoff_total_transition.text())
        except Exception:
            QMessageBox.critical(self, "Behatrix", "{} value is not allowed")
            return
        try:
            cutoff_behavior = float(self.le_cutoff_transition_after_behav.text())
        except Exception:
            QMessageBox.critical(self, "Behatrix", "{} value is not allowed")
            return

        gv_script = behatrix_cli.draw_diagram(cutoff_all=cutoff_all,
                                              cutoff_behavior=cutoff_behavior,
                                              unique_transitions=unique_transitions,
                                              nodes=nodes,
                                              starting_nodes=[],
                                              tot_nodes=tot_nodes,
                                              tot_trans=tot_trans,
                                              tot_trans_after_node=tot_trans_after_node,
                                              edge_label=edge_label,
                                              decimals_number=self.sb_decimals.value())

        self.pte_gv.setPlainText(gv_script)


    def save_gv(self):
        """
        save GV script to file
        """
        if self.pte_gv.toPlainText():

            file_name, filter_ = QFileDialog(self).getSaveFileName(self, "Select the file to save the GraphViz script", "",
                                                                         "GV files (*.gv);;TXT files (*.txt);;All files (*)")

            if file_name:
                with open(file_name, "w") as f_out:
                    f_out.write(self.pte_gv.toPlainText())


    def flow_diagram(self):
        """
        generate flow diagram from pte_gv content
        in PNG or SVG format
        with dot from graphviz package
        """

        if self.pte_gv.toPlainText():

            file_name, filter_ = QFileDialog(self).getSaveFileName(self, "Select the file and format to save the flow diagram", "",
                                                                         "PNG files (*.png);;SVG files (*.svg);;All files (*)")

            if file_name:

                image_format = "png"
                if not os.path.splitext(file_name)[1]:
                    if "svg" in filter_:
                        file_name += ".svg"
                        image_format = "svg"
                    if "png" in filter_:
                        file_name += ".png"
                        image_format = "png"

                gv_script = self.pte_gv.toPlainText()

                with tempfile.NamedTemporaryFile() as temp:
                    tmp_path = pathlib.Path(temp.name)

                with open(tmp_path, "w") as tmp_file:
                    tmp_file.write(gv_script)

                # check dot path
                if self.le_dot_path.text():
                    if not os.path.isfile(self.le_dot_path.text()):
                        QMessageBox.critical(self, "Behatrix",
                                             ("The path for <b>dot</b> program is wrong.<br>"
                                              "Indicate the full path where the <b>dot</b> program from the GraphViz package is installed"))
                        return
                    dot_path = self.le_dot_path.text()
                else:
                    dot_path = "dot"

                cmd = '"{prog}" -T{image_format} "{gv_file}" -o "{file_name}"'.format(prog=dot_path,
                                                                                      file_name=file_name,
                                                                                      gv_file=tmp_path,
                                                                                      image_format=image_format)

                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, error = p.communicate()

                if error:
                    QMessageBox.warning(self, "Behatrix", error.decode("utf-8"))
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
            self.pte_excluded_transitions.insertPlainText("{behavior}:{behavior}\n".format(behavior=behavior))


    def permutation_test(self):

        if self.pte_behav_strings.toPlainText():

            (return_code, sequences,
             d, nodes, starting_nodes, tot_nodes,
             tot_trans, tot_trans_after_node,
             behaviours) = behatrix_cli.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                            behaviors_separator=self.le_behaviors_separator.text(),
                                                            chunk=0)

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

                QMessageBox.information(self, "Behatrix",
                                        ("Randomization finished<br>"
                                         "{} permutations done<br><br>").format(nb_randomization_done))

            else:
                QMessageBox.warning(self, "Behatrix", "Select the number of permutations to execute")

        else:
            QMessageBox.warning("Behatrix", "No behavioral strings found!")


    def flow_chart_significant(self):
        """
        draw flow chart with transitions significativity
        """
        (return_code, sequences,
         unique_transitions, nodes, starting_nodes, tot_nodes,
         tot_trans, tot_trans_after_node,
         behaviors) = behatrix_cli.behav_strings_stats(self.pte_behav_strings.toPlainText(),
                                                        behaviors_separator=self.le_behaviors_separator.text(),
                                                        chunk=0)

        edge_label = "percent_node"
        if self.rb_percent_after_behav.isChecked():
            edge_label = "percent_node"
        if self.rb_percent_total_transitions.isChecked():
            edge_label = "percent_total"
        if self.rb_fraction_after_behav.isChecked():
            edge_label = "fraction_node"

        try:
            cutoff_all = float(self.le_cutoff_total_transition.text())
        except Exception:
            QMessageBox.critical(self, "Behatrix", "{} value is not allowed")
            return
        try:
            cutoff_behavior = float(self.le_cutoff_transition_after_behav.text())
        except Exception:
            QMessageBox.critical(self, "Behatrix", "{} value is not allowed")
            return

        gv_script = behatrix_cli.draw_diagram(cutoff_all=cutoff_all,
                                              cutoff_behavior=cutoff_behavior,
                                              unique_transitions=unique_transitions,
                                              nodes=nodes,
                                              starting_nodes=[],
                                              tot_nodes=tot_nodes,
                                              tot_trans=tot_trans,
                                              tot_trans_after_node=tot_trans_after_node,
                                              edge_label=edge_label,
                                              decimals_number=self.sb_decimals.value(),
                                              significativity=self.permutations_test_matrix,
                                              behaviors=behaviors)




    def save_random(self):
        """
        save matrix
        """
        if self.pte_random.toPlainText():

            file_name, filter_ = QFileDialog(self).getSaveFileName(self, "Select the file to save the matrix", "",
                                                                         "TSV files (*.tsv);;TXT files (*.txt);;All files (*)")

            if file_name:
                with open(file_name, "w") as f_out:
                    f_out.write(self.pte_random.toPlainText())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.show()
    mainWindow.raise_()
    sys.exit(app.exec_())
