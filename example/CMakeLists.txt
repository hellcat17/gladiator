cmake_minimum_required(VERSION 3.16)

project(example VERSION 1.0.0)

include(cmake/CPM.cmake)
CPMAddPackage(GITHUB_REPOSITORY libsdl-org/SDL GIT_TAG release-2.0.16)
CPMAddPackage(GITHUB_REPOSITORY TartanLlama/expected VERSION 1.0.0)

include(cmake/generate_wrappers.cmake)

if(MSVC)
	set(ADDITIONAL_LINK_OPTIONS /subsystem:console)
	set(ADDITIONAL_COMPILE_OPTIONS /WX)
elseif(NOT WIN32)
	set(ADDITIONAL_COMPILE_OPTIONS -Wall -Wextra -pedantic -Werror)
endif()

if(EXAMPLE_GENERATE_SCOPED_LOADER)
	set(ADDITIONAL_COMPILE_OPTIONS ${ADDITIONAL_COMPILE_OPTIONS} -DUSE_SCOPED_LOADER)
endif()

add_executable(${CMAKE_PROJECT_NAME} src/main.cxx ${GLADIATOR_OUTPUT})
target_compile_options(${CMAKE_PROJECT_NAME} PRIVATE ${ADDITIONAL_COMPILE_OPTIONS})
target_link_options(${CMAKE_PROJECT_NAME} PRIVATE ${ADDITIONAL_LINK_OPTIONS})
target_compile_features(${CMAKE_PROJECT_NAME} PRIVATE cxx_std_14)
target_include_directories(${CMAKE_PROJECT_NAME}
	PRIVATE
		${expected_SOURCE_DIR}/include
		${CMAKE_CURRENT_SOURCE_DIR}/src
		${CMAKE_CURRENT_BINARY_DIR}
)
target_link_libraries(${CMAKE_PROJECT_NAME} SDL2::SDL2 SDL2::SDL2main)
