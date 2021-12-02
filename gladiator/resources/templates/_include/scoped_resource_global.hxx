#include <cstdint>
#include <vector>

namespace {{ options.resource_wrapper_namespace or constants.default_resource_wrapper_namespace }} {

template<typename... AdditionalParams>
struct resource {
	using count_type = std::int32_t;
	using object_names_type = std::uint32_t;
	using create_func_type = typename std::add_pointer<void(AdditionalParams..., count_type, object_names_type*)>::type;
	using delete_func_type = typename std::add_pointer<void(count_type, const object_names_type*)>::type;
	using single_create_func_type = typename std::add_pointer<object_names_type(AdditionalParams...)>::type;
	using single_delete_func_type = typename std::add_pointer<void(object_names_type)>::type;

	// single element variant of array_wrapper
	template<create_func_type CreateObject, delete_func_type DeleteObject>
	struct wrapper {
		object_names_type name;

		explicit wrapper(AdditionalParams... params) { CreateObject(params..., 1, &name); }
		~wrapper() { if (name > 0) { DeleteObject(1, &name); } }
		wrapper(const wrapper& other) = delete;
		wrapper& operator=(const wrapper& other) = delete;
		wrapper(wrapper&& other) : name(other.name) { other.name = 0; }
		wrapper& operator=(wrapper&& other) { name = other.name; other.name = 0; return *this; }
		operator object_names_type() const { return name; }
	};

	template<create_func_type CreateObjects, delete_func_type DeleteObjects>
	struct array_wrapper {
		using container_type = std::vector<object_names_type>;
		using const_iterator_type = typename container_type::const_iterator;

		container_type names;

		explicit array_wrapper(AdditionalParams... params, count_type count) { names.resize(count); CreateObjects(params..., count, names.data()); }
		~array_wrapper() { if (names.size() > 0) { DeleteObjects(names.size(), names.data()); } }
		array_wrapper(const array_wrapper& other) = delete;
		array_wrapper& operator=(const array_wrapper& other) = delete;
		array_wrapper(array_wrapper&& other) : names(std::move(other.names)) { other.names.clear(); }
		array_wrapper& operator=(array_wrapper&& other) { names = std::move(other.names); other.names.clear(); return *this; }

		const_iterator_type begin() const { return names.begin(); }
		const_iterator_type end() const { return names.end(); }
	};

	template<single_create_func_type CreateObject, single_delete_func_type DeleteObject>
	struct single_wrapper {
		object_names_type name;

		explicit single_wrapper(AdditionalParams... params) { name = CreateObject(params...); }
		~single_wrapper() { if (name > 0) { DeleteObject(name); } }
		single_wrapper(const single_wrapper& other) = delete;
		single_wrapper& operator=(const single_wrapper& other) = delete;
		single_wrapper(single_wrapper&& other) : name(other.name) { other.name = 0; }
		single_wrapper& operator=(single_wrapper&& other) { name = other.name; other.name = 0; return *this; }
		operator object_names_type() const { return name; }
	};
};

}
