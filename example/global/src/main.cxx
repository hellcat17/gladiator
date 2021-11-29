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

auto run_example(SDL_Window* window) -> tl::expected<int, std::string> {
	if (!gl::load_functions(SDL_GL_GetProcAddress)) {
		return tl::make_unexpected("failed to load OpenGL functions");
	}

	gl::viewport(0, 0, window_width, window_height);

	while (true) {
		SDL_Event event;
		while (SDL_PollEvent(&event) != 0) {
			if (event.type == SDL_QUIT) {
				return 0;
			}
		}

		gl::clear_color(clear_r, clear_g, clear_b, 1);
		gl::clear(gl::clear_buffer_mask::color_buffer_bit | gl::clear_buffer_mask::depth_buffer_bit);

		SDL_GL_SwapWindow(window);
	}
}

constexpr std::array<std::pair<SDL_GLattr, int>, 10> window_settings = {{
		{SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE},
		{SDL_GL_CONTEXT_MAJOR_VERSION, 3},
		{SDL_GL_CONTEXT_MINOR_VERSION, 3},
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
