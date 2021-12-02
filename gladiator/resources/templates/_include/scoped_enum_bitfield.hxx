template<typename Enum>
struct _bitmask_ops {
	static const bool enable = false;
};

template<typename Enum>
constexpr typename std::enable_if<_bitmask_ops<Enum>::enable, Enum>::type operator &(Enum lhs, Enum rhs) {
	using underlying = typename std::underlying_type<Enum>::type;
	return static_cast<Enum> (
			static_cast<underlying>(lhs) &
			static_cast<underlying>(rhs)
	);
}

template<typename Enum>
constexpr typename std::enable_if<_bitmask_ops<Enum>::enable, Enum>::type operator ^(Enum lhs, Enum rhs) {
	using underlying = typename std::underlying_type<Enum>::type;
	return static_cast<Enum> (
			static_cast<underlying>(lhs) ^
			static_cast<underlying>(rhs)
	);
}

template<typename Enum>
constexpr typename std::enable_if<_bitmask_ops<Enum>::enable, Enum>::type operator ~(Enum rhs) {
	using underlying = typename std::underlying_type<Enum>::type;
	return static_cast<Enum> (
			~static_cast<underlying>(rhs)
	);
}

template<typename Enum>
constexpr typename std::enable_if<_bitmask_ops<Enum>::enable, Enum>::type operator |(Enum lhs, Enum rhs) {
	using underlying = typename std::underlying_type<Enum>::type;
	return static_cast<Enum> (
			static_cast<underlying>(lhs) |
			static_cast<underlying>(rhs)
	);
}

template<typename Enum>
constexpr typename std::enable_if<_bitmask_ops<Enum>::enable, Enum>::type& operator &=(Enum& lhs, Enum rhs) {
	using underlying = typename std::underlying_type<Enum>::type;
	lhs = static_cast<Enum> (
			static_cast<underlying>(lhs) &
			static_cast<underlying>(rhs)
	);
	return lhs;
}

template<typename Enum>
constexpr typename std::enable_if<_bitmask_ops<Enum>::enable, Enum>::type& operator ^=(Enum& lhs, Enum rhs) {
	using underlying = typename std::underlying_type<Enum>::type;
	lhs = static_cast<Enum> (
			static_cast<underlying>(lhs) ^
			static_cast<underlying>(rhs)
	);
	return lhs;
}

template<typename Enum>
constexpr typename std::enable_if<_bitmask_ops<Enum>::enable, Enum&>::type operator |=(Enum& lhs, Enum rhs) {
	using underlying = typename std::underlying_type<Enum>::type;
	lhs = static_cast<Enum> (
			static_cast<underlying>(lhs) |
			static_cast<underlying>(rhs)
	);
	return lhs;
}
