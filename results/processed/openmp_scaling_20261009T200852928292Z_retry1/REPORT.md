# OpenMP scaling report

Complete: True. Measured successes 1800; failed 0; missing 0; warmups 360.

Sequential merge_sort is the primary baseline; parallel request1 is a separate implementation baseline. Ratios use within-dataset medians before equal weighting distinct input fingerprints. Min/max spreads are not confidence intervals. All outliers retained.

| N | Distribution | Threads | Datasets | Sequential-baseline speedup median / min / max | Efficiency median | Parallel1 speedup median |
|---:|---|---:|---:|---|---:|---:|
| 32768 | duplicate_heavy | 1 | 3 | 0.889543 / 0.872849 / 0.893521 | 0.889543 | 1 |
| 32768 | duplicate_heavy | 2 | 3 | 1.46546 / 1.25931 / 1.62019 | 0.732729 | 1.60484 |
| 32768 | duplicate_heavy | 4 | 3 | 1.64536 / 1.57563 / 1.65799 | 0.411339 | 1.80061 |
| 32768 | duplicate_heavy | 8 | 3 | 1.57931 / 1.25816 / 1.62736 | 0.197414 | 1.78038 |
| 32768 | nearly_sorted | 1 | 3 | 0.745994 / 0.74017 / 0.764785 | 0.745994 | 1 |
| 32768 | nearly_sorted | 2 | 3 | 1.22836 / 1.21217 / 1.26615 | 0.614182 | 1.66662 |
| 32768 | nearly_sorted | 4 | 3 | 1.27943 / 1.19305 / 1.32401 | 0.319858 | 1.58673 |
| 32768 | nearly_sorted | 8 | 3 | 1.21792 / 0.83275 / 1.25382 | 0.15224 | 1.62532 |
| 32768 | reverse_sorted | 1 | 3 | 0.631168 / 0.627606 / 0.637506 | 0.631168 | 1 |
| 32768 | reverse_sorted | 2 | 3 | 1.13438 / 1.09256 / 1.13493 | 0.567192 | 1.75166 |
| 32768 | reverse_sorted | 4 | 3 | 1.07081 / 1.03273 / 1.11006 | 0.267701 | 1.77022 |
| 32768 | reverse_sorted | 8 | 3 | 1.06813 / 1.00912 / 1.24718 | 0.133516 | 1.65404 |
| 32768 | sorted | 1 | 3 | 0.684333 / 0.682013 / 0.771563 | 0.684333 | 1 |
| 32768 | sorted | 2 | 3 | 1.1624 / 1.13968 / 1.2362 | 0.581202 | 1.79808 |
| 32768 | sorted | 4 | 3 | 1.10418 / 1.10036 / 1.17091 | 0.276045 | 1.68741 |
| 32768 | sorted | 8 | 3 | 1.04404 / 0.96374 / 1.73486 | 0.130505 | 1.51448 |
| 32768 | uniform | 1 | 3 | 0.934264 / 0.919366 / 0.948692 | 0.934264 | 1 |
| 32768 | uniform | 2 | 3 | 1.66421 / 1.64614 / 1.73314 | 0.832104 | 1.84172 |
| 32768 | uniform | 4 | 3 | 1.68521 / 1.65521 / 1.73066 | 0.421303 | 1.81938 |
| 32768 | uniform | 8 | 3 | 1.66728 / 1.31607 / 1.70627 | 0.208409 | 1.55095 |
| 100000 | duplicate_heavy | 1 | 3 | 0.89513 / 0.863529 / 0.898575 | 0.89513 | 1 |
| 100000 | duplicate_heavy | 2 | 3 | 1.69585 / 1.67522 / 1.72984 | 0.847926 | 1.91247 |
| 100000 | duplicate_heavy | 4 | 3 | 2.0143 / 1.9607 / 2.18748 | 0.503574 | 2.17903 |
| 100000 | duplicate_heavy | 8 | 3 | 3.81716 / 3.52995 / 3.96852 | 0.477145 | 3.90266 |
| 100000 | nearly_sorted | 1 | 3 | 0.759692 / 0.733979 / 0.760769 | 0.759692 | 1 |
| 100000 | nearly_sorted | 2 | 3 | 1.39725 / 1.35154 / 1.41432 | 0.698627 | 1.84144 |
| 100000 | nearly_sorted | 4 | 3 | 1.67962 / 1.54294 / 1.713 | 0.419904 | 2.26745 |
| 100000 | nearly_sorted | 8 | 3 | 2.25733 / 2.18894 / 2.3955 | 0.282166 | 3.1244 |
| 100000 | reverse_sorted | 1 | 3 | 0.631801 / 0.617268 / 0.65031 | 0.631801 | 1 |
| 100000 | reverse_sorted | 2 | 3 | 1.1642 / 1.0448 / 1.21466 | 0.582102 | 1.75391 |
| 100000 | reverse_sorted | 4 | 3 | 1.40695 / 1.36798 / 1.49115 | 0.351738 | 2.30957 |
| 100000 | reverse_sorted | 8 | 3 | 1.90085 / 1.89848 / 1.90805 | 0.237606 | 3.03624 |
| 100000 | sorted | 1 | 3 | 0.705032 / 0.691828 / 0.705768 | 0.705032 | 1 |
| 100000 | sorted | 2 | 3 | 1.26715 / 1.19012 / 1.28878 | 0.633573 | 1.74013 |
| 100000 | sorted | 4 | 3 | 1.58783 / 1.24499 / 2.35307 | 0.396957 | 2.16113 |
| 100000 | sorted | 8 | 3 | 2.18917 / 2.09921 / 2.47298 | 0.273646 | 3.19217 |
| 100000 | uniform | 1 | 3 | 0.919852 / 0.90778 / 0.933576 | 0.919852 | 1 |
| 100000 | uniform | 2 | 3 | 1.72181 / 1.71778 / 1.73419 | 0.860905 | 2.02423 |
| 100000 | uniform | 4 | 3 | 2.01176 / 1.93099 / 2.02936 | 0.502941 | 2.34073 |
| 100000 | uniform | 8 | 3 | 2.835 / 2.68037 / 3.07942 | 0.354375 | 3.30014 |
| 1000000 | duplicate_heavy | 1 | 3 | 0.890856 / 0.845363 / 0.9078 | 0.890856 | 1 |
| 1000000 | duplicate_heavy | 2 | 3 | 1.75323 / 1.72127 / 1.84527 | 0.876614 | 1.90451 |
| 1000000 | duplicate_heavy | 4 | 3 | 2.33524 / 2.33172 / 2.61423 | 0.58381 | 2.84696 |
| 1000000 | duplicate_heavy | 8 | 3 | 3.56883 / 3.46847 / 3.82687 | 0.446104 | 3.89343 |
| 1000000 | nearly_sorted | 1 | 3 | 0.755023 / 0.712658 / 0.768436 | 0.755023 | 1 |
| 1000000 | nearly_sorted | 2 | 3 | 1.60776 / 1.53186 / 1.61619 | 0.803878 | 2.16595 |
| 1000000 | nearly_sorted | 4 | 3 | 2.19691 / 1.94274 / 2.26921 | 0.549228 | 2.82218 |
| 1000000 | nearly_sorted | 8 | 3 | 3.07947 / 2.49205 / 3.32853 | 0.384933 | 3.7777 |
| 1000000 | reverse_sorted | 1 | 3 | 0.664773 / 0.656188 / 0.680496 | 0.664773 | 1 |
| 1000000 | reverse_sorted | 2 | 3 | 1.37128 / 1.27935 / 1.46279 | 0.685641 | 2.31956 |
| 1000000 | reverse_sorted | 4 | 3 | 1.91438 / 1.78314 / 1.93704 | 0.478596 | 3.32696 |
| 1000000 | reverse_sorted | 8 | 3 | 2.60318 / 2.11169 / 2.92918 | 0.325397 | 4.38451 |
| 1000000 | sorted | 1 | 3 | 0.704061 / 0.669837 / 0.727593 | 0.704061 | 1 |
| 1000000 | sorted | 2 | 3 | 1.29791 / 0.929768 / 1.37846 | 0.648957 | 1.84045 |
| 1000000 | sorted | 4 | 3 | 1.80907 / 1.75399 / 1.92757 | 0.452267 | 2.42579 |
| 1000000 | sorted | 8 | 3 | 2.50176 / 2.45726 / 2.67167 | 0.31272 | 3.59446 |
| 1000000 | uniform | 1 | 3 | 0.934684 / 0.918546 / 0.955206 | 0.934684 | 1 |
| 1000000 | uniform | 2 | 3 | 1.71979 / 1.7108 / 1.74801 | 0.859893 | 1.8423 |
| 1000000 | uniform | 4 | 3 | 2.57281 / 2.41195 / 2.66399 | 0.643204 | 2.72153 |
| 1000000 | uniform | 8 | 3 | 3.04551 / 3.04287 / 3.51286 | 0.380689 | 3.35528 |

