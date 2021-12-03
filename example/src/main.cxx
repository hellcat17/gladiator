#include <array>
#include <iostream>
#include <string>
#include <tuple>

#include <SDL.h>
#include <tl/expected.hpp>

#include "opengl.hxx"

constexpr auto window_width = 600;
constexpr auto window_height = 400;

constexpr auto clear_r = 0x64 / 255.f;
constexpr auto clear_g = 0x95 / 255.f;
constexpr auto clear_b = 0xed / 255.f;

auto initialize_sdl() -> tl::expected<void, std::string>
{
	if (SDL_Init(SDL_INIT_VIDEO) != 0) {
		return tl::make_unexpected(SDL_GetError());
	}
	return {};
}

auto quit_sdl(int code) -> tl::expected<int, std::string> {
	SDL_Quit();
	return code;
}

auto load_gl() {
	#ifdef USE_SCOPED_LOADER
	return gl::functions{SDL_GL_GetProcAddress};
	#else
	return gl::load_functions(SDL_GL_GetProcAddress);
	#endif
}

bool test_resource_wrappers() {
	#ifdef USE_SCOPED_LOADER
	return true;
	#else
	const glw::texture_list texture_maps{4};
	for (const auto tex : texture_maps) {
		gl::bind_texture(gl::texture_target::texture_2d, tex);
		if (gl::get_error() != gl::error_code::no_error) {
			return false;
		}
		if (gl::is_texture(tex) == gl::boolean::false_) {
			return false;
		}
	}

	const glw::buffer vertex_buffer{};
	gl::bind_buffer(gl::buffer_target::array_buffer, vertex_buffer);
	if (gl::get_error() != gl::error_code::no_error) {
		return false;
	}
	if (gl::is_buffer(vertex_buffer) == gl::boolean::false_) {
		return false;
	}

	const glw::shader fragment_shader{gl::shader_type::fragment_shader};
	if (gl::get_error() != gl::error_code::no_error) {
		return false;
	}
	if (gl::is_shader(fragment_shader) == gl::boolean::false_) {
		return false;
	}

	return true;
	#endif
}

auto run_example(SDL_Window* window) -> tl::expected<int, std::string> {
	const auto gl = load_gl();
	if (!gl) {
		return tl::make_unexpected("failed to load OpenGL functions");
	}

	if (!test_resource_wrappers()) {
		return tl::make_unexpected("OpenGL error while testing resource wrappers");
	}

	#ifdef USE_SCOPED_LOADER
	gl.viewport(0, 0, window_width, window_height);
	#else
	gl::viewport(0, 0, window_width, window_height);
	#endif

	while (true) {
		SDL_Event event;
		while (SDL_PollEvent(&event) != 0) {
			if (event.type == SDL_QUIT) {
				return 0;
			}
		}

		#ifdef USE_SCOPED_LOADER
		gl.clear_color(clear_r, clear_g, clear_b, 1);
		gl.clear(gl::clear_buffer_mask::color_buffer_bit | gl::clear_buffer_mask::depth_buffer_bit);
		#else
		gl::clear_color(clear_r, clear_g, clear_b, 1);
		gl::clear(gl::clear_buffer_mask::color_buffer_bit | gl::clear_buffer_mask::depth_buffer_bit);
		#endif

		SDL_GL_SwapWindow(window);
	}
}

constexpr std::array<std::pair<SDL_GLattr, int>, 10> window_settings = {{
		{SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE},
		{SDL_GL_CONTEXT_MAJOR_VERSION, 3},
		{SDL_GL_CONTEXT_MINOR_VERSION, 3},
#ifndef _NDEBUG
		{SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_DEBUG_FLAG},
#endif
}};

auto set_attributes() -> tl::expected<void, std::string> {
	for (const auto& attrib : window_settings) {
		if (SDL_GL_SetAttribute(attrib.first, attrib.second) == -1) {
			return tl::make_unexpected(SDL_GetError());
		}
	}
	return {};
}

auto make_surface() -> tl::expected<SDL_Window*, std::string>
{
	auto window = SDL_CreateWindow("example",
			SDL_WINDOWPOS_CENTERED_DISPLAY(0),
			SDL_WINDOWPOS_CENTERED_DISPLAY(0),
			window_width, window_height, SDL_WINDOW_OPENGL);

	if (window == nullptr) {
		return tl::make_unexpected(SDL_GetError());
	}

	auto context = SDL_GL_CreateContext(window);
	if (context == nullptr) {
		SDL_DestroyWindow(window);
		return tl::make_unexpected(SDL_GetError());
	}

	return window;
}

void show_error(const std::string& message) {
	std::cerr << "ERROR: " << message << std::endl;
}

int main(int, char**)
{
	return initialize_sdl()
			.and_then(set_attributes)
			.and_then(make_surface)
			.and_then(run_example)
			.and_then(quit_sdl)
			.or_else(show_error)
			.value_or(1);
}
