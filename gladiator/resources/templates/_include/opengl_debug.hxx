#ifndef _NDEBUG

#include <cstdint>
#include <cstdlib>
#include <type_traits>
#include <iostream>
#include <string>

namespace {{ constants.detail_namespace }} {

constexpr std::uint32_t GL_CONTEXT_FLAGS = 0x821E;
constexpr std::uint32_t GL_CONTEXT_FLAG_DEBUG_BIT = 0x00000002;
constexpr std::uint32_t GL_DEBUG_OUTPUT = 0x92E0;
constexpr std::uint32_t GL_DEBUG_OUTPUT_SYNCHRONOUS = 0x8242;
constexpr std::uint32_t GL_DONT_CARE = 0x1100;
constexpr std::uint32_t GL_DEBUG_TYPE_ERROR = 0x824C;
constexpr std::uint32_t GL_DEBUG_SEVERITY_LOW = 0x9146;
constexpr std::uint32_t GL_DEBUG_SEVERITY_MEDIUM = 0x9147;
constexpr std::uint32_t GL_DEBUG_SEVERITY_HIGH = 0x9148;
constexpr std::uint32_t GL_TRUE = 1;

void _debug_output(std::uint32_t,
		std::uint32_t type,
		std::uint32_t,
		std::uint32_t severity,
		std::int32_t,
		const char* msg,
		const void*)
{
	if (severity == GL_DEBUG_SEVERITY_LOW || severity == GL_DEBUG_SEVERITY_MEDIUM || severity == GL_DEBUG_SEVERITY_HIGH) {
		std::cout << msg << std::endl;
		if (type == GL_DEBUG_TYPE_ERROR) {
			std::cout << "programming error found, aborting" << std::endl;
			std::abort();
		}
	}
}

using _proc_address_func = std::add_pointer<void*(const char*)>::type;
using _get_integer_v_proc = std::add_pointer<void(std::uint32_t, std::int32_t*)>::type;
using _enable_proc = std::add_pointer<void(std::uint32_t)>::type;
using _debug_callback_type = std::add_pointer<decltype(_debug_output)>::type;
using _debug_msg_callback_proc = std::add_pointer<void(_debug_callback_type, const void*)>::type;
using _debug_msg_control_proc = std::add_pointer<void(std::uint32_t, std::uint32_t, std::uint32_t, std::int32_t, const std::uint32_t*, std::uint32_t)>::type;

void* _core_or_ext(const char* name, _proc_address_func load) {
	auto func = load(name);
	if (func != nullptr) {
		return func;
	}

	const auto arb = std::string{name} + "ARB";
	func = load(arb.data());
	if (func != nullptr) {
		return func;
	}

	const auto khr = std::string{name} + "KHR";
  return load(khr.data());
}

void setup_debug_output(_proc_address_func load) {
	const auto glGetIntegerv = (_get_integer_v_proc) load("glGetIntegerv");
	const auto glEnable = (_enable_proc) load("glEnable");
	const auto glDebugMessageCallback = (_debug_msg_callback_proc) _core_or_ext("glDebugMessageCallback", load);
	const auto glDebugMessageControl = (_debug_msg_control_proc) _core_or_ext("glDebugMessageControl", load);

	if (glDebugMessageCallback == nullptr || glDebugMessageControl == nullptr) {
		return;
	}

	std::int32_t flags;
	glGetIntegerv(GL_CONTEXT_FLAGS, &flags);
	if (flags & GL_CONTEXT_FLAG_DEBUG_BIT) {
		glEnable(GL_DEBUG_OUTPUT);
		glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS);
		glDebugMessageCallback(_debug_output, nullptr);
		glDebugMessageControl(GL_DONT_CARE, GL_DONT_CARE, GL_DONT_CARE, 0, nullptr, GL_TRUE);
	}
}

}

#endif
