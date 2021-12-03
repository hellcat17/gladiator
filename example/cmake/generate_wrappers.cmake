include(cmake/gladiator_requirements.cmake)

if(EXAMPLE_GENERATE_SCOPED_LOADER)
	set(GLADIATOR_CONFIG ${CMAKE_SOURCE_DIR}/cmake/gladiator-scoped.yaml)
else()
	set(GLADIATOR_CONFIG ${CMAKE_SOURCE_DIR}/cmake/gladiator-global.yaml)
endif()

set(GLADIATOR_OUTPUT ${CMAKE_BINARY_DIR}/opengl.hxx)
add_custom_command(
	OUTPUT ${GLADIATOR_OUTPUT}
	COMMAND Python3::Interpreter -m gladiator --config-file ${GLADIATOR_CONFIG} --output ${GLADIATOR_OUTPUT}
	WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/cmake
	DEPENDS ${GLADIATOR_CONFIG}
)
