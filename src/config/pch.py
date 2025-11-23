PCH_SPECIAL_OPT =  f"""
// 编译器特定优化
#if defined(__GNUC__) || defined(__clang__)
    #define FORCE_INLINE inline __attribute__((always_inline))
    #define LIKELY(x)   __builtin_expect(!!(x), 1)
    #define UNLIKELY(x) __builtin_expect(!!(x), 0)
#elif defined(_MSC_VER)
    #define FORCE_INLINE __forceinline
    #define LIKELY(x)   (x)
    #define UNLIKELY(x) (x)
#else
    #define FORCE_INLINE inline
    #define LIKELY(x)   (x)
    #define UNLIKELY(x) (x)
#endif

// 常用类型别名
using std::string;
using std::vector;
using std::unique_ptr;
using std::shared_ptr;
using std::make_unique;
using std::make_shared;

// 常用常量
constexpr size_t KB = 1024;
constexpr size_t MB = 1024 * KB;
constexpr size_t GB = 1024 * MB;
"""
