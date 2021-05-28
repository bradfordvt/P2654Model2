rem build script for p2654callback library
del CMakeCache.txt
"C:\Program Files\CMake\bin\cmake.exe" -DCMAKE_BUILD_TYPE=Debug ..
"C:\Program Files\CMake\bin\cmake.exe" --build .
