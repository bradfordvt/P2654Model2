# P2654Model2
Second generation experimentation with P2654 callback concept as a demonstration.

The following describes the sections of the project tree:
##docs
This directory contains documentation files describing the concepts
behind the P2654Model2 project.  These are the currently available
files.
###P2654-P1687_1-Unified Concepts.pptx
This presentation contains the inspirations and concepts
gleaned out of my analysis activities regarding the
scope and purpose of IEEE P2654 and IEEE P1687.1.
The goal of this effort is to try to establish a
common callback strategy for both proposed standards
efforts.

This document is not a stable and static view document.
My intent is to update this document as new ideas
and insight are discovered.  Thus, citations to this
document should indicate a date to when it was referenced.
The GitHub change management tooling should allow
accurate retrieval of the version cited.

###MJBUnification20210720.pptx
This presentation contains the overview of demarcation between IEEE P2654 and IEEE P1687.1.
The concept of a P2654 Transport Layer Channel is introduced consisting of
RVFMessage packets transporting Bottom-Up Requests and Responses an RVFCommand
packets transporting Top-Down Requests and Responses between P2654 Nodes in the P2654 Tree model.
###P2654_C4Model_Architecture.docx
This document contains the C4 Model diagrams representing the context
of the various use case perspectives identified by the P2654 and P1687.1 working groups.  The
diagrams were created using PlantUML.  The source PUML files
may be found under the docs/puml directory.
###C4 Models found under docs/puml/context
| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/context_systemFCT.puml) |
| --- |
| *Figure 1 - docs/puml/context/context_systemFCT.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/context_boardFCT.puml) |
| --- |
| *Figure 2 - docs/puml/context/context_boardFCT.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/context_boardICT.puml) |
| --- |
| *Figure 3 - docs/puml/context/context_boardICT.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/context_boardJTAG.puml) |
| --- |
| *Figure 4 - docs/puml/context/context_boardJTAG.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/context_boardEmbedded.puml) |
| --- |
| *Figure 5 - docs/puml/context/context_boardEmbedded.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/context_device.puml) |
| --- |
| *Figure 6 - docs/puml/context/context_device.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/system/Board_ATPG_Tooling_System.puml) |
| --- |
| *Figure 7 - docs/puml/context/system/Board_ATPG_Tooling_System.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/system/Board_ATPG2_Tooling_System.puml) |
| --- |
| *Figure 8 - docs/puml/context/system/Board ATPG2 Tooling System.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/system/Board_ECAD_Tooling_System.puml) |
| --- |
| *Figure 9 - docs/puml/context/system/Board ECAD Tooling System.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/system/Board_EDA_Tooling_System.puml) |
| --- |
| *Figure 10 - docs/puml/context/system/Board EDA Tooling System.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/system/Board_ICT_System.puml) |
| --- |
| *Figure 11 - docs/puml/context/system/Board ICT System.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/system/Board_JTAG_Test_Equipment_System.puml) |
| --- |
| *Figure 12 - docs/puml/context/system/Board JTAG Test Equipment System.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/system/Device_ATE_System.puml) |
| --- |
| *Figure 13 - docs/puml/context/system/Device ATE System.puml* |

| ![uncached image](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/bradfordvt/P2654Model2/main/docs/puml/context/system/Device_EDA_Tooling_System.puml) |
| --- |
| *Figure 14 - docs/puml/context/system/Device EDA Tooling System.puml* |

##drivers
This directory contains the interface code to hardware
drivers used to validate the synchronization of the P2654Model2
software model with simulated or actual hardware implementations.
The current drivers avalable are:
###atesim
This driver interface enables access to the Telnet server
of the P2654Simulations project also found on my GitHub page.
##p2654model2
This directory contains the model Python package files
representing the software model classes to build up a
software model of a system from a description file.
The software model of a system is described using a
JSON formatted description file.  The description is provided
to the software to build up a model of the system
used to stimulate, synchronize with the hardware, and
to manage the connections to the various resources
described to the software model.

