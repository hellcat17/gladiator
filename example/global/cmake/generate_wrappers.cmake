include(cmake/gladiator_requirements.cmake)

set(GLADIATOR_CONFIG ${CMAKE_SOURCE_DIR}/cmake/gladiator.yaml)
set(GLADIATOR_OUTPUT ${CMAKE_BINARY_DIR}/opengl.hxx)
add_custom_command(
	OUTPUT ${GLADIATOR_OUTPUT}
	COMMAND Python::Interpreter -m gladiator --config-file ${GLADIATOR_CONFIG} --output ${GLADIATOR_OUTPUT}
	WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/cmake
	DEPENDS ${GLADIATOR_CONFIG}
)
