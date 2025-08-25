# @Author: Dr. Jeffrey Chijioke-Uche
# @Date: 2025-06-07
# @Description: Describes the QPU Processor Types for Qiskit Connector
# @License: Apache License 2.0  
# @Copyright (c) 2024-2025 Dr. Jeffrey Chijioke-Uche, All Rights Reserved.
# @Copyright by: U.S Copyright Office
# @Date: 2024-03-01
# @Last Modified by: Dr. Jeffrey Chijioke-Uche    
# @Last Modified time: 2025-06-09
# @Description: This module provides a connector to IBM Quantum devices using Qiskit Runtime Service.
# @License: Apache License 2.0 and creative commons license 4.0
# @Purpose: Software designed for Pypi package for Quantum Plan Backend Connection IBM Backend QPUs Compute Resources Information
#
# Any derivative works of this code must retain this copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals. All rights reserved by Dr. Jeffrey Chijioke-Uche.
#_________________________________________________________________________________
# This file is part of the Qiskit Connector Software.
from pathlib import Path
import os

eagle = f"""                                                                         
                 ░▒███▒░▒███▒                                                       
                 ░▒███▒░▒███▒                                              
                 ▒██▒░░░▒█▓██                                              
                ▒█▓▒▒  ░▒██▒█▓░                                            
                ██▒█▒░░░░░▓█░▓█▓▒▓█████▓▒░                                 
               ▒█░█▒      ░▓▓▒▓█▒▒▒░ ░▒▒▒█▓░                               
              ░██▓█▒░   ░▒▒██░█▓▒▓█████▓▒░▓█▓░                             
              ░████▒░   ▓█▓▒▓██▓▒░     ░▒▒▒░▓█▒░                           
              ░▒██▓     █▓█▓█▓░        ░▒▓▒▒▒░██▒░                         
              ░▒██░     █████░         ▒▓▒▒ ▒░▒▒▒██▒                  
                        ▒█░█▒        ░▓▒▒▒▒▒░▒░▒▒▒██▒                      
                        ░▓█▒█▒░     ░▒▓░▒░▒░▒▒░▒ ▒▒▒█▓░                    
                         ░██░██▒  ░▒▓▒▒▒▒░▒░▒░▒▒▒▓░▒░▒█▓░                  
                          ░▓█▒▒██▒░▓▒▒░▒░▒▒░▒░▒░▒░▒▒░▒░▓█▓░                
                            ▒██▒▒█▓░▓▒░▒░▒░▒░▒▒░▒░▒░▒▒░▒░▓█▓░              
                             ░▒██░▒█▒▓█▒▒▒░▒ ▒░▒▒░▒░▒░▒▒▒▒░██▒░            
                               ░▒██░▓█░▓█░▒▒▒▒░▒ ▒▒▒▒░▒░▒▒▒▒░██▒           
                                 ░▒█▓ ▓█ █▓░▓█▒▒▓█▒░░▓▓▒░▒▒▒▒░▓▓░          
                                   ░▓█▓███░█▓▒▓▒▒▒▒▒▒▒▒▒▒▓▒░▒██▒           
                                    ░▒█░▒▒█▓▓██▒░▒█▓▒░▓█▒▒▒▒▓▒░            
                                 ░▓███▒███▒▒█▓▒█▒▒▒░▒░▒▒▒▒▓█░              
                                 ░▓▒▒▒██▒▒██▒▓▒▒██▒▒▒▒▒ ▒█▒█░              
                                 ░▓███▒   ░▒██▒  ▒██░▒▒▒▒▓▓█░              
                                                  ░▒█▓ ▒▒▓▒█░              
                                                    ░▓█▓░▒▓█░              
                                                      ░▓███▒░              
                                                        ░░░                                                                                      
                                  Eagle Quantum Processor                                                      
"""


