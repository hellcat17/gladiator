# gladiator

Generate type-safe, zero-overhead OpenGL wrappers for C++


## Why

OpenGL is a C API. This allows widespread use, but unfortunately there are no
strong enumerations that ensure correct and convenient use. Personal anecdote:
AMD had a driver bug that allowed the `internalformat` parameter of `glTexImage2D`
to be `GL_RGBA`. Of course the code did not function with other graphics card vendors.
Having strong enumerations would have prevented this misuse.

## How

Luckily for us, Khronos provides a machine-readable OpenGL specification file
that groups related enums into a named higher-level type. These higher-level
types are referenced in the commands.

All gladiator does is define all higher-level types as strong C++11 enums
(plus bitmask operators for bitfields) and create tiny wrappers taking parameters
of these types. The wrappers execute the underlying OpenGL command, safely
casting the parameter types where required.

## Basic usage

1. Download the latest machine-readable OpenGL specification file from https://github.com/KhronosGroup/OpenGL-Registry/blob/main/xml/gl.xml.
2. Install gladiator via pip:
    ```
    $ python -m pip install --user gladiator-gen
    ```
2. Specify the API and version within the spec file for which to generate wrappers:
    ```
    $ python -m gladiator --spec-file <file> --api <gl|gles1|gles2|glsc2> --version <version>
    ```
3. For example, to generate for OpenGL ES 3.0:
    ```
    $ python -m gladiator --spec-file <file> --api gles2 --version 3.0
    ```
4. For example, to generate code that is compatible with both OpenGL ES 3.0 and OpenGL 4.3:
    ```
    $ python -m gladiator --spec-file <file> --api gles2 gl --version 3.0 4.3
    ```
    WARNING: be very careful with the intersection feature, as it does not
    always make sense. Use it with modern OpenGL(ES) only.

5. Most libraries that manage windows, input and OpenGL contexts abstract the
   platform-specific `GetProcAddress` function for retrieving OpenGL function
   pointers. Gladiator needs this to initialize the command storage.
   Very simplified example via SDL:
    ```c++
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 4);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
    SDL_GL_CreateContext(window);

    if (!gl::load_gl_43_functions(SDL_GL_GetProcAddress)) {
      std::cout << "failed to load OpenGL functions" << std::endl;
    }
    ```

## Advanced usage

### Scope of wrappers and OpenGL command storage

Gladiator supports both global wrappers and wrappers as class methods. Global wrappers
are more flexible but objects guarantee that the required OpenGL function pointers are
loaded where ever it is used. Use the `--scope object` option to switch to wrapper methods.

### Style options

This tool can split enum or command names into words and transform them to well-known case
styles, such as snake_case or camelCase to yield the code style you prefer or that is in
accordance with the language you generate code for. By default, everything is taken
as-is from the OpenGL specification file. Related options:
- `--enum-case`
- `--function-case`
- `--enum-value-case`

#### Omit GL prefix

If desired, one can remove the `gl` prefix from commands and the `GL_` prefix from enums with `--omit-prefix`.

### RAII-style resource wrappers

It is not only easy to forget but also tedious to call `glDelete*` after no longer
requiring OpenGL object names. Gladiator allows you to generate RAII-style wrappers
that create objects and delete them when they go out of scope with `--generate-resource-wrappers`.

```c++
const glw::texture tex{};
gl::bind_texture(gl::texture_target::texture_2d, tex);

const glw::texture_list texture_maps{4};
for (const auto tex : texture_maps) {
  gl::bind_texture(gl::texture_target::texture_2d, tex);
}

const glw::shader fragment_shader{gl::shader_type::fragment_shader};
// ...
```

### Custom templates

It is possible to override templates in the code generation pipeline. Refer
to the CLI help for option `--template-override-dir` to find out which.

The data gladiator passes to its templates is almost completely language-agnostic,
therefore it is possible to generate code for a language other than C++. The only
thing specific to C and C++ are types (e.g. command parameters) taken from the OpenGL
specification itself. Those types (and additional modifiers) need to be mapped manually.

### Example and CMake integration

A complete example can be found in the `example` directory. CMake integration boils down to this:

```cmake
find_package(Python3 COMPONENTS Interpreter REQUIRED)
execute_process(
  COMMAND ${Python3_EXECUTABLE} -c "import gladiator"
  RESULT_VARIABLE EXIT_CODE
)
if (NOT "${EXIT_CODE}" STREQUAL 0)
  message(FATAL_ERROR "The package 'gladiator' is not installed.")
endif()

set(CONFIG_DIR ${CMAKE_SOURCE_DIR}/whatever)
set(GLADIATOR_CONFIG ${CONFIG_DIR}/config.yaml)
set(GLADIATOR_OUTPUT ${CMAKE_BINARY_DIR}/opengl.hxx)
add_custom_command(
  OUTPUT ${GLADIATOR_OUTPUT}
  COMMAND Python3::Interpreter -m gladiator --config-file ${GLADIATOR_CONFIG} --output ${GLADIATOR_OUTPUT}
  DEPENDS ${GLADIATOR_CONFIG}
)

add_executable(${CMAKE_PROJECT_NAME} main.cxx ${GLADIATOR_OUTPUT})
```
