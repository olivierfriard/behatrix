#!/usr/bin/env python3

__version__ = '0.0.1'


import os
import sys
import numpy
import subprocess
import concurrent.futures
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from bsa_ui import Ui_MainWindow
import bsa_multi_cl

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        self.setWindowTitle("BSA")

        self.actionAbout.triggered.connect(self.about)

        self.pb_select_behav_strings_file.clicked.connect(self.pbSelectStringsFilename)

        self.pb_statistics.clicked.connect(self.behav_strings_statistics)
        
        self.pb_save_observed_matrix.clicked.connect(self.save_observed_matrix)
        
        self.pb_graphviz_script.clicked.connect(self.graphviz_script)
        
        self.pb_flow_diagram.clicked.connect(self.flow_diagram)
        
        self.pb_run_randomization_test.clicked.connect(self.randomization_test)
        
        self.pte_behav_strings.setLineWrapMode(0)
        
        num_available_proc = int(os.sysconf("SC_NPROCESSORS_ONLN"))
        if num_available_proc <= 2:
            self.sb_nb_cores.setValue(1)
        else:
            self.sb_nb_cores.setValue(num_available_proc - 1)
        

    def about(self):
        QMessageBox.about(self, "BSA", "Behavioral Strings Analysis - Università di Torino")


    def pbSelectStringsFilename(self):

        filename = QFileDialog(self).getOpenFileName(self, "Select the file containing the behavioral strings", "", "All files (*)")[0]

        if filename:
            self.leStringsFileName.setText(filename)

            with open(filename) as f_in:
                behav_str = f_in.read()

            self.pte_behav_strings.setPlainText(behav_str)


    def behav_strings_statistics(self):

        if self.pte_behav_strings.toPlainText():
            
            (return_code, sequences, 
             d, nodes , starting_nodes , tot_nodes,
             tot_trans, tot_trans_after_node, behaviours) = bsa_multi_cl.behav_strings_stats(self.pte_behav_strings.toPlainText(), chunk=0)
            
            output = ""
            output += ("Behaviours list:\n================\n{}\n".format("\n".join(behaviours)))
            output += ("\nStatistics\n==========\n")
            output += ('Number of different behaviours: {}\n'.format(len(behaviours)))
            output += ('Total number of behaviours: {}\n'.format(tot_nodes))
            output += ('Number of different transitions: {}\n'.format(len(d)))
            output += ('Total number of transitions: {}\n'.format(tot_trans))
            output +=  ('\nBehaviours frequencies:\n=======================\n')
    
            for behaviour in sorted(behaviours):
                countBehaviour = 0
                for seq in sequences:
                    countBehaviour += seq.count(behaviour)
    
                #output += ('%(behaviour)s\t%(freq).3f\t%(countBehaviour)d / %(tot_nodes)d\n' % {'behaviour': behaviour, 'freq': countBehaviour / tot_nodes, 'countBehaviour': countBehaviour, 'tot_nodes':tot_nodes})

                output += "{behaviour}\t{freq:.3f}\t{countBehaviour} / {tot_nodes}\n".format(behaviour=behaviour,
                                                                                         freq=countBehaviour / tot_nodes,
                                                                                         countBehaviour=countBehaviour,
                                                                                         tot_nodes=tot_nodes
                                                                                         )
                '''
                output += "<tr><td>{behaviour}</td><td>{freq:.3f}</td><td>{countBehaviour} / {tot_nodes}</td></tr>".format(behaviour=behaviour,
                                                                                         freq=countBehaviour / tot_nodes,
                                                                                         countBehaviour=countBehaviour,
                                                                                         tot_nodes=tot_nodes
                                                                                         )
                '''
                
            self.pte_statistics.setPlainText(output)

        else:
            QMessageBox.warning(self, "BSA", "No behavioral strings found!")


    def save_observed_matrix(self):

        (return_code, sequences, 
             d, nodes , starting_nodes , tot_nodes,
             tot_trans, tot_trans_after_node, behaviours) = bsa_multi_cl.behav_strings_stats(self.pte_behav_strings.toPlainText(), chunk=0)
             
        if sequences:

            observed_matrix = bsa_multi_cl.create_observed_transition_matrix(sequences, behaviours)
            
            file_name = QFileDialog(self).getSaveFileName(self, "Select the file to save the matrix", "", "All files (*)")[0]        
    
            with open(file_name, mode="wb") as f:
                header = "\t{}\n".format("\t".join(list(behaviours)))
                f.write(header.encode())
                row_names = numpy.array(behaviours, dtype="|S1000")[:, numpy.newaxis]
                data = numpy.char.mod("%8.6f", observed_matrix)
                numpy.savetxt(f, numpy.hstack((row_names, data)), fmt='%s', delimiter='\t')
        else:
            QMessageBox.warning(self, "BSA", "No behavioral strings found!")


    def graphviz_script(self):
        """
        generate flow diagram in PNG or SVG format with dot from graphviz package
        """
        (return_code, sequences, 
         d, nodes , starting_nodes , tot_nodes,
         tot_trans, tot_trans_after_node, behaviours) = bsa_multi_cl.behav_strings_stats(self.pte_behav_strings.toPlainText(), chunk=0)

        if self.rb_percent_after_behav.isChecked():
            edge_label = "percent_node"
        if self.rb_percent_total_transitions.isChecked():
            edge_label = "percent_total"
        if self.rb_fraction_after_behav.isChecked():
            edge_label = "fraction_node"

        try:
            cutoff_all = 0
            cutoff_all = float(self.le_cutoff_total_transition.text())
        except:
            QMessageBox.critical(self, "BSA", "{} value is not allowed")
            return
        try:
            cutoff_behavior = 0
            cutoff_behavior = float(self.le_cutoff_transition_after_behav.text())
        except:
            QMessageBox.critical(self, "BSA", "{} value is not allowed")
            return


        file_name, filter_ = QFileDialog(self).getSaveFileName(self, "Select the file to save the GraphViz script", "",
                                                               "GV files (*.gv);;TXT files (*.txt);;All files (*)")

        if file_name:
            gv_script = bsa_multi_cl.draw_diagram(cutoff_all=cutoff_all,
                                              cutoff_behavior=cutoff_behavior,
                                              d=d,
                                              nodes=nodes,
                                              starting_nodes=[],
                                              tot_nodes=tot_nodes,
                                              tot_trans=tot_trans,
                                              tot_trans_after_node=tot_trans_after_node,
                                              edge_label=edge_label)
            with open(file_name, "w") as f_out:
                f_out.write(gv_script)

            QMessageBox.information(self, "BSA", "GraphViz script saved")
 

    def flow_diagram(self):
        """
        generate flow diagram in PNG or SVG format with dot from graphviz package
        """
        
        (return_code, sequences, 
         d, nodes , starting_nodes , tot_nodes,
         tot_trans, tot_trans_after_node, behaviours) = bsa_multi_cl.behav_strings_stats(self.pte_behav_strings.toPlainText(), chunk=0)

        if self.rb_percent_after_behav.isChecked():
            edge_label = "percent_node"
        if self.rb_percent_total_transitions.isChecked():
            edge_label = "percent_total"
        if self.rb_fraction_after_behav.isChecked():
            edge_label = "fraction_node"

        try:
            cutoff_all = 0
            cutoff_all = float(self.le_cutoff_total_transition.text())
        except:
            QMessageBox.critical(self, "BSA", "{} value is not allowed")
            return
        try:
            cutoff_behavior = 0
            cutoff_behavior = float(self.le_cutoff_transition_after_behav.text())
        except:
            QMessageBox.critical(self, "BSA", "{} value is not allowed")
            return


        gv_script = bsa_multi_cl.draw_diagram(cutoff_all=cutoff_all,
                                              cutoff_behavior=cutoff_behavior,
                                              d=d,
                                              nodes=nodes,
                                              starting_nodes=[],
                                              tot_nodes=tot_nodes,
                                              tot_trans=tot_trans,
                                              tot_trans_after_node=tot_trans_after_node,
                                              edge_label=edge_label)

        file_name, filter_ = QFileDialog(self).getSaveFileName(self, "Select the file to save the flow diagram", "",
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

            gv_script = gv_script.replace("(", "\\(").replace(")", "\\)").replace("\n", " ")
            cmd = """echo '{gv_script}' | dot -T{image_format} -o "{file_name}" """.format(file_name=file_name,
                                                                                           gv_script=gv_script,
                                                                                           image_format=image_format)
            
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, error = p.communicate()
            
            if error:
                QMessageBox.warning(self, "BSA", error.decode("utf-8"))
            else:
                QMessageBox.information(self, "BSA", "The flow diagram was generated in {}".format(file_name))


    def randomization_test(self):

        if self.pte_behav_strings.toPlainText():
        
            (return_code, sequences, 
                 d, nodes , starting_nodes , tot_nodes,
                 tot_trans, tot_trans_after_node, behaviours) = bsa_multi_cl.behav_strings_stats(self.pte_behav_strings.toPlainText(), chunk=0)
                 
            # check exclusion list
            if self.pte_excluded_transitions.toPlainText():
                result = bsa_multi_cl.check_exclusion_list(self.pte_excluded_transitions.toPlainText(), sequences)

                if not result["error_code"]:
                    exclusion_list = result["exclusion_list"]
                else:
                    QMessageBox.warning(self, "BSA", result["message"])
                    return
            else:
                exclusion_list = {}
            
            if self.leNumberRandomizations.text():
                try:
                    nrandom = int(self.leNumberRandomizations.text())
                except:
                    nramdom = 0
                    QMessageBox.warning(self, "BSA", "The number of randomizations is not valid")
                    return
        
            if nrandom:
                
                self.statusbar.showMessage("Randomization test running... Be patient", 0)
                app.processEvents()
        
                num_proc = self.sb_nb_cores.value()
    
                observed_matrix = bsa_multi_cl.create_observed_transition_matrix(sequences, behaviours)
            
                results = numpy.zeros((len(behaviours), len(behaviours)))
                with concurrent.futures.ProcessPoolExecutor() as executor:
                    lst = []
                    n_required_randomizations = 0
                    for i in range(num_proc):
                        if i < num_proc - 1:
                            n_random_by_proc = nrandom // num_proc
                        else:
                            n_random_by_proc = nrandom - n_required_randomizations

                        lst.append(executor.submit(bsa_multi_cl.strings2matrix_cl,
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

                print("nb_randomization_done", nb_randomization_done)
    
                file_name = QFileDialog(self).getSaveFileName(self, "Select the file to save the matrix", "", "All files (*)")[0]
                if not file_name:
                    return
                
                #file_name = '{fileName}.randomized_transitions.{nrandom}.tsv'.format(fileName=os.path.splitext(self.leStringsFileName.text())[0], nrandom=nrandom)
    
                with open(file_name, mode="wb") as f:
                    header = "\t{}\n".format("\t".join(list(behaviours)))
                    f.write(header.encode())
                    row_names = numpy.array(behaviours, dtype="|S1000")[:, numpy.newaxis]
                    data = numpy.char.mod("%8.6f", results / nrandom)
                    numpy.savetxt(f, numpy.hstack((row_names, data)), fmt="%s", delimiter="\t")
                
                self.statusbar.showMessage("Randomization test done", 5000)

                QMessageBox.information(self, "BSA", ("Randomization text finished<br>"
                                                   "{} randomizations done<br><br>"
                                                   "Results were saved in file:<br>{}").format(nb_randomization_done, file_name))
        
            else:
                QMessageBox.warning(self, "BSA", "Select the number of randomizations to execute")

        else:
            QMessageBox.warning(self, "BSA", "No behavioral strings found!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.show()
    mainWindow.raise_()
    sys.exit(app.exec_())