heron = f"""
                       ░▒████████████▓▒░                                   
                       ░▒▒   ░▒█▓▒░▒░▒▒███▒░                               
                       ░▒████▓▓▒█████▓▒▒░▒▓███▓▒░░                         
                            ░█▒▓█▒░  ░▒██▓▒▒░▒▒▓████▒▒░                    
                            ▒█▒█░  ░▒▓██▓▒▒▒▒▒░▒▓▓▓██▓▒░                   
                            ▓█▓█   ░█▓▒░░░░░░░▒▓████▒▒▒░                   
                            ▓█▒█░  ▒█▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▒░                   
                            ▒█░█▒░ ░▓█▒▒▓██▒░                              
                            ░▓█░██▒░░▓██▒░▒█▓▒                             
                             ░▓█▒▒▓░   ░▓██▒▒█▓░                           
                              ░▒██▒░░░░  ░▒█▓░█▓░                          
                              ░░▓▓▓██████▒░░▓█░█▓░                         
                             ▒▓█▒░ ░░░░░░▒█▓░▒█░█░                         
                           ▒██▒░▓████████▓░▓█▒█▒█▒                         
                         ░▓█▓░██▒░      ░▓█▓▓██▒█▒                         
                       ░▒█▓ ▓█░▓▓▒░       ▒█▒██░█░                         
                     ░▒██░▓█░▓▓░▒░▒▓▒░     ▓█▓▒██░                         
                   ░▒██▒▒█▒▒▓░▒▓ ▓▓▒▓░░░  ░██░██░                          
                  ▒▓█▒▒█▓▒▓▒▒▓▒▓█░▒▓░▓▓▒░░▓█▒██▒                           
                ░▓█▒░█▓▒█▒▒▓▒▒█▒▒█▒▓█▒▒▒▒██░██▒                            
              ░▓█▓░▓▓░▓▒░▓▒▒█▒▒█▒▒█▒▒█▒▒██░██░                             
             ▒██░▓▓▒██░▓▓░█▓░█▓▒█▒▒█▓░▓▒▒█▒█▒                              
            ░▒▓▒▒▒██░██░█▓ ██░█▓░██▒▒█░▓▓█░█▒                              
            ░▒▓▒▓▓░██▒▓█░▓█ █▓ ▓█▓░ ▒█▒█░█░█▒                              
             ░▓█▒▓█▒██▓▒▓░▓▓░▓█▓░   ▓█▒█░█░█▒                              
             ░▓▓▒▒▒▒▒░▓▒░▒░▓██▒     ▓█▒█░█░█▒                              
             ░▓█▓▒▒▓███▒▒▓█▓▒       ▒█▒█░█░█▒                              
               ░▒▒▒▒▒░▒▒▒▒░░        ▓█▒█░█░█▒                              
                                    ▓█▒█░█░█▒                              
                                    ▒█▒█░█░█▒                              
                                    ▓█▒█░█░█▒                              
                                    ▒█▒█░█░█▒                              
                                    ▒▓▓▓░█▓█▒                              
                                    ░▒▒▒░▒▓▒░                              
                      Heron Quantum Processor            
"""

flamingo = f"""
                                        ░░░▒▒▒▒▒▒▒░░░                                                 
                                     ░▒▓▓▓▒░░░▒▓▓▓▓▓▒▒░░                                            
                                    ░▒▓▒░▒▒▒▒▒▒▒░░░▒▒▓▓▓░░                                          
                                   ░▒▓▒▒▓▓▒░░░▒▒▓▒░░░░▒▓▓▒░                                         
                                   ░▒█░█▒░ ░▒▓▓▓▓▒░░░▒▒░▓▓░                                         
                                   ░▒█░█▒░ ░▒▒░░░▒▓▓▓▓▓▓░▓▒                                         
                                   ░▒▓▒▓▓▒░░▒▓▓▓▓▓▒░░▒▓██▓▓                                         
                                    ░▒▓▒▒▓▓░░▒░░░     ░░▒▒░                                         
                                     ░▒▓▓░▒▓▓▓░░░       ░░░                                         
                             ░░░▒▒▓▓▓▓▒░▒▓▓░░▓▓▓▒░░                                                 
                          ░░▒▓▓▓▓▓▒▒▒▒▓▓▓▓░▒▓▒░▒▓▓▒░░                                               
                        ░░▒▓█▓░░▒▒▓▓▓▓▒▒░░▒▓▒▒▓▓▒▒▓▓░░                                              
                      ░░▒▓▓▒░▓█▓▓▓▒▒▒▒▓▓▓█▓▒▒▒░▒▓▓░▓▓▒░                                             
                    ░░▒▓▓▒░▓█▓▒░        ░░▒▓▒░░░░▒▓░▓▓░                                             
                   ░▒▓▓▒░▓▓▒░░                   ░▓▓░▓▒░                                            
                 ░░▓▓▒░▓▓░▓▓▒░░░░                 ▒▓░▓▒░                                            
                ░▒▓▓░▓▓░▓▓░▒▒▒▓▓▒░               ░▒▓░▓▒░                                            
               ░▒▓▒▒▓░▒▓░▒▓▒▒▓▒▒▒░              ░▒▓▒▒▓░░                                            
               ░▒▓░▓▒▓▒▒▓▒▒▓▒░▓▓▒░░░░░░░░░░░░░░▒▓▓▒▒▓▒░                                             
               ░▒█▒▓▒░▓▒░▓▓░▓█▓░ ░▓███████████▓▓░░▓▓▒░                                              
               ░▒█▓▒█▒░▓▓░▓█▓░░░▒▓██▓▒░░░░░░░░░▒▓▓▓░░                                               
               ░▒▓░▓▒▓▓░▒█▓▒░░▒▓█▒▒▒▓█▓███████▓▓▒░                                                  
               ░▒▓░▓▓░▒▓▓▒░░▒▓█▒░▓▓▒▒▓░                                                             
               ░░▓▓▒▒▓▓▒░░▒▓█▓░▓█▒▒▒▒▓░                                                             
                ░▒▓█▓▒░░░▓██▒░▒░▒▓█▓▓█▓▓▓▓▓▓▓▓▒▒░                                                   
                 ░░░░░░░▒▓▒░▒░▒▒▒▒▓▓▒▓▒▒▒▒▒▒▒▒▓█▓▒░                                                 
                      ░░▒▓▓█▓▓▓▓▓▓█▓▓█▓▓▓▓▓▓▓▓▒▒▒▒░                                                 
                      ░░▒▒▒▒▒▒▒▒▒▒▓▓▓▓▒▒▒▒▒▒▒▒▓▓▓▒░                                                 
                                 ░▓▓▒▓░       ░░░░                                                  
                                 ░▓▓▒▓░                                                             
                                 ░▓▓▒▓░                                                             
                                 ░▓▓▒▓░                                                             
                                 ░▓▓▒▓░                                                             
                                 ░▓▓▒▓▓▓▒░                                                          
                                 ░▒▓▓▒░▒▒░                                                          
                                 ░░▓▓▓▓▓▒░                                                          
                                ░░░░░░░░                                                            
               Flamingo Quantum Processor
"""

