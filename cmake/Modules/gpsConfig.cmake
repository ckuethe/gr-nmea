INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_GPS gps)

FIND_PATH(
    GPS_INCLUDE_DIRS
    NAMES gps/api.h
    HINTS $ENV{GPS_DIR}/include
        ${PC_GPS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GPS_LIBRARIES
    NAMES gnuradio-gps
    HINTS $ENV{GPS_DIR}/lib
        ${PC_GPS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GPS DEFAULT_MSG GPS_LIBRARIES GPS_INCLUDE_DIRS)
MARK_AS_ADVANCED(GPS_LIBRARIES GPS_INCLUDE_DIRS)

