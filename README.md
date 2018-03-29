# MCpMC
Statistical model checking of pMC

This prototype is implemented using python 3.6 (we give no guaranties for other versions)

Dependencies:
  - sympy : to represent expressions (to install: sudo pip install sympy)
  - ply : to parse the models (to install: pip install ply)
  - memory-profiler (to install: pip install memory_profiler)
  - matplotlib (to install: pip install matplotlib)
  
    (On a Debian-derived Linux distribution, e.g. Ubuntu, you can install the packages python3-sympy, python3-ply, python3-memory-profiler, and python3-mpltoolkits.basemap)
  
  to execute: run python main.py in a terminal
  
  To execute on different examples, change the last line of main.py to:
 
    - toy() # to perform 10000 simulations of length 100 on example/toy.pm
    
    - toym() # to perform 10000 simulations of length 100 on example/toymult.pm (identical to toy.pm but with 100 parameters)
    
    - zeroconf() # to perform 10000 simulations of length 500 on example/zeroconf.pm
    
    - crowd() # to perform 10000 simulations of length 1000000 on example/crowds.pm
    
    - main() # !! change line 197 and 198 to modify the number and length of runs. In this case, you can also run: python main.py probabilitisc_model_path to parse and execute simulation on the model located at probabilitisc_model_path
