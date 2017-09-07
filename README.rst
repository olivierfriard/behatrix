=================================
BSA (Behavioral Strings Analysis)
=================================

Requirements
============

* numpy
* PyQt5 for the GUI version


Usage
======


.. usage: bsa_multi_cl.py [-h] [-v] [--strings STRINGS] [--output OUTPUT]
                       [--exclusions EXCLUSIONS] [--n_random NRANDOM]
                       [--n_cpu N_CPU] [--block_first] [--block_last]
                       [--verbose]

    Behavioural Strings Analysis (BSA) command line utility
    
    optional arguments:
      -h, --help            show this help message and exit
      -v                    BSA version
      --strings STRINGS     Path of file containing behavioral strings
      --output OUTPUT       Path of output files
      --exclusions EXCLUSIONS
                            Path of file containing exclusions
      --n_random NRANDOM    Number of randomizations
      --n_cpu N_CPU         Number of CPU to use for randomizations test
      --block_first         block first behavior during randomization test
      --block_last          block last behavior during randomization test
      --verbose             Print results on terminal
    