condor = f"""
                        ░░███████▒░░                                             
                       ░████▒░▒▓███▒                                             
                     ░███▓██████████░                                            
                    ░▓████▒█▒ ░▒████░                                            
                    ░██▒████▒  ░████░                                            
                    ░███▓███▒░███████▓░                                          
                     ▒█████░███████░███░                                         
                      ▒▓▒░▓████████████░                                         
                        ▒███▓███░ ░████▓░░                                       
                       ███░███░   ░██████████░░                                  
                      ▒█████▒     ░▓████▓░▓▓█████░░                              
                      ██▓██░   ░▒▓██▓▓▒▓██████░████▒                             
                      ████░ ░▓████▒▒▒▒▒▒▒▓▒▒█████▓██▓░                           
                      ██▒██▒▓██▓████████▓▓▒  ░░███▓██▒                           
                      ▒███████████▒▒▒▒▒▒▒▒░     ░█████▓                          
                       ▒███▓█▒██░                ░█████▒                         
                        ░▓████▓██░███▓░███▒▒███▒░██░████▒                        
                            ▒██▒█████████████▓████████▒██▒                       
                            ░▓██▒██▓█░██▒█▒████▓████▓██▓██▒                      
                              ░██▓███▓█▒█▒██▓█░█▓▓█░██▒████▒                     
                               ▒███▓███░▒▓█▒██▓█▒█▓██░██████░                    
                               ▒█▒███▓▒▒░████░████░█▒██▓█████▒░                  
                               ▒█▒██████████▒███████▓█░████▓███▒                 
                               ▒███████▓██████▓▒███▓██░▓░█▒██▒███▒░              
                               ░██████▒░ ░░▒█████████▓▒▓█████▓▓████░             
                                ░░░░░░░          ░▓██████████▓█████░             
                                                     ░▒████████████░                
                                Condor Quantum Processor                                                                                                                                                                                                                               
"""
###########################################################################


# Processors:
# ───────────────────────────────
# Known processor image filenames
# ───────────────────────────────
processor_media_files_array = [
    # Removebg images
    "eagle-2021-removebg.png",
    "heron-2023-removebg.png",
    "flamingo-2025-removebg.png",
    "condor-2023-removebg.png",
    "egret-2023-removebg.png",
    "falcon-2019-removebg.png",
    "hummingbird-2019-removebg.png",
    "canary-2017-removebg.png",
    # Effects images
    "eagle-2021-effects.png",
    "heron-2023-effects.png",
    "flamingo-2025-effects.png",
    "condor-2023-effects.png",
    "egret-2023-effects.png",
    "falcon-2019-effects.png",
    "hummingbird-2019-effects.png",
    "canary-2017-effects.png",
]

