find_package(Python COMPONENTS Interpreter REQUIRED)
execute_process(
	COMMAND ${Python_EXECUTABLE} -c "import gladiator"
	RESULT_VARIABLE EXIT_CODE
)
if (NOT "${EXIT_CODE}" STREQUAL 0)
	message(FATAL_ERROR "The package 'gladiator' is not installed.")
endif()