## Environment
```json
{
  "build_directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
  "captured_at_utc": "2026-10-09T20:37:49.439617+00:00",
  "cmake": {
    "command": [
      "cmake",
      "--version"
    ],
    "returncode": 0,
    "stderr": "",
    "stdout": "cmake version 3.28.3\n\nCMake suite maintained and supported by Kitware (kitware.com/cmake).\n"
  },
  "cmake_cache": "# This is the CMakeCache file.\n# For build in directory: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release\n# It was generated by CMake: /usr/bin/cmake\n# You can edit this file to change values found and used by cmake.\n# If you do not want to change any of the values, simply exit the editor.\n# If you do want to change a value, simply edit, save, and exit the editor.\n# The syntax for the file is as follows:\n# KEY:TYPE=VALUE\n# KEY is the name of a variable in the cache.\n# TYPE is a hint to GUIs for the type of VALUE, DO NOT EDIT TYPE!.\n# VALUE is the current value for the KEY.\n\n########################\n# EXTERNAL cache entries\n########################\n\n//Build the testing tree.\nBUILD_TESTING:BOOL=ON\n\n//Path to a program.\nCMAKE_ADDR2LINE:FILEPATH=/usr/bin/addr2line\n\n//Path to a program.\nCMAKE_AR:FILEPATH=/usr/bin/ar\n\n//Choose the type of build, options are: None Debug Release RelWithDebInfo\n// MinSizeRel ...\nCMAKE_BUILD_TYPE:STRING=Release\n\n//Enable/Disable color output during build.\nCMAKE_COLOR_MAKEFILE:BOOL=ON\n\n//CXX compiler\nCMAKE_CXX_COMPILER:FILEPATH=/usr/bin/c++\n\n//A wrapper around 'ar' adding the appropriate '--plugin' option\n// for the GCC compiler\nCMAKE_CXX_COMPILER_AR:FILEPATH=/usr/bin/gcc-ar-13\n\n//A wrapper around 'ranlib' adding the appropriate '--plugin' option\n// for the GCC compiler\nCMAKE_CXX_COMPILER_RANLIB:FILEPATH=/usr/bin/gcc-ranlib-13\n\n//Flags used by the CXX compiler during all build types.\nCMAKE_CXX_FLAGS:STRING=\n\n//Flags used by the CXX compiler during DEBUG builds.\nCMAKE_CXX_FLAGS_DEBUG:STRING=-g\n\n//Flags used by the CXX compiler during MINSIZEREL builds.\nCMAKE_CXX_FLAGS_MINSIZEREL:STRING=-Os -DNDEBUG\n\n//Flags used by the CXX compiler during RELEASE builds.\nCMAKE_CXX_FLAGS_RELEASE:STRING=-O3 -DNDEBUG\n\n//Flags used by the CXX compiler during RELWITHDEBINFO builds.\nCMAKE_CXX_FLAGS_RELWITHDEBINFO:STRING=-O2 -g -DNDEBUG\n\n//Path to a program.\nCMAKE_DLLTOOL:FILEPATH=CMAKE_DLLTOOL-NOTFOUND\n\n//Flags used by the linker during all build types.\nCMAKE_EXE_LINKER_FLAGS:STRING=\n\n//Flags used by the linker during DEBUG builds.\nCMAKE_EXE_LINKER_FLAGS_DEBUG:STRING=\n\n//Flags used by the linker during MINSIZEREL builds.\nCMAKE_EXE_LINKER_FLAGS_MINSIZEREL:STRING=\n\n//Flags used by the linker during RELEASE builds.\nCMAKE_EXE_LINKER_FLAGS_RELEASE:STRING=\n\n//Flags used by the linker during RELWITHDEBINFO builds.\nCMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO:STRING=\n\n//Enable/Disable output of compile commands during generation.\nCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=\n\n//Value Computed by CMake.\nCMAKE_FIND_PACKAGE_REDIRECTS_DIR:STATIC=/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release/CMakeFiles/pkgRedirects\n\n//Install path prefix, prepended onto install directories.\nCMAKE_INSTALL_PREFIX:PATH=/usr/local\n\n//Path to a program.\nCMAKE_LINKER:FILEPATH=/usr/bin/ld\n\n//Path to a program.\nCMAKE_MAKE_PROGRAM:FILEPATH=/usr/bin/gmake\n\n//Flags used by the linker during the creation of modules during\n// all build types.\nCMAKE_MODULE_LINKER_FLAGS:STRING=\n\n//Flags used by the linker during the creation of modules during\n// DEBUG builds.\nCMAKE_MODULE_LINKER_FLAGS_DEBUG:STRING=\n\n//Flags used by the linker during the creation of modules during\n// MINSIZEREL builds.\nCMAKE_MODULE_LINKER_FLAGS_MINSIZEREL:STRING=\n\n//Flags used by the linker during the creation of modules during\n// RELEASE builds.\nCMAKE_MODULE_LINKER_FLAGS_RELEASE:STRING=\n\n//Flags used by the linker during the creation of modules during\n// RELWITHDEBINFO builds.\nCMAKE_MODULE_LINKER_FLAGS_RELWITHDEBINFO:STRING=\n\n//Path to a program.\nCMAKE_NM:FILEPATH=/usr/bin/nm\n\n//Path to a program.\nCMAKE_OBJCOPY:FILEPATH=/usr/bin/objcopy\n\n//Path to a program.\nCMAKE_OBJDUMP:FILEPATH=/usr/bin/objdump\n\n//Value Computed by CMake\nCMAKE_PROJECT_DESCRIPTION:STATIC=\n\n//Value Computed by CMake\nCMAKE_PROJECT_HOMEPAGE_URL:STATIC=\n\n//Value Computed by CMake\nCMAKE_PROJECT_NAME:STATIC=modern_algorithm_benchmark\n\n//Value Computed by CMake\nCMAKE_PROJECT_VERSION:STATIC=0.1.0\n\n//Value Computed by CMake\nCMAKE_PROJECT_VERSION_MAJOR:STATIC=0\n\n//Value Computed by CMake\nCMAKE_PROJECT_VERSION_MINOR:STATIC=1\n\n//Value Computed by CMake\nCMAKE_PROJECT_VERSION_PATCH:STATIC=0\n\n//Value Computed by CMake\nCMAKE_PROJECT_VERSION_TWEAK:STATIC=\n\n//Path to a program.\nCMAKE_RANLIB:FILEPATH=/usr/bin/ranlib\n\n//Path to a program.\nCMAKE_READELF:FILEPATH=/usr/bin/readelf\n\n//Flags used by the linker during the creation of shared libraries\n// during all build types.\nCMAKE_SHARED_LINKER_FLAGS:STRING=\n\n//Flags used by the linker during the creation of shared libraries\n// during DEBUG builds.\nCMAKE_SHARED_LINKER_FLAGS_DEBUG:STRING=\n\n//Flags used by the linker during the creation of shared libraries\n// during MINSIZEREL builds.\nCMAKE_SHARED_LINKER_FLAGS_MINSIZEREL:STRING=\n\n//Flags used by the linker during the creation of shared libraries\n// during RELEASE builds.\nCMAKE_SHARED_LINKER_FLAGS_RELEASE:STRING=\n\n//Flags used by the linker during the creation of shared libraries\n// during RELWITHDEBINFO builds.\nCMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO:STRING=\n\n//If set, runtime paths are not added when installing shared libraries,\n// but are added when building.\nCMAKE_SKIP_INSTALL_RPATH:BOOL=NO\n\n//If set, runtime paths are not added when using shared libraries.\nCMAKE_SKIP_RPATH:BOOL=NO\n\n//Flags used by the linker during the creation of static libraries\n// during all build types.\nCMAKE_STATIC_LINKER_FLAGS:STRING=\n\n//Flags used by the linker during the creation of static libraries\n// during DEBUG builds.\nCMAKE_STATIC_LINKER_FLAGS_DEBUG:STRING=\n\n//Flags used by the linker during the creation of static libraries\n// during MINSIZEREL builds.\nCMAKE_STATIC_LINKER_FLAGS_MINSIZEREL:STRING=\n\n//Flags used by the linker during the creation of static libraries\n// during RELEASE builds.\nCMAKE_STATIC_LINKER_FLAGS_RELEASE:STRING=\n\n//Flags used by the linker during the creation of static libraries\n// during RELWITHDEBINFO builds.\nCMAKE_STATIC_LINKER_FLAGS_RELWITHDEBINFO:STRING=\n\n//Path to a program.\nCMAKE_STRIP:FILEPATH=/usr/bin/strip\n\n//Path to a program.\nCMAKE_TAPI:FILEPATH=CMAKE_TAPI-NOTFOUND\n\n//If this value is on, makefiles will be generated without the\n// .SILENT directive, and all commands will be echoed to the console\n// during the make.  This is useful for debugging only. With Visual\n// Studio IDE projects all commands are done without /nologo.\nCMAKE_VERBOSE_MAKEFILE:BOOL=FALSE\n\n//Path to the coverage program that CTest uses for performing coverage\n// inspection\nCOVERAGE_COMMAND:FILEPATH=/usr/bin/gcov\n\n//Extra command line flags to pass to the coverage tool\nCOVERAGE_EXTRA_FLAGS:STRING=-l\n\n//How many times to retry timed-out CTest submissions.\nCTEST_SUBMIT_RETRY_COUNT:STRING=3\n\n//How long to wait between timed-out CTest submissions.\nCTEST_SUBMIT_RETRY_DELAY:STRING=5\n\n//Maximum time allowed before CTest will kill the test.\nDART_TESTING_TIMEOUT:STRING=1500\n\n//Build the separate OpenMP parallel sorting family\nMAB_ENABLE_OPENMP:BOOL=ON\n\n//Enable address and undefined-behavior sanitizers\nMAB_ENABLE_SANITIZERS:BOOL=OFF\n\n//Command to build the project\nMAKECOMMAND:STRING=/usr/bin/cmake --build . --config \"${CTEST_CONFIGURATION_TYPE}\"\n\n//Path to the memory checking command, used for memory error detection.\nMEMORYCHECK_COMMAND:FILEPATH=MEMORYCHECK_COMMAND-NOTFOUND\n\n//File that contains suppressions for the memory checker\nMEMORYCHECK_SUPPRESSIONS_FILE:FILEPATH=\n\n//CXX compiler flags for OpenMP parallelization\nOpenMP_CXX_FLAGS:STRING=-fopenmp\n\n//CXX compiler libraries for OpenMP parallelization\nOpenMP_CXX_LIB_NAMES:STRING=gomp;pthread\n\n//Path to the gomp library for OpenMP\nOpenMP_gomp_LIBRARY:FILEPATH=/usr/lib/gcc/x86_64-linux-gnu/13/libgomp.so\n\n//Path to the pthread library for OpenMP\nOpenMP_pthread_LIBRARY:FILEPATH=/usr/lib/x86_64-linux-gnu/libpthread.a\n\n//Name of the computer/site where compile is being run\nSITE:STRING=pop-os\n\n//Value Computed by CMake\nmodern_algorithm_benchmark_BINARY_DIR:STATIC=/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release\n\n//Value Computed by CMake\nmodern_algorithm_benchmark_IS_TOP_LEVEL:STATIC=ON\n\n//Value Computed by CMake\nmodern_algorithm_benchmark_SOURCE_DIR:STATIC=/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark\n\n\n########################\n# INTERNAL cache entries\n########################\n\n//ADVANCED property for variable: CMAKE_ADDR2LINE\nCMAKE_ADDR2LINE-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_AR\nCMAKE_AR-ADVANCED:INTERNAL=1\n//This is the directory where this CMakeCache.txt was created\nCMAKE_CACHEFILE_DIR:INTERNAL=/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release\n//Major version of cmake used to create the current loaded cache\nCMAKE_CACHE_MAJOR_VERSION:INTERNAL=3\n//Minor version of cmake used to create the current loaded cache\nCMAKE_CACHE_MINOR_VERSION:INTERNAL=28\n//Patch version of cmake used to create the current loaded cache\nCMAKE_CACHE_PATCH_VERSION:INTERNAL=3\n//ADVANCED property for variable: CMAKE_COLOR_MAKEFILE\nCMAKE_COLOR_MAKEFILE-ADVANCED:INTERNAL=1\n//Path to CMake executable.\nCMAKE_COMMAND:INTERNAL=/usr/bin/cmake\n//Path to cpack program executable.\nCMAKE_CPACK_COMMAND:INTERNAL=/usr/bin/cpack\n//ADVANCED property for variable: CMAKE_CTEST_COMMAND\nCMAKE_CTEST_COMMAND-ADVANCED:INTERNAL=1\n//Path to ctest program executable.\nCMAKE_CTEST_COMMAND:INTERNAL=/usr/bin/ctest\n//ADVANCED property for variable: CMAKE_CXX_COMPILER\nCMAKE_CXX_COMPILER-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_CXX_COMPILER_AR\nCMAKE_CXX_COMPILER_AR-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_CXX_COMPILER_RANLIB\nCMAKE_CXX_COMPILER_RANLIB-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_CXX_FLAGS\nCMAKE_CXX_FLAGS-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_CXX_FLAGS_DEBUG\nCMAKE_CXX_FLAGS_DEBUG-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_CXX_FLAGS_MINSIZEREL\nCMAKE_CXX_FLAGS_MINSIZEREL-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_CXX_FLAGS_RELEASE\nCMAKE_CXX_FLAGS_RELEASE-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_CXX_FLAGS_RELWITHDEBINFO\nCMAKE_CXX_FLAGS_RELWITHDEBINFO-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_DLLTOOL\nCMAKE_DLLTOOL-ADVANCED:INTERNAL=1\n//Executable file format\nCMAKE_EXECUTABLE_FORMAT:INTERNAL=ELF\n//ADVANCED property for variable: CMAKE_EXE_LINKER_FLAGS\nCMAKE_EXE_LINKER_FLAGS-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_EXE_LINKER_FLAGS_DEBUG\nCMAKE_EXE_LINKER_FLAGS_DEBUG-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_EXE_LINKER_FLAGS_MINSIZEREL\nCMAKE_EXE_LINKER_FLAGS_MINSIZEREL-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_EXE_LINKER_FLAGS_RELEASE\nCMAKE_EXE_LINKER_FLAGS_RELEASE-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO\nCMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_EXPORT_COMPILE_COMMANDS\nCMAKE_EXPORT_COMPILE_COMMANDS-ADVANCED:INTERNAL=1\n//Name of external makefile project generator.\nCMAKE_EXTRA_GENERATOR:INTERNAL=\n//Name of generator.\nCMAKE_GENERATOR:INTERNAL=Unix Makefiles\n//Generator instance identifier.\nCMAKE_GENERATOR_INSTANCE:INTERNAL=\n//Name of generator platform.\nCMAKE_GENERATOR_PLATFORM:INTERNAL=\n//Name of generator toolset.\nCMAKE_GENERATOR_TOOLSET:INTERNAL=\n//Test CMAKE_HAVE_LIBC_PTHREAD\nCMAKE_HAVE_LIBC_PTHREAD:INTERNAL=1\n//Source directory with the top level CMakeLists.txt file for this\n// project\nCMAKE_HOME_DIRECTORY:INTERNAL=/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark\n//Install .so files without execute permission.\nCMAKE_INSTALL_SO_NO_EXE:INTERNAL=1\n//ADVANCED property for variable: CMAKE_LINKER\nCMAKE_LINKER-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_MAKE_PROGRAM\nCMAKE_MAKE_PROGRAM-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_MODULE_LINKER_FLAGS\nCMAKE_MODULE_LINKER_FLAGS-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_MODULE_LINKER_FLAGS_DEBUG\nCMAKE_MODULE_LINKER_FLAGS_DEBUG-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_MODULE_LINKER_FLAGS_MINSIZEREL\nCMAKE_MODULE_LINKER_FLAGS_MINSIZEREL-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_MODULE_LINKER_FLAGS_RELEASE\nCMAKE_MODULE_LINKER_FLAGS_RELEASE-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_MODULE_LINKER_FLAGS_RELWITHDEBINFO\nCMAKE_MODULE_LINKER_FLAGS_RELWITHDEBINFO-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_NM\nCMAKE_NM-ADVANCED:INTERNAL=1\n//number of local generators\nCMAKE_NUMBER_OF_MAKEFILES:INTERNAL=1\n//ADVANCED property for variable: CMAKE_OBJCOPY\nCMAKE_OBJCOPY-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_OBJDUMP\nCMAKE_OBJDUMP-ADVANCED:INTERNAL=1\n//Platform information initialized\nCMAKE_PLATFORM_INFO_INITIALIZED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_RANLIB\nCMAKE_RANLIB-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_READELF\nCMAKE_READELF-ADVANCED:INTERNAL=1\n//Path to CMake installation.\nCMAKE_ROOT:INTERNAL=/usr/share/cmake-3.28\n//ADVANCED property for variable: CMAKE_SHARED_LINKER_FLAGS\nCMAKE_SHARED_LINKER_FLAGS-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_SHARED_LINKER_FLAGS_DEBUG\nCMAKE_SHARED_LINKER_FLAGS_DEBUG-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_SHARED_LINKER_FLAGS_MINSIZEREL\nCMAKE_SHARED_LINKER_FLAGS_MINSIZEREL-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_SHARED_LINKER_FLAGS_RELEASE\nCMAKE_SHARED_LINKER_FLAGS_RELEASE-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO\nCMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_SKIP_INSTALL_RPATH\nCMAKE_SKIP_INSTALL_RPATH-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_SKIP_RPATH\nCMAKE_SKIP_RPATH-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_STATIC_LINKER_FLAGS\nCMAKE_STATIC_LINKER_FLAGS-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_STATIC_LINKER_FLAGS_DEBUG\nCMAKE_STATIC_LINKER_FLAGS_DEBUG-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_STATIC_LINKER_FLAGS_MINSIZEREL\nCMAKE_STATIC_LINKER_FLAGS_MINSIZEREL-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_STATIC_LINKER_FLAGS_RELEASE\nCMAKE_STATIC_LINKER_FLAGS_RELEASE-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_STATIC_LINKER_FLAGS_RELWITHDEBINFO\nCMAKE_STATIC_LINKER_FLAGS_RELWITHDEBINFO-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_STRIP\nCMAKE_STRIP-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CMAKE_TAPI\nCMAKE_TAPI-ADVANCED:INTERNAL=1\n//uname command\nCMAKE_UNAME:INTERNAL=/usr/bin/uname\n//ADVANCED property for variable: CMAKE_VERBOSE_MAKEFILE\nCMAKE_VERBOSE_MAKEFILE-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: COVERAGE_COMMAND\nCOVERAGE_COMMAND-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: COVERAGE_EXTRA_FLAGS\nCOVERAGE_EXTRA_FLAGS-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CTEST_SUBMIT_RETRY_COUNT\nCTEST_SUBMIT_RETRY_COUNT-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: CTEST_SUBMIT_RETRY_DELAY\nCTEST_SUBMIT_RETRY_DELAY-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: DART_TESTING_TIMEOUT\nDART_TESTING_TIMEOUT-ADVANCED:INTERNAL=1\n//Details about finding OpenMP\nFIND_PACKAGE_MESSAGE_DETAILS_OpenMP:INTERNAL=[TRUE][cfound components: CXX ][v4.5()]\n//Details about finding OpenMP_CXX\nFIND_PACKAGE_MESSAGE_DETAILS_OpenMP_CXX:INTERNAL=[-fopenmp][/usr/lib/gcc/x86_64-linux-gnu/13/libgomp.so][/usr/lib/x86_64-linux-gnu/libpthread.a][v4.5()]\n//Details about finding Python3\nFIND_PACKAGE_MESSAGE_DETAILS_Python3:INTERNAL=[/usr/bin/python3][cfound components: Interpreter ][v3.12.3()]\n//Details about finding Threads\nFIND_PACKAGE_MESSAGE_DETAILS_Threads:INTERNAL=[TRUE][v()]\n//ADVANCED property for variable: MAKECOMMAND\nMAKECOMMAND-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: MEMORYCHECK_COMMAND\nMEMORYCHECK_COMMAND-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: MEMORYCHECK_SUPPRESSIONS_FILE\nMEMORYCHECK_SUPPRESSIONS_FILE-ADVANCED:INTERNAL=1\n//Result of TRY_COMPILE\nOpenMP_COMPILE_RESULT_CXX_fopenmp:INTERNAL=TRUE\n//ADVANCED property for variable: OpenMP_CXX_FLAGS\nOpenMP_CXX_FLAGS-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: OpenMP_CXX_LIB_NAMES\nOpenMP_CXX_LIB_NAMES-ADVANCED:INTERNAL=1\n//CXX compiler's OpenMP specification date\nOpenMP_CXX_SPEC_DATE:INTERNAL=201511\n//Result of TRY_COMPILE\nOpenMP_SPECTEST_CXX_:INTERNAL=TRUE\n//ADVANCED property for variable: OpenMP_gomp_LIBRARY\nOpenMP_gomp_LIBRARY-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: OpenMP_pthread_LIBRARY\nOpenMP_pthread_LIBRARY-ADVANCED:INTERNAL=1\n//ADVANCED property for variable: SITE\nSITE-ADVANCED:INTERNAL=1\n//linker supports push/pop state\n_CMAKE_LINKER_PUSHPOP_STATE_SUPPORTED:INTERNAL=TRUE\n//Compiler reason failure\n_Python3_Compiler_REASON_FAILURE:INTERNAL=\n//Development reason failure\n_Python3_Development_REASON_FAILURE:INTERNAL=\n//Path to a program.\n_Python3_EXECUTABLE:INTERNAL=/usr/bin/python3\n//Python3 Properties\n_Python3_INTERPRETER_PROPERTIES:INTERNAL=Python;3;12;3;64;32;;cpython-312-x86_64-linux-gnu;abi3;/usr/lib/python3.12;/usr/lib/python3.12;/usr/local/lib/python3.12/dist-packages;/usr/local/lib/python3.12/dist-packages\n_Python3_INTERPRETER_SIGNATURE:INTERNAL=4c8bfa8951e99fa32e4000a94f8c04a2\n//NumPy reason failure\n_Python3_NumPy_REASON_FAILURE:INTERNAL=\n\n",
  "compile_commands": [
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_core.dir/src/algorithms/baselines.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/baselines.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/baselines.cpp",
      "output": "CMakeFiles/mab_core.dir/src/algorithms/baselines.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_core.dir/src/datasets/generator.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/datasets/generator.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/datasets/generator.cpp",
      "output": "CMakeFiles/mab_core.dir/src/datasets/generator.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_core.dir/src/algorithms/quicksort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/quicksort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/quicksort.cpp",
      "output": "CMakeFiles/mab_core.dir/src/algorithms/quicksort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_core.dir/src/algorithms/sorting.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/sorting.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/sorting.cpp",
      "output": "CMakeFiles/mab_core.dir/src/algorithms/sorting.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_core.dir/src/algorithms/pdqsort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/pdqsort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/pdqsort.cpp",
      "output": "CMakeFiles/mab_core.dir/src/algorithms/pdqsort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_core.dir/src/algorithms/timsort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/timsort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/timsort.cpp",
      "output": "CMakeFiles/mab_core.dir/src/algorithms/timsort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_core.dir/src/algorithms/mergesort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/mergesort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/mergesort.cpp",
      "output": "CMakeFiles/mab_core.dir/src/algorithms/mergesort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_core.dir/src/algorithms/radixsort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/radixsort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/radixsort.cpp",
      "output": "CMakeFiles/mab_core.dir/src/algorithms/radixsort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/algorithm_benchmark.dir/src/main.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/main.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/main.cpp",
      "output": "CMakeFiles/algorithm_benchmark.dir/src/main.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_metrics.dir/src/benchmark/comparisons.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/comparisons.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/comparisons.cpp",
      "output": "CMakeFiles/mab_metrics.dir/src/benchmark/comparisons.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_metrics.dir/src/benchmark/memory.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/memory.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/memory.cpp",
      "output": "CMakeFiles/mab_metrics.dir/src/benchmark/memory.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/pdqsort -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/third_party/timsort/include -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_metrics.dir/src/benchmark/memory_json.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/memory_json.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/memory_json.cpp",
      "output": "CMakeFiles/mab_metrics.dir/src/benchmark/memory_json.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/sort_metrics.dir/src/benchmark/metrics_main.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/metrics_main.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/metrics_main.cpp",
      "output": "CMakeFiles/sort_metrics.dir/src/benchmark/metrics_main.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_timing.dir/src/benchmark/timing.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/timing.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/timing.cpp",
      "output": "CMakeFiles/mab_timing.dir/src/benchmark/timing.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_timing.dir/src/benchmark/output.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/output.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/output.cpp",
      "output": "CMakeFiles/mab_timing.dir/src/benchmark/output.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release/generated/Release -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/sort_benchmark.dir/src/benchmark/timing_main.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/timing_main.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/timing_main.cpp",
      "output": "CMakeFiles/sort_benchmark.dir/src/benchmark/timing_main.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_search.dir/src/algorithms/searching.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/searching.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/searching.cpp",
      "output": "CMakeFiles/mab_search.dir/src/algorithms/searching.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_search_metrics.dir/src/benchmark/search_comparisons.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/search_comparisons.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/search_comparisons.cpp",
      "output": "CMakeFiles/mab_search_metrics.dir/src/benchmark/search_comparisons.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_search_timing.dir/src/benchmark/search_timing.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/search_timing.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/search_timing.cpp",
      "output": "CMakeFiles/mab_search_timing.dir/src/benchmark/search_timing.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release/generated/Release -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/search_benchmark.dir/src/benchmark/search_main.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/search_main.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/search_main.cpp",
      "output": "CMakeFiles/search_benchmark.dir/src/benchmark/search_main.cpp.o"
    },
    {
      "command": "/usr/bin/c++ -DMAB_SEARCH_COUNTS=1 -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release/generated/Release -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/search_counts.dir/src/benchmark/search_main.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/search_main.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/search_main.cpp",
      "output": "CMakeFiles/search_counts.dir/src/benchmark/search_main.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_structures.dir/src/structures/skip_list.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/structures/skip_list.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/structures/skip_list.cpp",
      "output": "CMakeFiles/mab_structures.dir/src/structures/skip_list.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_structures.dir/src/structures/btree.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/structures/btree.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/structures/btree.cpp",
      "output": "CMakeFiles/mab_structures.dir/src/structures/btree.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_structures.dir/src/structures/registry.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/structures/registry.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/structures/registry.cpp",
      "output": "CMakeFiles/mab_structures.dir/src/structures/registry.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/mab_structure_timing.dir/src/benchmark/structure_timing.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/structure_timing.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/structure_timing.cpp",
      "output": "CMakeFiles/mab_structure_timing.dir/src/benchmark/structure_timing.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release/generated/Release -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/structure_benchmark.dir/src/benchmark/structure_main.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/structure_main.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/structure_main.cpp",
      "output": "CMakeFiles/structure_benchmark.dir/src/benchmark/structure_main.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_structures.dir/tests/test_structures.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_structures.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_structures.cpp",
      "output": "CMakeFiles/test_structures.dir/tests/test_structures.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_structure_timing.dir/tests/test_structure_timing.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_structure_timing.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_structure_timing.cpp",
      "output": "CMakeFiles/test_structure_timing.dir/tests/test_structure_timing.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_searching.dir/tests/test_searching.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_searching.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_searching.cpp",
      "output": "CMakeFiles/test_searching.dir/tests/test_searching.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_search_timing.dir/tests/test_search_timing.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_search_timing.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_search_timing.cpp",
      "output": "CMakeFiles/test_search_timing.dir/tests/test_search_timing.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_baselines.dir/tests/test_baselines.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_baselines.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_baselines.cpp",
      "output": "CMakeFiles/test_baselines.dir/tests/test_baselines.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_datasets.dir/tests/test_datasets.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_datasets.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_datasets.cpp",
      "output": "CMakeFiles/test_datasets.dir/tests/test_datasets.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_quicksort.dir/tests/test_quicksort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_quicksort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_quicksort.cpp",
      "output": "CMakeFiles/test_quicksort.dir/tests/test_quicksort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_pdqsort.dir/tests/test_pdqsort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_pdqsort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_pdqsort.cpp",
      "output": "CMakeFiles/test_pdqsort.dir/tests/test_pdqsort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_timsort.dir/tests/test_timsort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_timsort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_timsort.cpp",
      "output": "CMakeFiles/test_timsort.dir/tests/test_timsort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_mergesort.dir/tests/test_mergesort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_mergesort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_mergesort.cpp",
      "output": "CMakeFiles/test_mergesort.dir/tests/test_mergesort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_radixsort.dir/tests/test_radixsort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_radixsort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_radixsort.cpp",
      "output": "CMakeFiles/test_radixsort.dir/tests/test_radixsort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_comparisons.dir/tests/test_comparisons.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_comparisons.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_comparisons.cpp",
      "output": "CMakeFiles/test_comparisons.dir/tests/test_comparisons.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_memory.dir/tests/test_memory.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_memory.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_memory.cpp",
      "output": "CMakeFiles/test_memory.dir/tests/test_memory.cpp.o"
    },
    {
      "command": "/usr/bin/c++ -DMAB_FORCE_UNSUPPORTED_MEMORY=1 -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_memory_unsupported.dir/tests/test_memory.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_memory.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_memory.cpp",
      "output": "CMakeFiles/test_memory_unsupported.dir/tests/test_memory.cpp.o"
    },
    {
      "command": "/usr/bin/c++ -DMAB_FORCE_UNSUPPORTED_MEMORY=1 -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_memory_unsupported.dir/src/benchmark/memory.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/memory.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/memory.cpp",
      "output": "CMakeFiles/test_memory_unsupported.dir/src/benchmark/memory.cpp.o"
    },
    {
      "command": "/usr/bin/c++ -DMAB_FORCE_UNSUPPORTED_MEMORY=1 -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_memory_unsupported.dir/src/benchmark/memory_json.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/memory_json.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/memory_json.cpp",
      "output": "CMakeFiles/test_memory_unsupported.dir/src/benchmark/memory_json.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -o CMakeFiles/test_timing.dir/tests/test_timing.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_timing.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_timing.cpp",
      "output": "CMakeFiles/test_timing.dir/tests/test_timing.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -fopenmp -o CMakeFiles/mab_parallel.dir/src/algorithms/parallel_mergesort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/parallel_mergesort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/algorithms/parallel_mergesort.cpp",
      "output": "CMakeFiles/mab_parallel.dir/src/algorithms/parallel_mergesort.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -fopenmp -o CMakeFiles/mab_parallel_timing.dir/src/benchmark/parallel_timing.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/parallel_timing.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/parallel_timing.cpp",
      "output": "CMakeFiles/mab_parallel_timing.dir/src/benchmark/parallel_timing.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release/generated/Release -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -fopenmp -o CMakeFiles/parallel_sort_benchmark.dir/src/benchmark/parallel_main.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/parallel_main.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/src/benchmark/parallel_main.cpp",
      "output": "CMakeFiles/parallel_sort_benchmark.dir/src/benchmark/parallel_main.cpp.o"
    },
    {
      "command": "/usr/bin/c++  -I/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/include -O3 -DNDEBUG -Wall -Wextra -Wpedantic -fopenmp -o CMakeFiles/test_parallel_mergesort.dir/tests/test_parallel_mergesort.cpp.o -c /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_parallel_mergesort.cpp",
      "directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release",
      "file": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/tests/test_parallel_mergesort.cpp",
      "output": "CMakeFiles/test_parallel_mergesort.dir/tests/test_parallel_mergesort.cpp.o"
    }
  ],
  "compiler": {
    "command": [
      "/usr/bin/c++",
      "--version"
    ],
    "returncode": 0,
    "stderr": "",
    "stdout": "c++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0\nCopyright (C) 2023 Free Software Foundation, Inc.\nThis is free software; see the source for copying conditions.  There is NO\nwarranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n\n"
  },
  "cpu_probe": {
    "command": [
      "lscpu"
    ],
    "returncode": 0,
    "stderr": "",
    "stdout": "Architecture:                            x86_64\nCPU op-mode(s):                          32-bit, 64-bit\nAddress sizes:                           39 bits physical, 48 bits virtual\nByte Order:                              Little Endian\nCPU(s):                                  12\nOn-line CPU(s) list:                     0-11\nVendor ID:                               GenuineIntel\nModel name:                              11th Gen Intel(R) Core(TM) i5-11400H @ 2.70GHz\nCPU family:                              6\nModel:                                   141\nThread(s) per core:                      2\nCore(s) per socket:                      6\nSocket(s):                               1\nStepping:                                1\nCPU(s) scaling MHz:                      77%\nCPU max MHz:                             4500.0000\nCPU min MHz:                             800.0000\nBogoMIPS:                                5376.00\nFlags:                                   fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf tsc_known_freq pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb cat_l2 cdp_l2 ssbd ibrs ibpb stibp ibrs_enhanced tpr_shadow flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid rdt_a avx512f avx512dq rdseed adx smap avx512ifma clflushopt clwb intel_pt avx512cd sha_ni avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves split_lock_detect user_shstk dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp hwp_pkg_req vnmi avx512vbmi umip pku ospke avx512_vbmi2 gfni vaes vpclmulqdq avx512_vnni avx512_bitalg avx512_vpopcntdq rdpid movdiri movdir64b fsrm avx512_vp2intersect md_clear ibt flush_l1d arch_capabilities\nVirtualization:                          VT-x\nL1d cache:                               288 KiB (6 instances)\nL1i cache:                               192 KiB (6 instances)\nL2 cache:                                7.5 MiB (6 instances)\nL3 cache:                                12 MiB (1 instance)\nNUMA node(s):                            1\nNUMA node0 CPU(s):                       0-11\nVulnerability Gather data sampling:      Vulnerable\nVulnerability Ghostwrite:                Not affected\nVulnerability Indirect target selection: Mitigation; Aligned branch/return thunks\nVulnerability Itlb multihit:             Not affected\nVulnerability L1tf:                      Not affected\nVulnerability Mds:                       Not affected\nVulnerability Meltdown:                  Not affected\nVulnerability Mmio stale data:           Not affected\nVulnerability Old microcode:             Not affected\nVulnerability Reg file data sampling:    Not affected\nVulnerability Retbleed:                  Not affected\nVulnerability Spec rstack overflow:      Not affected\nVulnerability Spec store bypass:         Mitigation; Speculative Store Bypass disabled via prctl\nVulnerability Spectre v1:                Mitigation; usercopy/swapgs barriers and __user pointer sanitization\nVulnerability Spectre v2:                Mitigation; Enhanced / Automatic IBRS; IBPB conditional; PBRSB-eIBRS SW sequence; BHI SW loop, KVM SW loop\nVulnerability Srbds:                     Not affected\nVulnerability Tsa:                       Not affected\nVulnerability Tsx async abort:           Not affected\nVulnerability Vmscape:                   Not affected\n"
  },
  "cpu_reported_by_python": "x86_64",
  "executable_sha256": "b5a990e58a51e453976980a0c6701dd21d1fae8447db922a48d9416199176a9d",
  "git_status": {
    "command": [
      "git",
      "status",
      "--short"
    ],
    "returncode": 128,
    "stderr": "fatal: not a git repository (or any of the parent directories): .git\n",
    "stdout": ""
  },
  "gpu_status": "not probed; no GPU experiment attempted",
  "invocation": "scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z_retry1 --processed results/processed/openmp_scaling_20261009T200852928292Z_retry1 --figures results/figures/openmp_scaling_20261009T200852928292Z_retry1",
  "linux_cgroup": "0::/user.slice/user-1000.slice/user@1000.service/app.slice/cosmic-files-applet.scope\n",
  "linux_meminfo": "MemTotal:       16089028 kB\nMemFree:         3916300 kB\nMemAvailable:    6576264 kB\nBuffers:          201532 kB\nCached:          4188828 kB\nSwapCached:         4180 kB\nActive:          5382128 kB\nInactive:        4068736 kB\nActive(anon):    4498276 kB\nInactive(anon):  1555888 kB\nActive(file):     883852 kB\nInactive(file):  2512848 kB\nUnevictable:      261344 kB\nMlocked:            7980 kB\nSwapTotal:      42675696 kB\nSwapFree:       37963996 kB\nZswap:                 0 kB\nZswapped:              0 kB\nDirty:             13580 kB\nWriteback:             0 kB\nAnonPages:       5319544 kB\nMapped:          1419324 kB\nShmem:            987796 kB\nKReclaimable:     520128 kB\nSlab:             849740 kB\nSReclaimable:     520128 kB\nSUnreclaim:       329612 kB\nKernelStack:       45168 kB\nPageTables:       115736 kB\nSecPageTables:      7748 kB\nNFS_Unstable:          0 kB\nBounce:                0 kB\nWritebackTmp:          0 kB\nCommitLimit:    50720208 kB\nCommitted_AS:   48467396 kB\nVmallocTotal:   34359738367 kB\nVmallocUsed:      216076 kB\nVmallocChunk:          0 kB\nPercpu:            14160 kB\nHardwareCorrupted:     0 kB\nAnonHugePages:     24576 kB\nShmemHugePages:   221184 kB\nShmemPmdMapped:        0 kB\nFileHugePages:     47104 kB\nFilePmdMapped:         0 kB\nCmaTotal:              0 kB\nCmaFree:               0 kB\nUnaccepted:            0 kB\nBalloon:               0 kB\nHugePages_Total:       0\nHugePages_Free:        0\nHugePages_Rsvd:        0\nHugePages_Surp:        0\nHugepagesize:       2048 kB\nHugetlb:               0 kB\nDirectMap4k:      323992 kB\nDirectMap2M:     3586048 kB\nDirectMap1G:    13631488 kB\n",
  "logical_cpu_count": 12,
  "machine": "x86_64",
  "matplotlib_version": "3.11.0",
  "omp_environment": {
    "OMP_DYNAMIC": "FALSE",
    "OMP_MAX_ACTIVE_LEVELS": "1",
    "OMP_THREAD_LIMIT": "8",
    "OMP_WAIT_POLICY": "PASSIVE"
  },
  "os": "Linux-6.18.7-76061807-generic-x86_64-with-glibc2.39",
  "python": "3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]",
  "record_kind": "parallel_scaling_environment",
  "registry_probe": {
    "command": [
      "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release/parallel_sort_benchmark",
      "--list-sorts"
    ],
    "exit_code": 0,
    "finished_utc": "2026-10-09T20:37:49.436365+00:00",
    "started_utc": "2026-10-09T20:37:49.434989+00:00",
    "status": "successful",
    "stderr": "",
    "stdout": "merge_sort\nparallel_merge_sort\n",
    "wall_seconds": 0.0013694049994228408
  },
  "runtime_library_sha256": {
    "/lib/x86_64-linux-gnu/libc.so.6": "8db37cf3f2169f59a0f07ef1fea308c35656668c64c8ff294e1860f4121eb161",
    "/lib/x86_64-linux-gnu/libgcc_s.so.1": "d93224d2b0dab4247598be683adca02f5cf00586f99c187579cd7e92058fb7cb",
    "/lib/x86_64-linux-gnu/libgomp.so.1": "135f3c8f006d2fe5e68e51281c7974cb991a03de3bfb3593d68d174dfcf854d1",
    "/lib/x86_64-linux-gnu/libm.so.6": "e9c4b28d340e415b8137480ec442662f981e1399386c5931dae0e886e3639e91",
    "/lib/x86_64-linux-gnu/libstdc++.so.6": "1fd75fe70354a416d75aef22bcae68c47bd25d20e2d0568c30b1a9838cf62f11"
  },
  "runtime_linkage": {
    "command": [
      "ldd",
      "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/build/release/parallel_sort_benchmark"
    ],
    "exit_code": 0,
    "finished_utc": "2026-10-09T20:37:49.455928+00:00",
    "started_utc": "2026-10-09T20:37:49.451671+00:00",
    "status": "successful",
    "stderr": "",
    "stdout": "\tlinux-vdso.so.1 (0x00007caf96d73000)\n\tlibgomp.so.1 => /lib/x86_64-linux-gnu/libgomp.so.1 (0x00007caf96ce7000)\n\tlibstdc++.so.6 => /lib/x86_64-linux-gnu/libstdc++.so.6 (0x00007caf96a00000)\n\tlibgcc_s.so.1 => /lib/x86_64-linux-gnu/libgcc_s.so.1 (0x00007caf96cb9000)\n\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007caf96600000)\n\tlibm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007caf96917000)\n\t/lib64/ld-linux-x86-64.so.2 (0x00007caf96d75000)\n",
    "wall_seconds": 0.004255252999428194
  },
  "schema_version": 1,
  "tools_sha256": {
    "analyze_experiment.py": "ecf00ac8c50de87b4f024679a9fa4dab076350603bd94c35799f176e2612da8f",
    "analyze_parallel_results.py": "b3a5a4238767359ca5abdb452b2cdfd0e8c9387d92950f1d76dca46b9f857e88",
    "analyze_results.py": "742d4eeaff4234ad7572f942dd5f510d45e8b14025e416a960da5933dfe54f24",
    "analyze_search_results.py": "d6713c3dcb7318421f84425bc8d56ab71adc5cce3f0b00f323374e85a99b50ef",
    "analyze_structure_results.py": "9e449fe4862b4088088b032c6da749efbc182335d670f3138c5a648abc2dcceb",
    "assess_experiment.py": "bb68354fb7f6965cf67e6f5503e23ec2af567e797d06c68c1f19816865c62ccf",
    "capture_environment.py": "1d49b0ac22c91ddf8e904232d41525a482d37f2c812c28da012449625e645210",
    "experiment_model.py": "8848f50284dc86dbe77bf6f65025ba68bbf14ccbe6c4820650b0588506060c75",
    "plot_results.py": "a2f3a5063410f6be318806357a08cd4e5f3d71fc2a856306a9f7432536128f03",
    "run_experiments.py": "5aef113b16654adb685a750237cd9e97ecb5a71de02a7006a987120bcb58033f",
    "run_matrix.py": "1e19af5ed3ef73d05591ef14b31e3f456b763e747535b0440b30fbbc24d6988d",
    "run_parallel_matrix.py": "a96b7f35e7e0fae872c65e1e0ce6d54414cac6bf1be6c2a351c4d03c3a3db118",
    "run_search_matrix.py": "fd2070a4ebd83f922d108a6a69476a40f69313f9cfd3dbcb9bea9db2edb08801",
    "run_structure_matrix.py": "6f0849876d99d9e2b8faa125b2942161d5cb2866ea0587c5fbe32b7b220a1806"
  },
  "working_directory": "/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark",
  "workload": null,
  "workload_note": "Correctness baseline only; no benchmark workload executed."
}
```

## Limitations and reproduction
One shared Linux session, unpinned frequency/affinity/thermal/background load; fixed configuration order and odd-repetition cyclic imbalance. Serial parent merges limit parallelism. Actual team size is not a count of task-executing workers. No race-freedom, significance or universal superiority claim. No isolated memory/counting or CUDA/100M experiment.

Full ns statistics, failures and every raw row remain in summary.json/observations.jsonl. Plot stack/points/source hashes are in plot_manifest.json. Regenerate to new paths:
`python3 scripts/analyze_parallel_results.py /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/openmp_scaling_20261009T200852928292Z_retry1 --output NEW_PROCESSED --figures NEW_FIGURES`