# ───────────────────────────────
# Local & remote base paths
# ───────────────────────────────
this_file  = Path(__file__).resolve()
media_dir  = this_file.parent / "media"
remote_dir = "https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media"

# ───────────────────────────────
# Build variables at runtime
# ───────────────────────────────
#initialize empty image path string if not found:
global default_processor
default_processor = "QConnV2.ico"
default_target_file = media_dir / default_processor

#____________________________________________
# Check if media directory exists, if not create it
#_____________________________________________
for filename in processor_media_files_array:
    varname = filename.replace("-", "-").replace(".png", "")
    target_file = media_dir / filename
    if target_file.exists():
        globals()[varname] = target_file
        if varname.__eq__("eagle-2021-removebg"):
            eagle_processor = target_file
        elif varname.__eq__("heron-2023-removebg"):
            heron_processor = target_file
        elif varname.__eq__("flamingo-2025-removebg"):
            flamingo_processor = target_file
        elif varname.__eq__("condor-2023-removebg"):
            condor_processor = target_file
        elif varname.__eq__("egret-2023-removebg"):
            egret_processor = target_file
        elif varname.__eq__("falcon-2019-removebg"):
            falcon_processor = target_file
        elif varname.__eq__("hummingbird-2019-removebg"):
            hummingbird_processor = target_file
        elif varname.__eq__("canary-2017-removebg"):
            canary_processor = target_file
        elif varname.__eq__("eagle-2021-effects"):
            j_eagle_processor = target_file
        elif varname.__eq__("heron-2023-effects"):
            j_heron_processor = target_file
        elif varname.__eq__("flamingo-2025-effects"):
            j_flamingo_processor = target_file
        elif varname.__eq__("condor-2023-effects"):
            j_condor_processor = target_file
        elif varname.__eq__("egret-2023-effects"):
            j_egret_processor = target_file
        elif varname.__eq__("falcon-2019-effects"):
            j_falcon_processor = target_file
        elif varname.__eq__("hummingbird-2019-effects"):
            j_hummingbird_processor = target_file
        elif varname.__eq__("canary-2017-effects"):
            j_canary_processor = target_file
            print(f"🌐 Live")
    else:
        globals()[varname] = f"{remote_dir}/{filename}"
        if varname.__eq__("eagle-2021-removebg"):
            eagle_processor = default_target_file
        elif varname.__eq__("heron-2023-removebg"):
            heron_processor = default_target_file
        elif varname.__eq__("flamingo-2025-removebg"):
            flamingo_processor = default_target_file
        elif varname.__eq__("condor-2023-removebg"):
            condor_processor = default_target_file
        elif varname.__eq__("egret-2023-removebg"):
            egret_processor = default_target_file
        elif varname.__eq__("falcon-2019-removebg"):
            falcon_processor = default_target_file
        elif varname.__eq__("hummingbird-2019-removebg"):
            hummingbird_processor = default_target_file
        elif varname.__eq__("canary-2017-removebg"):
            canary_processor = f"{remote_dir}/{filename}"
        # Effects images
        elif varname.__eq__("eagle-2021-effects"):
            j_eagle_processor = default_target_file
        elif varname.__eq__("heron-2023-effects"):
            j_heron_processor = default_target_file
        elif varname.__eq__("flamingo-2025-effects"):
            j_flamingo_processor = default_target_file
        elif varname.__eq__("condor-2023-effects"):
            j_condor_processor = default_target_file
        elif varname.__eq__("egret-2023-effects"):
            j_egret_processor = default_target_file
        elif varname.__eq__("falcon-2019-effects"):
            j_falcon_processor = default_target_file
        elif varname.__eq__("hummingbird-2019-effects"):
            j_hummingbird_processor = default_target_file
        elif varname.__eq__("canary-2017-effects"):
            j_canary_processor = default_target_file
            print(f"🌐 Active")


############################################################
qcon =  rf"""
   ____   ______                                  __              
  / __ \ / ____/____   ____   ____   ___   _____ / /_ ____   _____
 / / / // /    / __ \ / __ \ / __ \ / _ \ / ___// __// __ \ / ___/
/ /_/ // /___ / /_/ // / / // / / //  __// /__ / /_ / /_/ // /    
\___\_\\____/ \____//_/ /_//_/ /_/ \___/ \___/ \__/ \____//_/     
                                                                  
🧠 Qiskit Connector® for Quantum Backend Realtime Connection
"""