###Building protobuf for Windows 10
This package uses the Google Protobuf serialization/deserialization
message library to send messages between specialized users
ModelNodes and strategy plug-ins.  To build the development
environment for Windows 10, the user needs to install
[Visual Studio 2019 Community Edition](https://visualstudio.microsoft.com/vs/community/)
to provide the
compiler needed to build the protobuf package as well
as the C++ code used by this P2654Model2 project.
Compilation cannot be done using MINGW due to the lack
of support for posix multitasking used by the protobuf code
(std::once_flag, std::call_once both from mutex.h).
You also need to install cmake from
[https://cmake.org/install/](https://cmake.org/install/).
I first installed Git for Windows 10 by downloading
and installing the package found at the
[Git-SCM](https://git-scm.com/download/win) site
and installing the package found there.  Next, I opened
a Git bash window to run the commands found in the
instructions at
[https://medium.com/@dev.ashurai/protoc-protobuf-installation-on-windows-linux-mac-d70d5380489d](https://medium.com/@dev.ashurai/protoc-protobuf-installation-on-windows-linux-mac-d70d5380489d).
I used vcpkg.exe where vcpkg is used in the instructions.
A summary of the commands used is shown below:
```bash
$ git clone https://github.com/Microsoft/vcpkg.git
$ cd vcpkg
$ ./bootstrap-vcpkg.sh
$ ./vcpkg.exe integrate install
$ ./vcpkg.exe install protobuf protobuf:x64-windows
$ ./vcpkg.exe list
protobuf:x64-windows                               3.14.0#2         Protocol Buffers - Google's data interchange format
protobuf:x86-windows                               3.14.0#2         Protocol Buffers - Google's data interchange format
$ 
```
The result of the build provides the following instructions:
```text
The package protobuf:x64-windows provides CMake targets:

    find_package(protobuf CONFIG REQUIRED)
    target_link_libraries(main PRIVATE protobuf::libprotoc protobuf::libprotobuf protobuf::libprotobuf-lite)

The package protobuf:x86-windows provides CMake targets:

    find_package(protobuf CONFIG REQUIRED)
    target_link_libraries(main PRIVATE protobuf::libprotoc protobuf::libprotobuf protobuf::libprotobuf-lite)
```
###Building protobuf for Ubuntu Linux
TBD

The decomposition of the package tree is as follows:
###builder
This directory contains the code to read the JSON description
and compose a model representation of the system that is
able to be stimulated and observed to change and monitor the
state of a target system.
####builder.py
Main code to build up the software model from a JSON description.
####configurer.py
Code used to define the environmental configuration of the
runtime demonstration application.  The configuration is provided
to the Configurer using a JSON based description file.
####drivers.py
Factory class used to manage the hardware drivers used by CONTROLLER
building blocks.
####moduleinfo.py
ModuleInfo class describes a Python or Python wrapper
module for interfacing to plugin strategies.
ClassInfo class describes the names and methods
of classes found in these ModuleInfo objects.
FunctionInfo class describes the names of the
methods in a Module or Class.
####moduleloader.py
Utility class used to load in plugin modules for strategies or injectors.
####nodecontainer.py
NodeContainer is a helper class used to cache
association information used to look up nodes
instances.
The application uses the NodeContainer to locate
a node instance based on either the dot path
name or the UUID.
###callback
This directory contains the code used to pass callback
control between external C++ strategies and the
hosting language (Python used by this demonstration model).
The code in this directory is not to be confused
with the P2654 or P1687.1 callback concept, but is
instead a code implementation API for the model
used to pass RVF messages from a dissimilar plug-in
strategy library, and the software model possibly
implemented in a different language.  This p2654model2
demonstration shows the integration of an external C++
strategy library plug-in with a software model
implemented in Python as a different host language.
####p2654callback.h
***CModelError*** is a class to provide a common error
handling mechanism that may be shared between the
external C++ plug-in library and the hosting software
model.

***P2654Callback*** is a base class used to define
a callback representation for passing messages from
the strategy code (that may be an external C++ plug-in)
and the software representing the associated ***ModelNode***.

***P2654Caller*** is a base class for strategy
classes to standardize a common method for passing
messages between the strategy and the registered
callback handler from the ***ModelNode*** specialized
class.  This class provides the sendRequest() and
sendResponse() methods used to pass request and response messages
from the strategy to the ***ModelNode***.
####p2654callback.cc
This file is just a handle for compiling the code
located in p2654callback.h into a dynamic library
that may be integrated with the software model code
as well as the strategy library plug-in.
####p2654callback.i
This file is the Software Wrapper Interface Generator
(SWIG) information description file
that is used to generate the host language wrapper code
around the C++ code.  SWIG may be found at
[swig.org](http://swig.org/). To generate the wrapper code,
the following SWIG command should be used:
```bash
swig -python -o p2654callback_wrap.cpp p2654callback.i
```
####test_p2654callback.cc
Unit test cases for C++ code version of P2654Callback.
####test_p2654callback.py
Unit trst cases for Python code version of the P2654callback wrapper.
