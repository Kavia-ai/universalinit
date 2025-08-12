cmake_minimum_required(VERSION 3.16)
project(Welcome VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find required Qt6 components
find_package(Qt6 REQUIRED COMPONENTS Core Widgets)

# Enable Qt MOC
set(CMAKE_AUTOMOC ON)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Source files
set(SOURCES
    src/welcome.cpp
)

# Header files
set(HEADERS
    include/welcome.h
)

# Create executable
add_executable(welcome ${SOURCES} ${HEADERS})

# Link Qt6 libraries
target_link_libraries(welcome Qt6::Core Qt6::Widgets)

# Set output directory
set_target_properties(welcome PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

# Enable testing
enable_testing()

# Add basic test
add_test(NAME WelcomeTest COMMAND welcome)