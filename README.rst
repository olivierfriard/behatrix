=================================
BSA (Behavioral Strings Analysis)
=================================

Requirements
============

* numpy
* PyQt5 for the GUI version


Usage of command line utility
=============================

.. code-block:: text

    usage: bsa_multi_cl.py [-h] [-v] [--strings STRINGS] [--output OUTPUT]
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
    


Example of behavioral strings file
==================================

Behaviors are separated by the pipe character (|) otherwise each character will be interpreted as a behavior

.. code-block:: text

  Swim|Play in the water|Play in the water
  Swim|Play in the water|Swim|Swim|Play in the water|Swim|Play in the water|Play in the water|Alert|Locomotion|Swim
  Locomotion|Locomotion|Alert|Sniff|Rub|Locomotion
  Locomotion|Alert|Alert+Vocalize|Alert+Vocalize|Locomotion
  Locomotion|Alert|Sniff|Rub|Rest|Locomotion|Locomotion|Locomotion|Locomotion+Sniff|Sniff|Alert|Drink|Alert
  Sniff|Manipulate|Locomotion|Locomotion|Locomotion|Locomotion|Rub|Alert|Sniff|Alert|Manipulate|Locomotion
  Manipulate
  Play on the ground|Manipulate|Locomotion
  Rub|Locomotion|Sniff|Alert|Rub|Locomotion|Rub|Locomotion|Rub|Alert|Locomotion|Rub|Sniff|Rub|Sniff|Dig|Rest|Rub|Locomotion|Rub
  Rub|Manipulate|Sniff|Rub|Sniff|Rub|Locomotion|Rub|Locomotion
  Play on the ground|Locomotion
  Locomotion|Manipulate|Alert|Sniff|Sniff+Locomotion|Sniff|Manipulate|Sniff
  Self-groom|Sniff|Locomotion|Locomotion+Sniff|Sniff|Defecate|Defecate+Urinate|Defecate+Urinate+Yawn|Urinate|Locomotion|Locomotion+Sniff|Sniff
  Sniff|Sniff|Defecate|Defecate+Urinate|Defecate+Urinate+Stomp|Defecate+Urinate|Defecate+Urinate+Yawn|Urinate|Locomotion|Dig|Locomotion
  Play on the ground
  Locomotion|Sniff|Locomotion|Locomotion+Sniff|Sniff|Locomotion|Locomotion|Rub|Sniff
  Rub|Sniff|Rub|Locomotion
  Alert|Alert+Vocalize|Alert+Vocalize|Rub|Rub+Vocalize|Rub+Vocalize|Vocalize|Alert|Alert+Vocalize|Alert+Vocalize|Alert+Vocalize|Rub|Alert|Rub|Alert|Self-groom|Alert|Rub|Locomotion|Locomotion
  Locomotion|Alert|Locomotion|Alert|Locomotion|Locomotion|Locomotion|Locomotion+Sniff|Locomotion|Alert|Locomotion|Rub|Alert|Rub|Alert|Rub|Alert|Rub|Allogroom|Rub|Alert|Rub|Alert|Rub|Alert|Locomotion
  Alert|Alert+Vocalize|Alert+Vocalize|Alert+Vocalize|Rub|Self-groom|Alert|Alert+Vocalize|Rub|Locomotion|Alert|Locomotion|Alert|Locomotion
  Sniff|Alert|Locomotion
  Locomotion|Alert|Rub|Self-groom|Alert|Self-groom|Rub|Self-groom|Alert|Rub|Alert|Rub
  Rub|Sniff|Alert|Sniff|Alert|Rub|Sniff|Rub|Alert|Locomotion
  Rub|Alert|Rub|Sniff|Rub
  Rub|Rub|Sniff
  Locomotion|Manipulate|Alert|Locomotion|Manipulate|Tear|Manipulate|Tear
  Self-groom|Locomotion|Self-groom|Alert|Self-groom|Alert|Locomotion
  Alert|Locomotion|Locomotion+Sniff|Sniff|Manipulate|Locomotion|Locomotion+Sniff|Sniff|Manipulate|Sniff|Sniff+Locomotion|Sniff|Manipulate|Locomotion|Manipulate
  Locomotion|Alert|Locomotion|Alert|Locomotion
  Swim|Swim|Locomotion|Locomotion+Sniff|Locomotion|Locomotion+Sniff|Sniff|Sniff|Swim|Locomotion|Locomotion|Locomotion|Swim|Alert|Swim|Swim|Alert|Eat|Alert|Swim|Alert|Sniff|Eat|Dig|Eat|Locomotion|Dig|Eat|Swim|Alert|Sniff|Alert|Sniff|Dig|Eat|Dig|Eat|Dig|Sniff|Dig|Alert|Dig|Alert|Locomotion
  Sniff|Eat|Sniff|Dig|Eat|Dig|Swim




