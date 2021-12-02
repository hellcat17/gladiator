#include <type_traits>
#include <memory>
#include <utility>

namespace {{ constants.detail_namespace }} {

template<class To, class From>
constexpr auto sized_ptr_cast(From ptr)
		-> typename std::enable_if<sizeof(typename std::pointer_traits<To>::element_type)
				== sizeof(typename std::pointer_traits<From>::element_type), To>::type
{
	return reinterpret_cast<To>(ptr);
}

template <class Enum>
constexpr auto to_underlying(Enum value) noexcept
		-> typename std::underlying_type<Enum>::type
{
	return static_cast<typename std::underlying_type<Enum>::type>(value);
}

}
